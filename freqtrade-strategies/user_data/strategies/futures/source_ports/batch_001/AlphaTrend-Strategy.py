"""Port of sources/SM_f4d6c1940de7cb3d.pine (batch_001/AlphaTrend-Strategy.md).

KivancOzbilgic's AlphaTrend strategy version. The indicator is a one-dimensional
trailing band built from a two-state recursion, and the strategy trades the
cross of that band against itself two bars back:

    ATR        = ta.sma(ta.tr, AP)
    upT        = low  - ATR * coeff
    downT      = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    buySignalk  = ta.crossover(AlphaTrend, AlphaTrend[2])
    sellSignalk = ta.crossunder(AlphaTrend, AlphaTrend[2])
    if buySignalk  -> strategy.entry("Long",  strategy.long)
    if sellSignalk -> strategy.entry("Short", strategy.short)

`AlphaTrend` is Pine's `x = 0.0` followed by `x :=` on the same line, i.e. a
self-referencing series whose initial value is 0.0, so on the first bar
`nz(AlphaTrend[1])` is 0. `nz` is applied to the history reference itself, so a
bar whose input is na takes the previous value rather than na. The recursion is
reproduced with an explicit loop rather than a vectorised rolling operation
because the state (not a window) is what carries across bars.

`strategy()` declares only title / shorttitle / overlay / format / precision /
margin_long / margin_short, so every order property is Pine's default: fixed
quantity of 1 contract, 0% commission, pyramiding 0, initial capital 1000000.
`margin_long=100` / `margin_short=100` is 100% margin, i.e. no leverage, which
is what the engine's unlevered cash model assumes. There is no exit call at
all: a position goes flat only when the opposite entry reverses it, so
`source_reproduce_stops` is False and a position open at the end of the window
stays open.

FIDELITY:

* `ta.mfi` is not part of `pine_ta`, so it is implemented here from
  TradingView's definition; see `_pine_mfi` for the formula and the two places
  its edge behaviour is a modelling choice rather than a documented rule.
* `ta.tr` is called WITHOUT the `handle_na` argument, so Pine returns na on the
  first bar while `pine_ta.pine_tr` returns `high - low` there
  (PINE_SEMANTICS.md 3.7). That one bar early seeding shifts the whole
  `ta.rma`-free `ta.sma(ta.tr, AP)` warmup by one bar. Public-layer boundary,
  recorded and not modified.
* The source writes four `ta.barssince` counters (`K1`, `K2`, `O1`, `O2`) and
  uses them ONLY inside the two `plotshape` visibility conditions
  (`buySignalk and showsignalsk and O1 > K2`). They gate the painted BUY/SELL
  labels, not the orders: `longCondition = buySignalk` and
  `shortCondition = sellSignalk` are the bare crosses. The display gating is
  therefore not reproduced, and `showsignalsk` has no trading effect.
* The md's argument table renders the `Multiplier` default as `true`
  (`v_input_float_1|true|Multiplier`), which is the FMZ exporter's
  rendering of the float `1`; the source reads `input.float(1, ...)`, so the
  port uses 1.0. Recorded, source wins.
* `src = input(close)` is consumed only on the `novolumedata` branch
  (`ta.rsi(src, AP)`); the default branch reads `hlc3` literally and does not
  go through `src`.
* `format` / `precision` / `shorttitle` / the three `plot`/`fill` calls are
  display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding -- the chain verifier measures that
  separately instead of treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(series, length)`.

    TradingView defines the Money Flow Index as

        MFI          = 100 - 100 / (1 + upper / lower)
        upper        = sum over the window of series * volume where series rose
        lower        = sum over the window of series * volume where series fell

    which is the same shape as the published Pine reference

        upper = math.sum(series > series[1] ? series * volume : 0, length)
        lower = math.sum(series < series[1] ? series * volume : 0, length)

    Two edge behaviours are NOT published by TradingView and are modelling
    choices here:

    * a bar whose `series - series[1]` is na (the first bar, or the first bar
      after a gap) contributes 0 to both sums, because Pine treats an na
      condition in a ternary as false;
    * a window with no falling bar makes the ratio undefined. Pine's own
      `ta.rsi` is documented to return 100 for the mirror-image case (no
      losses), and `pine_ta.pine_rsi` encodes exactly that, so the same
      convention is applied here rather than inventing a third one. A window
      that is entirely flat therefore also reads 100.
    * `math.sum` returns na until `length` bars are available, hence
      `min_periods=length`.
    """
    source = pd.Series(source).astype(float)
    volume = pd.Series(volume).astype(float)
    rising = source.diff() > 0
    falling = source.diff() < 0
    money = source * volume
    upper = money.where(rising, 0.0).rolling(length, min_periods=length).sum()
    lower = money.where(falling, 0.0).rolling(length, min_periods=length).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = upper / lower
        out = 100.0 - 100.0 / (1.0 + ratio)
    out = out.where(lower != 0.0, 100.0)
    return out.where(upper.notna() & lower.notna())


class SMAlphaTrend_f4d6c1(PinePortBase, IStrategy):
    source_id = "SM_f4d6c1940de7cb3d"
    source_file = "AlphaTrend-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 14,
        "src": "close",
        "showsignalsk": False,
        "novolumedata": False,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.mfi is not in pine_ta; implemented here from TradingView's MFI "
        "definition (sum of series*volume over rising bars vs falling bars). "
        "Two edge cases are modelling choices, not published rules: an na "
        "change contributes 0 to both sums, and an undefined ratio (no falling "
        "bar in the window) is mapped to 100, following the convention "
        "pine_ta.pine_rsi already encodes for its documented no-loss case.",
        "ta.tr is called without handle_na in the source, so Pine returns na on "
        "bar 0 while pine_ta.pine_tr returns high-low there "
        "(PINE_SEMANTICS.md 3.7). That shifts the warmup of ta.sma(ta.tr, AP) "
        "by one bar. Public-layer boundary, recorded not modified.",
        "AlphaTrend is a self-referencing series initialised to 0.0 "
        "(`AlphaTrend = 0.0` then `:=` on the same line), so nz(AlphaTrend[1]) "
        "is 0 on the first bar; reproduced with an explicit recursion loop.",
        "The four ta.barssince counters (K1/K2/O1/O2) feed only the plotshape "
        "visibility conditions (buySignalk and showsignalsk and O1 > K2). They "
        "gate the painted labels, not the orders -- the source's "
        "longCondition/shortCondition are the bare crosses -- so the display "
        "gating is not reproduced and showsignalsk has no trading effect.",
        "The md's argument table shows the Multiplier default as `true` "
        "(v_input_float_1|true|Multiplier), which is the exporter's rendering "
        "of the float 1; the source reads input.float(1, ...) and the port uses "
        "1.0. Recorded; source wins.",
        "src = input(close) is consumed only on the novolumedata branch "
        "(ta.rsi(src, AP)); the default branch reads hlc3 literally.",
        "strategy() declares only display properties, so qty_type=fixed, "
        "qty_value=1, commission=0%, pyramiding=0 and initial_capital=1000000 "
        "are Pine's documented defaults.",
        "margin_long=100/margin_short=100 is 100% margin, i.e. no leverage, "
        "which matches the engine's unlevered cash model.",
        "There is no exit call: a position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False and a position "
        "open at the end of the window stays open.",
        "format/precision/shorttitle and the plot/fill calls are display-only "
        "and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        coeff = float(params["coeff"])
        ap = int(params["AP"])
        atr = ta.pine_sma(ta.pine_tr(dataframe), ap)
        up_t = dataframe["low"] - atr * coeff
        down_t = dataframe["high"] + atr * coeff

        # `novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50`
        if bool(params["novolumedata"]):
            source = ta.pine_source(dataframe, str(params["src"]))
            gate = (ta.pine_rsi(source, ap) >= 50.0).fillna(False).to_numpy()
        else:
            hlc3 = ta.pine_source(dataframe, "hlc3")
            gate = (
                _pine_mfi(hlc3, dataframe["volume"], ap) >= 50.0
            ).fillna(False).to_numpy()

        up_values = up_t.to_numpy(dtype=float)
        down_values = down_t.to_numpy(dtype=float)
        alpha = np.full(len(dataframe), np.nan)
        previous = 0.0  # nz(AlphaTrend[1]) on the first bar
        for i in range(len(dataframe)):
            if gate[i]:
                value = previous if up_values[i] < previous else up_values[i]
            else:
                value = previous if down_values[i] > previous else down_values[i]
            alpha[i] = value
            # nz(): an na bar carries the state forward as 0.
            previous = 0.0 if np.isnan(value) else value

        alpha_series = pd.Series(alpha, index=dataframe.index, dtype=float)
        alpha_two_back = alpha_series.shift(2)
        dataframe["pine_alpha_trend"] = alpha_series
        dataframe["pine_buy_signal"] = ta.pine_crossover(alpha_series, alpha_two_back)
        dataframe["pine_sell_signal"] = ta.pine_crossunder(alpha_series, alpha_two_back)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "alpha_trend": dataframe["pine_alpha_trend"].to_numpy(),
            "buy_signal": dataframe["pine_buy_signal"].to_numpy(),
            "sell_signal": dataframe["pine_sell_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignalk)
        #     strategy.entry("Long", strategy.long)
        if ctx["buy_signal"][i]:
            broker.entry("Long", "long")
        # if (sellSignalk)
        #     strategy.entry("Short", strategy.short)
        if ctx["sell_signal"][i]:
            broker.entry("Short", "short")
