"""Port of sources/SM_358d77df4331041c.pine (batch_001/AlphaTrend与KAMA结合的自适应趋势跟踪与风险管理策略Adaptive-Trend-Following-Strategy-Combining-AlphaTrend-and-KAMA-with-Risk-Management.md).

Pine v5. KivancOzbilgic's AlphaTrend band crossed by a Kaufman Adaptive MA,
with a hand-rolled position state and a 50% partial exit at a fixed profit
target:

    ATR  = ta.sma(ta.tr, AP)                     // AP = 14, plain SMA, not ta.atr
    upT  = low  - ATR * coeff
    downT = high + ATR * coeff
    AlphaTrend := (novolumedata ? ta.rsi(src, AP) >= 50 : ta.mfi(hlc3, AP) >= 50)
                  ? (upT   < nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : upT)
                  : (downT > nz(AlphaTrend[1]) ? nz(AlphaTrend[1]) : downT)

    xvnoise  = abs(xPrice - xPrice[1])
    nsignal  = abs(xPrice - xPrice[kamaLength])
    nnoise   = sum of xvnoise over the last kamaLength bars      // an explicit for loop
    nefratio = nnoise != 0 ? nsignal / nnoise : 0
    nsmooth  = pow(nefratio * (0.666 - 0.0645) + 0.0645, 2)
    nAMA := nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))

    buyCondition  = (crossover(nAMA, AlphaTrend)   and crossover(nAMA, AlphaTrend[2]))
                 or (crossover(nAMA, AlphaTrend)   and nAMA > AlphaTrend[2])
                 or (crossover(nAMA, AlphaTrend[2]) and nAMA > AlphaTrend)
    sellCondition = the same three disjuncts with crossunder / `<`

The order stream is a small state machine held in `var` scalars
(`entryPrice`, `currentPosition`, `partialExitPrice`), reproduced here as a
pre-computed per-bar pass because none of it depends on fills -- only on the
signals and on the bar's own high/low:

    if buySignal and currentPosition != "long"
        if currentPosition == "short" -> strategy.close("Short")
        strategy.entry("Long", strategy.long)
        entryPrice := close ; currentPosition := "long"
        partialExitPrice := entryPrice * (1 + profitTarget / 100)
    if sellSignal and currentPosition != "short"
        if currentPosition == "long" -> strategy.close("Long")
        strategy.entry("Short", strategy.short)
        entryPrice := close ; currentPosition := "short"
        partialExitPrice := entryPrice * (1 - profitTarget / 100)
    if currentPosition == "long"  and high >= partialExitPrice
        strategy.close("Long",  qty_percent=50) ; partialExitPrice := na
    if currentPosition == "short" and low  <= partialExitPrice
        strategy.close("Short", qty_percent=50) ; partialExitPrice := na

`strategy()` declares `initial_capital=100000`, `default_qty_type =
strategy.percent_of_equity` and `default_qty_value = 100`, so every entry
commits the whole equity. `alphaTrend`, `nAMA` and the two conditions are
vectorised, but the two recursive series (the band and the KAMA) are stepped
bar by bar because their state, not a window, carries across bars.

FIDELITY:

* `strategy.close(id, qty_percent=50)` CANNOT BE EXPRESSED. The engine's
  `broker.close` (and `PineBroker._close_entries`) closes the WHOLE entry; there
  is no `qty_percent` parameter anywhere on the broker surface, and the shared
  layer must not be modified (PORT_BRIEF rule 9). The port therefore emits
  `broker.close("Long")` / `broker.close("Short")` for those two calls, which
  closes 100% where the source closes 50%. This is a real behavioural
  difference, not a rounding artefact: after a +10% move the source keeps half
  the position on, and the engine goes flat. See `blockers`.
* `ta.mfi` is not in `pine_ta`, so it is implemented here from TradingView's
  definition; see `_pine_mfi` for the formula and the three places its edge
  behaviour is a modelling choice rather than a published rule.
* `ta.tr` is called WITHOUT `handle_na`, so Pine returns na on the first bar
  while `pine_ta.pine_tr` returns `high - low` (PINE_SEMANTICS.md 3.7). That
  one bar early seeding shifts the `ta.sma(ta.tr, AP)` warm-up by one bar.
  Public-layer boundary, recorded and not modified.
* `novolumedata` is False by default, so the band reads `ta.mfi(hlc3, AP)` and
  the `ta.rsi(src, AP)` branch is dead. Both are implemented so that
  `source_parameters` can flip the switch without a code change.
* The `for i = 0 to kamaLength-1: nnoise := nnoise + xvnoise[i]` loop is a
  plain rolling sum, but it propagates na (`na + x` is na), so `nnoise` is na
  until `kamaLength` bars have elapsed -- `pine_sum`'s `min_periods` model.
* `nefratio = nnoise != 0 ? nsignal / nnoise : 0` is ambiguous for an na
  `nnoise`: Pine v5 does not publish whether `na != 0` is true or false, and
  the two readings give DIFFERENT `nefratio` (na vs 0) on the warm-up bars.
  The port takes the na-propagating reading. The difference is immaterial for
  the final series: the first bar on which `nsmooth` is defined is preceded by
  a bar where `nsignal` is still na, so `nsmooth` is na there, `nAMA` becomes
  na, and the next bar's `nz(nAMA[1])` resets the recursion to 0 either way.
  Recorded rather than silent.
* `showsignals` only gates the three `plotshape` calls, and `plotshape` /
  `plot` / `fill` / `alertcondition` place no condition -- none is reproduced.
* The reversal path closes the opposite entry id and opens the new one on the
  same bar; both calls are replayed in source order.
* The source's PositionState is a `var string` compared against "long" /
  "short" / "flat", and it is updated when the SIGNAL fires, not when the fill
  happens. It is reproduced as a pre-computed per-bar pass for that reason.
* No `request.security`, no `varip`, no barstate branch, no stop / limit /
  trail exit and no `strategy.risk.*` in the source, so
  `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; with `percent_of_equity` at 100 the framework's wallet and
  the engine's cash can drift (PINE_SEMANTICS.md 1.4/1.6), and the chain
  verifier measures that separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_mfi(source: pd.Series, volume: pd.Series, length: int) -> pd.Series:
    """Pine `ta.mfi(series, length)`.

        MFI = 100 - 100 / (1 + upper / lower)
        upper = sum over the window of series * volume on bars where series ROSE
        lower = sum over the window of series * volume on bars where series FELL

    which is the shape of TradingView's published reference

        upper = math.sum(series > series[1] ? series * volume : 0, length)
        lower = math.sum(series < series[1] ? series * volume : 0, length)

    Three edge behaviours are NOT published and are modelling choices here:

    * a bar whose `series - series[1]` is na (the first bar) contributes 0 to
      both sums, because Pine treats an na condition in a ternary as false;
    * a window with no falling bar leaves the ratio undefined. Pine's own
      `ta.rsi` is documented to return 100 for the mirror-image case (no
      losses) and `pine_ta.pine_rsi` encodes exactly that, so the same
      convention is applied here rather than inventing a third one -- an
      entirely flat window therefore also reads 100;
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


def _alpha_trend(up_t: np.ndarray, down_t: np.ndarray, up_leg: np.ndarray) -> np.ndarray:
    """`AlphaTrend := cond ? (upT < nz(prev) ? nz(prev) : upT) : (downT > nz(prev) ? nz(prev) : downT)`.

    `nz(prev)` turns the previous bar's na into 0, so the recursion restarts
    from 0 whenever the previous bar was undefined (which is what happens
    while the ATR warm-up is incomplete).
    """
    out = np.empty(len(up_t), dtype=float)
    prev = 0.0
    for i in range(len(up_t)):
        if up_leg[i]:
            value = prev if up_t[i] < prev else up_t[i]
        else:
            value = prev if down_t[i] > prev else down_t[i]
        out[i] = value
        prev = 0.0 if not np.isfinite(value) else float(value)
    return out


def _kama(close: np.ndarray, length: int) -> np.ndarray:
    """The source's hand-written Kaufman Adaptive Moving Average.

    `nsmooth` is the squared efficiency ratio scaled between the two published
    constants (0.666 fast, 0.0645 slow); `nAMA` is an exponential recursion
    whose previous value goes through `nz`, so an undefined bar restarts it.
    """
    x_price = np.asarray(close, dtype=float)
    if len(x_price) <= length:
        return np.full(len(x_price), np.nan)
    previous = np.empty_like(x_price)
    previous[0] = np.nan
    previous[1:] = x_price[:-1]
    xv_noise = np.abs(x_price - previous)
    nsignal = np.abs(x_price - np.concatenate([np.full(length, np.nan), x_price[:-length]]))
    nnoise = pd.Series(xv_noise).rolling(length, min_periods=length).sum().to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = nsignal / nnoise
    # `nnoise != 0` is true for an na nnoise, which is the na-propagating
    # reading of Pine's ternary; see the module docstring.
    efratio = np.where(nnoise != 0, ratio, 0.0)
    smooth = np.power(efratio * (0.666 - 0.0645) + 0.0645, 2)

    out = np.empty_like(x_price)
    prev = 0.0
    for i in range(len(x_price)):
        value = prev + smooth[i] * (x_price[i] - prev)
        out[i] = value
        prev = 0.0 if not np.isfinite(value) else float(value)
    return out


def _position_state_machine(
    close: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    buy: np.ndarray,
    sell: np.ndarray,
    profit_target: float,
) -> dict:
    """The source's `var` state, replayed bar by bar.

    Runs in the source's own order: the entry blocks first (which is what sets
    `partialExitPrice`), then the two partial-exit tests, which may fire on the
    very bar the entry was declared on.
    """
    count = len(close)
    enter_long = np.zeros(count, dtype=bool)
    enter_short = np.zeros(count, dtype=bool)
    close_short_first = np.zeros(count, dtype=bool)
    close_long_first = np.zeros(count, dtype=bool)
    partial_long = np.zeros(count, dtype=bool)
    partial_short = np.zeros(count, dtype=bool)

    state = "flat"
    partial_price = np.nan
    for i in range(count):
        if buy[i] and state != "long":
            if state == "short":
                close_short_first[i] = True
            enter_long[i] = True
            state = "long"
            partial_price = float(close[i]) * (1.0 + profit_target / 100.0)
        if sell[i] and state != "short":
            if state == "long":
                close_long_first[i] = True
            enter_short[i] = True
            state = "short"
            partial_price = float(close[i]) * (1.0 - profit_target / 100.0)
        if state == "long" and np.isfinite(partial_price) and high[i] >= partial_price:
            partial_long[i] = True
            partial_price = np.nan
        if state == "short" and np.isfinite(partial_price) and low[i] <= partial_price:
            partial_short[i] = True
            partial_price = np.nan

    return {
        "enter_long": enter_long,
        "enter_short": enter_short,
        "close_short_first": close_short_first,
        "close_long_first": close_long_first,
        "partial_long": partial_long,
        "partial_short": partial_short,
    }


class SMAlphatrendKama_358d77(PinePortBase, IStrategy):
    source_id = "SM_358d77df4331041c"
    source_file = "AlphaTrend与KAMA结合的自适应趋势跟踪与风险管理策略Adaptive-Trend-Following-Strategy-Combining-AlphaTrend-and-KAMA-with-Risk-Management.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "coeff": 1.0,
        "AP": 14,
        "src": "close",
        "showsignals": True,
        "novolumedata": False,
        "kamaLength": 21,
        "profitTarget": 10.0,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "BLOCKER -- `strategy.close(id, qty_percent=50)` is not expressible: "
        "`PineBroker.close` closes the WHOLE entry and no broker call takes a "
        "`qty_percent`, so the two partial-exit branches are emitted as full "
        "closes. After a +10% / -10% move the source keeps HALF the position "
        "and this port goes flat. The shared layer is not modified "
        "(PORT_BRIEF rule 9).",
        "`ta.mfi` is not in `pine_ta`; implemented here from TradingView's MFI "
        "definition (sum of series*volume over rising bars vs falling bars). "
        "Three edge cases are modelling choices, not published rules: an na "
        "change contributes 0 to both sums, an undefined ratio reads 100 (the "
        "convention `pine_ta.pine_rsi` already uses), and `math.sum` is na "
        "until `length` bars exist.",
        "`ta.tr` is called WITHOUT `handle_na`, so Pine returns na on the first "
        "bar while `pine_ta.pine_tr` returns `high - low` there "
        "(PINE_SEMANTICS.md 3.7). One bar of early seeding, which the "
        "`ta.sma(ta.tr, AP)` warm-up inherits. Public-layer boundary, recorded "
        "and not modified.",
        "`nefratio = nnoise != 0 ? nsignal / nnoise : 0` is ambiguous for an na "
        "`nnoise`; Pine v5 does not publish the truth value of `na != 0`. The "
        "port takes the na-propagating reading. It is immaterial to the "
        "resulting series (the first defined `nsmooth` is preceded by an na "
        "`nsmooth`, which resets `nAMA` through `nz` either way), and the "
        "ambiguity is recorded rather than hidden.",
        "`novolumedata` is False, so the live branch is `ta.mfi(hlc3, AP) >= 50` "
        "and `ta.rsi(src, AP)` is dead. Both branches are implemented so "
        "flipping the switch needs no code change; `src` is only read by the "
        "dead branch.",
        "`AlphaTrend` and `nAMA` are state-carrying recursions, so they are "
        "stepped bar by bar rather than expressed as a rolling window.",
        "The `var string currentPosition` / `var float entryPrice` / "
        "`var float partialExitPrice` state is updated when the SIGNAL fires, "
        "not when the fill happens, and the partial-exit test uses the value "
        "set earlier on the SAME bar. Reproduced as a pre-computed per-bar "
        "pass in the source's own block order.",
        "`showsignals` only gates `plotshape`; the `plot` / `fill` / "
        "`plotshape` / `alertcondition` calls place no condition and are not "
        "reproduced.",
        "`default_qty_type = strategy.percent_of_equity` with "
        "`default_qty_value = 100` against `initial_capital = 100000` commits "
        "the whole equity per entry. PINE_SEMANTICS.md 1.4/1.6: the engine's "
        "committed notional and the framework's wallet can drift, and a "
        "too-small declared capital turns the venue's contract step into "
        "noise-level error.",
        "No stop / limit / trail exit exists, so `source_reproduce_stops` is "
        "False, and a position still open at the end of the window stays open.",
        "No `request.security`, no `varip`, no barstate branch and no "
        "`strategy.risk.*` in the source.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding is measured by the chain verifier "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        hlc3 = (high + low + close) / 3.0
        coeff = float(params["coeff"])
        ap = int(params["AP"])
        kama_length = int(params["kamaLength"])

        # ATR = ta.sma(ta.tr, AP): a plain SMA of the true range, not ta.atr.
        atr = ta.pine_sma(ta.pine_tr(dataframe), ap)
        up_t = (low - atr * coeff).to_numpy(dtype=float)
        down_t = (high + atr * coeff).to_numpy(dtype=float)

        if bool(params["novolumedata"]):
            gate = pd.Series(ta.pine_rsi(ta.pine_source(dataframe, str(params["src"])), ap))
        else:
            gate = _pine_mfi(hlc3, dataframe["volume"], ap)
        up_leg = (gate >= 50).to_numpy()

        alpha_trend = _alpha_trend(up_t, down_t, up_leg)
        nama = _kama(close.to_numpy(dtype=float), kama_length)

        at_series = pd.Series(alpha_trend, index=dataframe.index)
        nama_series = pd.Series(nama, index=dataframe.index)
        at_lag2 = at_series.shift(2)

        cross_at = ta.pine_crossover(nama_series, at_series)
        cross_at2 = ta.pine_crossover(nama_series, at_lag2)
        crossunder_at = ta.pine_crossunder(nama_series, at_series)
        crossunder_at2 = ta.pine_crossunder(nama_series, at_lag2)

        buy_condition = (
            (cross_at & cross_at2)
            | (cross_at & (nama_series > at_lag2))
            | (cross_at2 & (nama_series > at_series))
        )
        sell_condition = (
            (crossunder_at & crossunder_at2)
            | (crossunder_at & (nama_series < at_lag2))
            | (crossunder_at2 & (nama_series < at_series))
        )

        state = _position_state_machine(
            close.to_numpy(dtype=float),
            high.to_numpy(dtype=float),
            low.to_numpy(dtype=float),
            buy_condition.fillna(False).to_numpy(dtype=bool),
            sell_condition.fillna(False).to_numpy(dtype=bool),
            float(params["profitTarget"]),
        )

        dataframe["pine_alpha_trend"] = alpha_trend
        dataframe["pine_alpha_trend_lag2"] = at_lag2
        dataframe["pine_kama"] = nama
        dataframe["pine_buy_condition"] = buy_condition
        dataframe["pine_sell_condition"] = sell_condition
        for name, values in state.items():
            dataframe[f"pine_state_{name}"] = values
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "enter_long": dataframe["pine_state_enter_long"].to_numpy(dtype=bool),
            "enter_short": dataframe["pine_state_enter_short"].to_numpy(dtype=bool),
            "close_short_first": dataframe["pine_state_close_short_first"].to_numpy(dtype=bool),
            "close_long_first": dataframe["pine_state_close_long_first"].to_numpy(dtype=bool),
            "partial_long": dataframe["pine_state_partial_long"].to_numpy(dtype=bool),
            "partial_short": dataframe["pine_state_partial_short"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (buySignal and currentPosition != "long")
        if ctx["enter_long"][i]:
            #     if (currentPosition == "short") strategy.close("Short")
            if ctx["close_short_first"][i]:
                broker.close("Short")
            #     strategy.entry("Long", strategy.long)
            broker.entry("Long", "long")

        # if (sellSignal and currentPosition != "short")
        if ctx["enter_short"][i]:
            #     if (currentPosition == "long") strategy.close("Long")
            if ctx["close_long_first"][i]:
                broker.close("Long")
            #     strategy.entry("Short", strategy.short)
            broker.entry("Short", "short")

        # if (currentPosition == "long" and high >= partialExitPrice)
        #     strategy.close("Long", ..., qty_percent=50)   <-- see blockers
        if ctx["partial_long"][i]:
            broker.close("Long")

        # if (currentPosition == "short" and low <= partialExitPrice)
        #     strategy.close("Short", ..., qty_percent=50)  <-- see blockers
        if ctx["partial_short"][i]:
            broker.close("Short")
