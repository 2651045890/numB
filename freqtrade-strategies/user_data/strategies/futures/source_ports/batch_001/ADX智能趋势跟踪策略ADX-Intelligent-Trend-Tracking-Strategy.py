"""Port of sources/SM_14f86f3b4354b4f2.pine (batch_001/ADX智能趋势跟踪策略ADX-Intelligent-Trend-Tracking-Strategy.md).

Pine v5 ("Rob Booker - ADX Breakout"). Both sides. While the ADX is BELOW a
threshold the pair is treated as consolidating; a box is drawn around the last
`boxLookBack` highs and lows and a close crossing that box boundary opens a
trade, with an OCA exit at +/- a multiple of the box width:

    dirmov(len) =>
        up        = ta.change(high)
        down      = -ta.change(low)
        truerange = ta.rma(ta.tr, len)
        plus      = fixnan(100 * ta.rma(up   > down and up   > 0 ? up   : 0, len) / truerange)
        minus     = fixnan(100 * ta.rma(down > up   and down > 0 ? down : 0, len) / truerange)
        [plus, minus]

    adx(dilen, adxlen) =>
        [plus, minus] = dirmov(dilen)
        sum = plus + minus
        100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)

    sig       = adx(adxSmoothPeriod, adxPeriod)
    isADXLow  = sig < adxLowerLevel

    var float boxUpperLevelCarry = 0
    var float boxLowerLevelCarry = 0
    boxUpperLevel = strategy.position_size == 0 ? ta.highest(high, boxLookBack)[1] : boxUpperLevelCarry
    boxUpperLevelCarry := boxUpperLevel
    boxLowerLevel = strategy.position_size == 0 ? ta.lowest(low,  boxLookBack)[1] : boxLowerLevelCarry
    boxLowerLevelCarry := boxLowerLevel
    boxWidth      = boxUpperLevel - boxLowerLevel

    profitTarget = position_size > 0 ? avg + m*boxWidth : position_size < 0 ? avg - m*boxWidth : na
    stopLoss     = position_size > 0 ? avg - s*boxWidth : position_size < 0 ? avg + s*boxWidth : na

    isBuyValid  = strategy.position_size == 0 and ta.cross(close, boxUpperLevel) and isADXLow
    strategy.exit("close_long",  from_entry="open_long",  limit=profitTarget, stop=stopLoss)
    if isBuyValid  and strategy.opentrades == 0 and (enableDirection == -1 or enableDirection == 0)
        strategy.entry("open_long",  strategy.long)

    isSellValid = strategy.position_size == 0 and ta.cross(close, boxLowerLevel) and isADXLow
    strategy.exit("close_short", from_entry="open_short", limit=profitTarget, stop=stopLoss)
    if isSellValid and strategy.opentrades == 0 and (enableDirection ==  1 or enableDirection == 0)
        strategy.entry("open_short", strategy.short)

The four calls are reproduced in exactly that order, exits before entries.

THE BOX IS A `var` CARRY, not a rolling window. `boxUpperLevelCarry` holds the
value `boxUpperLevel` had on the previous bar (`:=` runs after the read, so the
read still sees the previous bar's value). While the position is flat
`boxUpperLevel` is re-derived from `ta.highest(high, boxLookBack)[1]`; while a
position is open it holds that frozen value. Modelling it as "the last flat
bar's box" without the carry would move the box out from under an open trade.
It is modelled as per-run state in `pine_context`, because it depends on
`strategy.position_size`, which only exists during the run.

`strategy()` declares `default_qty_type = strategy.cash`, `default_qty_value =
100000` and `initial_capital = 100000`; everything else is Pine's documented
default: commission 0%, pyramiding 0, `process_orders_on_close=false`.

FIDELITY:

* `ta.tr` is called BARE (no argument), i.e. Pine's default `handle_na=false`.
  `pine_ta.pine_tr(frame, handle_na=False)` is therefore the correct counterpart
  and `pine_ta.pine_atr` is deliberately NOT used (it is `handle_na=True`, a
  different series at the first bar). PINE_SEMANTICS.md 3.7 records that the
  modelled `pine_tr` still returns `high - low` on the first bar rather than na,
  which can shift the `ta.rma` seed by one bar and leave a boundary difference
  in the ADX/DI series after warmup. Not corrected here (shared layer).
* `dirmov`'s `len` is `adxSmoothPeriod` and `adx`'s smoothing is `adxPeriod`;
  both default to 14 but they are separate inputs and are kept separate.
* `ta.change`, `ta.rma` and the ternaries are in `pine_ta`; `fixnan` is not, so
  it is written out as a forward fill (replace na with the last non-na value),
  which is its documented behaviour.
* na handling: an na operand makes a Pine comparison false, so the DI source
  ternaries evaluate to 0 while `ta.change` is na and `plus`/`minus` step
  through the rma without advancing. `fixnan` then carries the last valid value.
  `sum == 0` selects 1 as the divisor exactly as written; when `plus`/`minus`
  are na the comparison is false and the na sum propagates instead.
* MEASURED CHOICE: `100 * di / truerange` is a float division by a possibly
  zero `truerange` (a fully flat series). Pine's behaviour there is not
  published; the port maps pandas' +/-inf onto na before `fixnan`, which is the
  closest reproducible reading (an na feeds `fixnan` exactly like a warmup na).
  On BTC data `truerange` is never 0.
* `ta.cross(a, b)` is Pine v5's either-direction cross, reproduced as
  `crossover(a, b) or crossunder(a, b)` on the CURRENT and PREVIOUS box levels.
  The previous level is the `var` carry's own previous value, which is why the
  cross is evaluated in the script rather than precomputed as a column.
* `strategy.opentrades == 0` is read as `broker.open_trades == 0`; `isBuyValid`
  already requires `strategy.position_size == 0`, so the two agree.
* The two `strategy.exit` calls carry BOTH legs (stop and take-profit) and are
  placed on EVERY bar with no `when=` guard. Each is bound via `from_entry`, so
  while its entry is not open it neither fills nor publishes a level to the
  framework (PINE_SEMANTICS.md 1.12); the same-id replacement Pine performs is
  modelled by the engine's `_place` for kind == 'exit'. On a bar where the
  position is flat both legs are na -- a legless exit, which the engine never
  fills and never projects (PINE_SEMANTICS.md 1.15). In practice a position can
  only open once the box window is full (>20 bars), so while a position is open
  the legs are finite and no legless exit survives to be projected.
* The input is titled "Both(0), Long(1), Short(-1)" but the CODE enables the
  LONG when `enableDirection == -1 or == 0` and the SHORT when `== 1 or == 0` --
  i.e. `1` selects SHORT-ONLY and `-1` selects LONG-ONLY, the opposite of the
  label. The code is followed; the disagreement is recorded, not reconciled.
* `bgcolor()` / `plot()` calls are display-only and are not reproduced.
* `strategy.exit`'s `stop` / `limit` are absolute prices here (not ticks), so
  nothing is scaled by `mintick`; the exit reaches the framework through
  `pine_stop_level` / `pine_limit_level` and the ROI override.
* `default_qty_type = strategy.cash` with `default_qty_value = 100000` against
  `initial_capital = 100000` commits the whole declared capital on every entry.
  PINE_SEMANTICS.md 1.5/1.6: after any loss the engine's fixed 100000 can exceed
  the framework's wallet and the entry is vetoed. That follows from the source's
  own sizing and is not corrected here.
* The `/*backtest` header's `basePeriod: 1m` is the FMZ backtester's own
  granularity for filling 5m bars, not the strategy's period.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan`: replace na with the last non-na value."""
    return series.ffill()


def _level(value) -> float | None:
    """An na level is no level: the engine wants None, not a NaN."""
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


class SMAdxIntelligentTrendTracking_14f86f(PinePortBase, IStrategy):
    source_id = "SM_14f86f3b4354b4f2"
    source_file = "ADX智能趋势跟踪策略ADX-Intelligent-Trend-Tracking-Strategy.md"
    timeframe = "5m"
    can_short = True
    source_defaults: dict = {
        "adxSmoothPeriod": 14,
        "adxPeriod": 14,
        "adxLowerLevel": 18,
        "boxLookBack": 20,
        "profitTargetMultiple": 1.0,
        "stopLossMultiple": 0.5,
        "enableDirection": 0,
    }
    source_qty_type = "cash"
    source_qty_value = 100000.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "ta.tr is called BARE (Pine's handle_na=false default), so "
        "pine_ta.pine_tr(frame, handle_na=False) is used and pine_atr is "
        "deliberately NOT used (it is the handle_na=true series). "
        "PINE_SEMANTICS.md 3.7 records that the modelled pine_tr still returns "
        "high-low on the first bar, which can shift the ta.rma seed by one bar.",
        "`fixnan` is not in pine_ta; written out as a forward fill, which is its "
        "documented behaviour.",
        "dirmov's `len` is adxSmoothPeriod and adx's smoothing is adxPeriod; both "
        "default to 14 but they are separate inputs and stay separate.",
        "MEASURED CHOICE: 100*di/truerange divides by a possibly-zero truerange. "
        "Pine's behaviour there is not published; pandas' +/-inf is mapped onto "
        "na before fixnan, which feeds fixnan exactly like a warmup na. "
        "truerange is never 0 on BTC data.",
        "The box is a `var` CARRY (`boxUpperLevelCarry` / `boxLowerLevelCarry`), "
        "not a rolling window: while a position is open the box stays frozen at "
        "the last value derived while flat. Modelled as per-run state in "
        "pine_context because it depends on strategy.position_size.",
        "ta.cross(a, b) is v5's either-direction cross, reproduced as "
        "crossover or crossunder against the CURRENT and PREVIOUS box levels; "
        "the previous level is the var carry's previous value, so the cross is "
        "evaluated in the script rather than precomputed as a column.",
        "The two strategy.exit calls carry BOTH legs and are placed every bar "
        "with no `when=` guard, bound via from_entry; while their entry is not "
        "open they neither fill nor publish a level (PINE_SEMANTICS.md 1.12). "
        "While flat both legs are na -- a legless exit the engine never fills "
        "and never projects (PINE_SEMANTICS.md 1.15); in practice the box window "
        "keeps positions from opening before bar 20, so no legless exit survives.",
        "The input is labelled 'Both(0), Long(1), Short(-1)' but the CODE enables "
        "the LONG for enableDirection == -1 or 0 and the SHORT for == 1 or 0, so "
        "1 is SHORT-ONLY and -1 is LONG-ONLY -- the opposite of the label. Code "
        "followed, disagreement recorded.",
        "strategy.exit's stop/limit are absolute PRICES here, not ticks, so no "
        "mintick scaling is involved.",
        "strategy.opentrades == 0 is read as broker.open_trades == 0; isBuyValid "
        "already requires position_size == 0, so the two agree.",
        "default_qty_type=strategy.cash value=100000 against "
        "initial_capital=100000 commits the whole declared capital per entry. "
        "PINE_SEMANTICS.md 1.5/1.6: after a loss the engine's fixed 100000 can "
        "exceed the framework's wallet and the entry is vetoed; that follows from "
        "the source's own sizing and is not corrected here.",
        "bgcolor()/plot() are display-only and not reproduced.",
        "The /*backtest header's basePeriod: 1m is the FMZ backtester's own "
        "granularity for filling the 5m bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        high, low = dataframe["high"], dataframe["low"]
        dilen = int(params["adxSmoothPeriod"])
        adxlen = int(params["adxPeriod"])

        # up = ta.change(high) / down = -ta.change(low)
        up = ta.pine_change(high, 1)
        down = -ta.pine_change(low, 1)
        # truerange = ta.rma(ta.tr, len) -- ta.tr bare, i.e. handle_na=false
        truerange = ta.pine_rma(ta.pine_tr(dataframe, handle_na=False), dilen)

        # plus  = fixnan(100 * ta.rma(up   > down and up   > 0 ? up   : 0, len) / truerange)
        # minus = fixnan(100 * ta.rma(down > up   and down > 0 ? down : 0, len) / truerange)
        plus_src = up.where((up > down) & (up > 0.0), 0.0)
        minus_src = down.where((down > up) & (down > 0.0), 0.0)
        plus_raw = (100.0 * ta.pine_rma(plus_src, dilen)) / truerange
        minus_raw = (100.0 * ta.pine_rma(minus_src, dilen)) / truerange
        plus = _fixnan(plus_raw.replace([np.inf, -np.inf], np.nan))
        minus = _fixnan(minus_raw.replace([np.inf, -np.inf], np.nan))

        # sum = plus + minus; adx = 100 * ta.rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)
        total = plus + minus
        divisor = total.where(total != 0.0, 1.0)
        sig = 100.0 * ta.pine_rma((plus - minus).abs() / divisor, adxlen)

        dataframe["pine_plus_di"] = plus
        dataframe["pine_minus_di"] = minus
        dataframe["pine_adx"] = sig
        # isADXLow = sig < adxLowerLevel -- an na sig compares false.
        dataframe["pine_is_adx_low"] = (sig < float(params["adxLowerLevel"])).fillna(False)
        # The box, lagged one bar, for the flat case:
        #   ta.highest(high, boxLookBack)[1] / ta.lowest(low, boxLookBack)[1]
        lookback = int(params["boxLookBack"])
        dataframe["pine_box_upper_lag1"] = ta.pine_highest(high, lookback).shift(1)
        dataframe["pine_box_lower_lag1"] = ta.pine_lowest(low, lookback).shift(1)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "box_upper_lag1": dataframe["pine_box_upper_lag1"].to_numpy(dtype=float),
            "box_lower_lag1": dataframe["pine_box_lower_lag1"].to_numpy(dtype=float),
            "is_adx_low": dataframe["pine_is_adx_low"].to_numpy(dtype=bool),
            "profit_multiple": float(params["profitTargetMultiple"]),
            "stop_multiple": float(params["stopLossMultiple"]),
            "enable_direction": int(params["enableDirection"]),
            # `var float boxUpperLevelCarry = 0` / `var float boxLowerLevelCarry = 0`
            "state": {"box_upper": 0.0, "box_lower": 0.0},
        }

    def pine_script(self, broker, i, ctx):
        state = ctx["state"]
        close = ctx["close"]
        position = broker.position_size
        # Read the carries BEFORE this bar's `:=`, which is what Pine does.
        previous_upper = state["box_upper"]
        previous_lower = state["box_lower"]

        # boxUpperLevel = strategy.position_size == 0 ? ta.highest(high, boxLookBack)[1]
        #                                                   : boxUpperLevelCarry
        # boxUpperLevelCarry := boxUpperLevel
        if position == 0:
            box_upper = float(ctx["box_upper_lag1"][i])
            box_lower = float(ctx["box_lower_lag1"][i])
        else:
            box_upper = previous_upper
            box_lower = previous_lower
        state["box_upper"] = box_upper
        state["box_lower"] = box_lower

        box_width = box_upper - box_lower

        # profitTarget / stopLoss off strategy.position_avg_price (na while flat).
        average = broker.position_avg_price
        profit_multiple = ctx["profit_multiple"]
        stop_multiple = ctx["stop_multiple"]
        if position > 0:
            profit_target = average + profit_multiple * box_width
            stop_loss = average - stop_multiple * box_width
        elif position < 0:
            profit_target = average - profit_multiple * box_width
            stop_loss = average + stop_multiple * box_width
        else:
            profit_target = float("nan")
            stop_loss = float("nan")

        # ta.cross(close, boxUpperLevel) / ta.cross(close, boxLowerLevel):
        # a > b and a[1] <= b[1]  OR  a < b and a[1] >= b[1]. The levels' own
        # previous-bar values are the carries read above. na compares false.
        if i > 0:
            previous_close = close[i - 1]
            cross_upper = (
                (close[i] > box_upper and previous_close <= previous_upper)
                or (close[i] < box_upper and previous_close >= previous_upper)
            )
            cross_lower = (
                (close[i] > box_lower and previous_close <= previous_lower)
                or (close[i] < box_lower and previous_close >= previous_lower)
            )
        else:
            cross_upper = False
            cross_lower = False

        is_adx_low = bool(ctx["is_adx_low"][i])
        direction = ctx["enable_direction"]

        # isBuyValid = strategy.position_size == 0 and ta.cross(close, boxUpperLevel) and isADXLow
        is_buy_valid = position == 0 and cross_upper and is_adx_low
        # isSellValid = strategy.position_size == 0 and ta.cross(close, boxLowerLevel) and isADXLow
        is_sell_valid = position == 0 and cross_lower and is_adx_low

        # strategy.exit("close_long", from_entry="open_long", limit=profitTarget, stop=stopLoss)
        broker.exit(
            "close_long",
            from_entry="open_long",
            limit=_level(profit_target),
            stop=_level(stop_loss),
        )
        # if isBuyValid and strategy.opentrades == 0 and (enableDirection == -1 or enableDirection == 0)
        #     strategy.entry("open_long", strategy.long)
        if is_buy_valid and broker.open_trades == 0 and (direction == -1 or direction == 0):
            broker.entry("open_long", "long")

        # strategy.exit("close_short", from_entry="open_short", limit=profitTarget, stop=stopLoss)
        broker.exit(
            "close_short",
            from_entry="open_short",
            limit=_level(profit_target),
            stop=_level(stop_loss),
        )
        # if isSellValid and strategy.opentrades == 0 and (enableDirection == 1 or enableDirection == 0)
        #     strategy.entry("open_short", strategy.short)
        if is_sell_valid and broker.open_trades == 0 and (direction == 1 or direction == 0):
            broker.entry("open_short", "short")
