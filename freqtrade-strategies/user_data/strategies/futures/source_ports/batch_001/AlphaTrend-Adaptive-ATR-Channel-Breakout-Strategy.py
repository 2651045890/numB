"""Port of sources/SM_692887aed8df2d28.pine
(batch_001/AlphaTrend-Adaptive-ATR-Channel-Breakout-Strategy.md).

Pine v5, AlphaTrend by KivancOzbilgic. An adaptive ATR channel whose two edges
are evaluated recursively against their own previous value:

    coeff = input.float(1, 'Multiplier')
    AP    = input(14, 'Common Period')
    ATR   = ta.sma(ta.tr, AP)
    upT   = low  - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend = 0.0
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    buySignalk  = ta.crossover(AlphaTrend, AlphaTrend[2])
    sellSignalk = ta.crossunder(AlphaTrend, AlphaTrend[2])

    if buySignalk  -> strategy.entry("Long",  strategy.long)
    if sellSignalk -> strategy.entry("Short", strategy.short)

`src` is `input(close)` but is only read by the `novolumedata` branch (the
default branch uses the literal `hlc3`); both are kept.

There is no exit call, so a position is only closed by the opposite entry
reversing it: `source_reproduce_stops` is False.

`strategy("AlphaTrend Strategy", shorttitle='ATst', overlay=true,
format=format.price, precision=2, margin_long=100, margin_short=100)` sets no
sizing, capital or commission property, so Pine's documented defaults apply:
`fixed` / 1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close false`. `margin_long` / `margin_short` are 100 (no
leverage); margin is not modelled by the engine at all.

The `/*backtest` header declares `period: 1h` on Binance BTC_USDT, so
`timeframe` is "1h".

FIDELITY:

* `AlphaTrend` is recursive through `nz(AlphaTrend[1])`, which replaces the
  previous bar's na with 0.0 -- 0.0 both on the very first bar and for the
  whole warm-up, where `ta.sma(ta.tr, AP)` is still na and therefore makes
  `upT` / `downT` na too. Reproduced by an explicit per-bar loop; an na
  comparison is false in both Pine and numpy, so the value stays na until ATR
  exists, and the branch taken on the first ATR bar is the same one Pine
  takes.
* `ta.tr` follows Pine's v5 default `handle_na = false`, whose first bar is
  na; `pine_ta.pine_tr` returns `high - low` there instead. This is the shared
  layer's known one-bar seeding offset for `ta.sma(ta.tr, n)` (PINE_SEMANTICS
  section 3.7) -- it moves the whole ATR series' seed one bar earlier. It is
  recorded, not worked around: rule 9 forbids touching `pine_ta`, and the
  section explicitly leaves the boundary unfixed. ATR has converged long
  before any signal fires.
* `ta.mfi(hlc3, AP)` is implemented locally (pine_ta has no `mfi`), from the
  documented equivalent:

      upper = math.sum(volume * (ta.change(source) <= 0 ? 0 : source), length)
      lower = math.sum(volume * (ta.change(source) >= 0 ? 0 : source), length)
      mfi   = upper + lower == 0 ? 50 : 100 - 100 / (1 + upper / lower)

  On the first bar `ta.change` is na; a na condition takes the false branch in
  Pine's ternary, so that bar's turnover enters both sums. Reproduced exactly.
* Only the DEFAULT branch of `novolumedata` (false) is exercised by the
  defaults; the `ta.rsi(src, AP) >= 50` alternative is kept selectable.
* `src`, `showsignalsk`, and the `K1/K2/O1/O2 = ta.barssince(...)` series feed
  only `plot` / `fill` / `plotshape` -- display output. `showsignalsk` gates
  the two `plotshape` labels and nothing else, so it changes no order and is
  reproduced only as a declared input.
* Leverage, margin, liquidation and funding are not modelled, and the venue's
  contract-step rounding is not modelled either.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(source, length)`, from the documented equivalent code.

    A bar whose `ta.change(source)` is na (the first bar) fails both
    comparisons, so Pine's ternary takes its false branch and the bar's
    turnover is counted on BOTH sides -- matched here by numpy's False for a
    NaN comparison.
    """
    change = source.diff()
    values = source.to_numpy(dtype=float)
    volume = volume.to_numpy(dtype=float)
    upper_term = np.where((change <= 0).to_numpy(), 0.0, values) * volume
    lower_term = np.where((change >= 0).to_numpy(), 0.0, values) * volume
    upper = pd.Series(upper_term, index=source.index).rolling(length, min_periods=length).sum()
    lower = pd.Series(lower_term, index=source.index).rolling(length, min_periods=length).sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = upper / lower
        value = 100.0 - 100.0 / (1.0 + ratio)
    return value.where(upper + lower != 0.0, 50.0)


def _pine_alpha_trend(cond: np.ndarray, up: np.ndarray, down: np.ndarray) -> np.ndarray:
    """The `AlphaTrend` recursion, one bar at a time.

    `nz(AlphaTrend[1])` collapses the previous value's na to 0.0; a comparison
    against na is false, so whichever edge is chosen comes back na while ATR
    is still na.
    """
    out = np.full(len(cond), np.nan)
    previous = np.nan
    for i in range(len(cond)):
        base = 0.0 if np.isnan(previous) else float(previous)
        if bool(cond[i]):
            value = base if up[i] < base else up[i]
        else:
            value = base if down[i] > base else down[i]
        out[i] = value
        previous = value
    return out


class SMAlphaTrendAdaptiveAtrChannelBreakout_692887(PinePortBase, IStrategy):
    source_id = "SM_692887aed8df2d28"
    source_file = "AlphaTrend-Adaptive-ATR-Channel-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 14,
        "src": "close",
        "showsignalsk": False,
        "novolumedata": False,
    }
    # strategy(title, shorttitle, overlay, format, precision, margin_long,
    # margin_short) -- no sizing/capital/commission property, so Pine defaults.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`AlphaTrend` is recursive via `nz(AlphaTrend[1])`; reproduced with an "
        "explicit per-bar loop, including 0.0 as the seed on the first bar and "
        "through the warm-up where ATR is still na.",
        "PINE_SEMANTICS section 3.7: `ta.tr` (v5, handle_na=false) is na on "
        "the first bar while `pine_ta.pine_tr` returns `high - low` there, so "
        "`ta.sma(ta.tr, AP)` is seeded one bar earlier than in Pine. Recorded, "
        "not worked around (rule 9 forbids changing pine_ta).",
        "`ta.mfi` is implemented locally from the documented equivalent code; "
        "the first bar's `ta.change` is na and therefore enters both money-flow "
        "sums, as Pine's ternary does.",
        "`novolumedata` selects `ta.rsi(src, AP) >= 50` instead of MFI; only "
        "the default (false, MFI on hlc3) is exercised by the defaults.",
        "`showsignalsk` and the `ta.barssince` series only drive plot/fill/"
        "plotshape output and change no order.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False.",
        "`strategy()` sets no sizing/capital/commission, so Pine's defaults "
        "apply: fixed / 1 contract, 1000000 initial capital, 0% commission, "
        "pyramiding 0. `margin_long`/`margin_short` are 100; margin is not "
        "modelled.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["AP"])
        coeff = float(params["coeff"])

        atr = ta.pine_sma(ta.pine_tr(dataframe), length)
        up_t = dataframe["low"] - atr * coeff
        down_t = dataframe["high"] + atr * coeff

        if bool(params["novolumedata"]):
            source = ta.pine_source(dataframe, str(params["src"]))
            trend_cond = (ta.pine_rsi(source, length) >= 50.0).to_numpy()
        else:
            hlc3 = ta.pine_source(dataframe, "hlc3")
            trend_cond = (_pine_mfi(hlc3, dataframe["volume"], length) >= 50.0).to_numpy()

        alpha_trend = _pine_alpha_trend(
            trend_cond, up_t.to_numpy(dtype=float), down_t.to_numpy(dtype=float)
        )
        trend = pd.Series(alpha_trend, index=dataframe.index, dtype=float)

        dataframe["pine_alpha_trend"] = trend
        dataframe["pine_long_condition"] = ta.pine_crossover(trend, trend.shift(2))
        dataframe["pine_short_condition"] = ta.pine_crossunder(trend, trend.shift(2))
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # longCondition = buySignalk
        # if (longCondition)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # shortCondition = sellSignalk
        # if (shortCondition)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
