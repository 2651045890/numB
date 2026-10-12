"""Port of sources/SM_8a74439a29a45cd7.pine
(batch_001/EMA与SuperTrend组合趋势跟踪策略EMA-and-SuperTrend-Combined-Trend-Following-Strategy.md).

Pine v5. An EMA filters the direction and a SuperTrend line times the entry:

    usedEma = ta.ema(close, ema1)                  # ema1 default 34
    atrPeriod = int(mult)                          # mult default 2.0 -> 2
    [supertrend, direction] = ta.supertrend(length, atrPeriod)   # length default 10

    longEntry  = ta.crossover(close, supertrend)  and close > usedEma
    shortEntry = ta.crossunder(close, supertrend) and close < usedEma
    longExit   = ta.crossunder(close, supertrend) or  close < usedEma
    shortExit  = ta.crossover(close, supertrend)  or  close > usedEma

    if longEntry  -> strategy.entry("Buy",  strategy.long)
    if longExit   -> strategy.close("Buy")
    if shortEntry -> strategy.entry("Sell", strategy.short)
    if shortExit  -> strategy.close("Sell")

The source's own call order (Buy entry, Buy close, Sell entry, Sell close) is
reproduced verbatim. A side's exit condition is a superset of the opposite
side's entry condition, so an entry and a close of the other id can be placed on
one bar; the engine's ordering handles that the way it handles every same-bar
pair (PINE_SEMANTICS.md section 1.13).

`strategy()` declares only title/overlay, so every other property is Pine's
documented default: `default_qty_type=strategy.fixed`, `default_qty_value=1`,
commission 0%, `pyramiding=0`, `process_orders_on_close=false`, initial capital
1000000. Both entries pass no qty.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those daily bars.

No stop, limit, profit, loss or trail call exists anywhere, so
`source_reproduce_stops` is False and a side is only closed by `strategy.close`.

FIDELITY:

* `ta.supertrend` is a TradingView built-in whose internals are not public. The
  port follows the equivalent implementation published in the Pine Script v5
  Reference (`src = hl2`, bands `hl2 +/- factor * ta.atr(atrPeriod)`, previous
  bands seeded with `nz()`, and the documented direction recursion), which is a
  MODELLED CHOICE: the line, its flips and therefore every signal are a parity
  risk until compared bar by bar against TradingView output. Pine's na rules are
  applied inside it (`nz` on the previous bar's bands, and a comparison with an
  na operand being false), and `atr` is `pine_ta.pine_atr` (the
  `handle_na=true` true-range series, which is what `ta.atr` is defined as).
* md vs source: the md's argument table names v_input_int_1=10 "SuperTrend
  Length" and v_input_float_1=2 "Multiplier", but the source passes `length` as
  `ta.supertrend`'s FIRST argument (the factor) and `int(mult)` as its second
  (the ATR period). So the two inputs act with the roles opposite to their
  labels: the "Length" input is the multiplier and the "Multiplier" input is the
  ATR period. The source governs and the roles are preserved exactly.
* `int(mult)` is Pine's truncating float-to-int cast (not `math.round`); with the
  default 2.0 it yields 2 either way, so no rounding choice is observable here.
* `emaLength` (`input.int(34, 'EMA UpTrend', minval=1, maxval=300)`) is DECLARED
  BUT NEVER USED: the code uses the second, identically-defaulted `ema1`. Both
  default to 34, so no number changes; both are carried in `source_defaults`.
* `shema` (`input(true, ...)`) is used only by the final `plot()`, which is
  display-only, so it places nothing; it is carried in `source_defaults` for
  visibility.
* `direction` (the second `ta.supertrend` return) is bound in the source but
  never read by any condition; it is returned by the helper and unused.
* `close > usedEma` / `close < usedEma` read the CURRENT bar's close, which is
  not future data: Pine evaluates the script at that bar's close.
* `ta.ema` seeding is the modelled 'first non-na value' choice
  (PINE_SEMANTICS.md section 3.1), a parity risk versus TradingView.
* `plot(...)` and `overlay` are display-only.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float) -> float:
    """Pine `nz`: an na value becomes 0."""
    return 0.0 if value is None or np.isnan(value) else float(value)


def _pine_gt(left: float, right: float) -> bool:
    """Pine `>`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left > right)


def _pine_lt(left: float, right: float) -> bool:
    """Pine `<`: a comparison with an na operand is false."""
    if np.isnan(left) or np.isnan(right):
        return False
    return bool(left < right)


def _pine_supertrend(dataframe: pd.DataFrame, factor: float, atr_period: int):
    """Pine `ta.supertrend(factor, atrPeriod)` -> (supertrend, direction).

    The equivalent implementation from the Pine v5 Reference, reproduced with
    Pine's na rules (`nz` on the previous bar's bands; a comparison with an na
    operand is false). `direction` is -1 in an up trend and +1 in a down trend.
    On the first bars, where `atr` is still na, the reference's `if na(atr[1])`
    branch sets `direction = 1` and the bands fall back to `nz(na) = 0`.
    """
    src = (dataframe["high"] + dataframe["low"]) / 2.0
    atr = ta.pine_atr(dataframe, atr_period)
    raw_upper = (src + factor * atr).to_numpy(dtype=float)
    raw_lower = (src - factor * atr).to_numpy(dtype=float)
    atr_values = atr.to_numpy(dtype=float)
    close = dataframe["close"].to_numpy(dtype=float)

    size = len(dataframe)
    upper = np.full(size, np.nan)
    lower = np.full(size, np.nan)
    supertrend = np.full(size, np.nan)
    direction = np.ones(size, dtype=float)

    for i in range(size):
        previous_close = close[i - 1] if i >= 1 else np.nan
        prev_lower = _nz(lower[i - 1]) if i >= 1 else 0.0
        prev_upper = _nz(upper[i - 1]) if i >= 1 else 0.0

        # lowerBand := lowerBand > prevLowerBand or close[1] < prevLowerBand ? lowerBand : prevLowerBand
        lower[i] = (
            raw_lower[i]
            if _pine_gt(raw_lower[i], prev_lower) or _pine_lt(previous_close, prev_lower)
            else prev_lower
        )
        # upperBand := upperBand < prevUpperBand or close[1] > prevUpperBand ? upperBand : prevUpperBand
        upper[i] = (
            raw_upper[i]
            if _pine_lt(raw_upper[i], prev_upper) or _pine_gt(previous_close, prev_upper)
            else prev_upper
        )

        prev_supertrend = supertrend[i - 1] if i >= 1 else np.nan
        if i == 0 or np.isnan(atr_values[i - 1]):
            current = 1.0
        elif not np.isnan(prev_supertrend) and prev_supertrend == prev_upper:
            current = -1.0 if _pine_gt(close[i], upper[i]) else 1.0
        else:
            current = 1.0 if _pine_lt(close[i], lower[i]) else -1.0

        direction[i] = current
        supertrend[i] = lower[i] if current == -1.0 else upper[i]

    return (
        pd.Series(supertrend, index=dataframe.index, dtype=float),
        pd.Series(direction, index=dataframe.index, dtype=float),
    )


class SMEmaAndSuperTrendTrendFollowing_8a7443(PinePortBase, IStrategy):
    source_id = "SM_8a74439a29a45cd7"
    source_file = "EMA与SuperTrend组合趋势跟踪策略EMA-and-SuperTrend-Combined-Trend-Following-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "length": 10,
        "mult": 2.0,
        "emaLength": 34,
        "ema1": 34,
        "shema": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.supertrend is a TradingView built-in whose internals are not "
        "public; the port follows the equivalent implementation published in "
        "the Pine v5 Reference (hl2 bands +/- factor*ta.atr(atrPeriod), bands "
        "seeded with nz(), documented direction recursion). MODELLED CHOICE: "
        "the line, its flips and every signal are a parity risk until compared "
        "bar by bar against TradingView output.",
        "md vs source: the md labels the inputs 'SuperTrend Length' (10) and "
        "Multiplier' (2.0), but the source passes `length` as ta.supertrend's "
        "FACTOR and `int(mult)` as its ATR PERIOD -- the roles are opposite to "
        "the labels. The source governs and the roles are preserved exactly.",
        "`int(mult)` is Pine's truncating float-to-int cast (not math.round); "
        "2.0 -> 2 either way, so no rounding choice is observable with the "
        "source's default.",
        "`emaLength` (input.int(34)) is DECLARED BUT NEVER USED: the code uses "
        "the identically-defaulted `ema1`. Both are carried in source_defaults.",
        "`shema` (input(true)) is used only by the final plot(), which is "
        "display-only; it places nothing.",
        "`direction` (the second ta.supertrend return) is bound in the source "
        "but never read by any condition; the helper returns it and the port "
        "does not use it.",
        "close > / < usedEma reads the CURRENT bar's close, which is not future "
        "data: Pine evaluates the script at that bar's close.",
        "No stop/limit/profit/loss/trail call exists, so source_reproduce_stops "
        "is False and a side is only closed by strategy.close.",
        "strategy() declares only title/overlay: fixed/1 sizing, 0% commission, "
        "pyramiding 0, process_orders_on_close=false, initial capital 1000000.",
        "ta.atr uses pine_ta's documented handle_na=true true-range series and "
        "rma seeding; ta.ema uses the 'first non-na value' seeding "
        "(PINE_SEMANTICS.md sections 3.1 and 3.7). Modelled choices, parity "
        "risks versus TradingView.",
        "plot and overlay are display-only.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        used_ema = ta.pine_ema(close, int(params["ema1"]))
        # length is ta.supertrend's factor; int(mult) is its ATR period.
        factor = float(params["length"])
        atr_period = int(float(params["mult"]))
        supertrend, _direction = _pine_supertrend(dataframe, factor, atr_period)

        dataframe["pine_used_ema"] = used_ema
        dataframe["pine_supertrend"] = supertrend

        cross_up = ta.pine_crossover(close, supertrend)
        cross_down = ta.pine_crossunder(close, supertrend)
        dataframe["pine_long_entry"] = cross_up & (close > used_ema)
        dataframe["pine_short_entry"] = cross_down & (close < used_ema)
        dataframe["pine_long_exit"] = cross_down | (close < used_ema)
        dataframe["pine_short_exit"] = cross_up | (close > used_ema)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_entry": dataframe["pine_long_entry"].to_numpy(),
            "short_entry": dataframe["pine_short_entry"].to_numpy(),
            "long_exit": dataframe["pine_long_exit"].to_numpy(),
            "short_exit": dataframe["pine_short_exit"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # The source's own call order: Buy entry, Buy close, Sell entry, Sell
        # close.
        if ctx["long_entry"][i]:
            broker.entry("Buy", "long")
        if ctx["long_exit"][i]:
            broker.close("Buy")
        if ctx["short_entry"][i]:
            broker.entry("Sell", "short")
        if ctx["short_exit"][i]:
            broker.close("Sell")
