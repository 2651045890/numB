"""Port of sources/SM_e5ca8cb5744904e6.pine (batch_001/ATR均线突破策略-ATR-Average-Breakout-Strategy.md).

Pine v5, `strategy("Consolidation Breakout Strategy", overlay=true)`. An SMA of
close with an ATR band around it; a bar whose HIGH pierces the upper band opens
a long and one whose LOW pierces the lower band opens a short, both closed by a
`strategy.close` when the opposite band is reached:

    atr_value     = ta.atr(length)
    average_price = ta.sma(close, length)
    upper_bound   = average_price + multiplier * atr_value
    lower_bound   = average_price - multiplier * atr_value

    is_consolidating = (high < upper_bound) and (low > lower_bound)
    is_breakout_up   = high > upper_bound
    is_breakout_down = low  < lower_bound

    enter_long  = is_breakout_up   and not is_consolidating
    enter_short = is_breakout_down and not is_consolidating

    exit_long  = low < (average_price - atr_value * stop_loss_percentage)
                 or high > (average_price + atr_value * take_profit_percentage)
    exit_short = high > (average_price + atr_value * stop_loss_percentage)
                 or low < (average_price - atr_value * take_profit_percentage)

    risk_per_trade = strategy.equity * (risk_percentage / 100)
    position_size  = risk_per_trade / atr_value

    if (enter_long)  -> strategy.entry("Long",  strategy.long,  qty=position_size)
    if (enter_short) -> strategy.entry("Short", strategy.short, qty=position_size)
    if (exit_long)   -> strategy.close("Long")
    if (exit_short)  -> strategy.close("Short")

`not is_consolidating` is REDUNDANT: `high > upper_bound` already makes
`high < upper_bound` false, so `enter_long` is exactly `is_breakout_up` (and
`enter_short` exactly `is_breakout_down`). The conjunction is evaluated as
written rather than reduced, because the na semantics of the two forms would
part company if it were dropped (`~nan_comparison` is not `nan`).

`stop_loss_percentage` / `take_profit_percentage` are percent-SCALED
multipliers applied to ATR (`average_price - atr_value * 1.0`), matching the
source's own arithmetic; they are not divided by 100.

Both entries pass an explicit `qty` and neither passes `stop=` / `limit=`, so
they are plain MARKET orders and DO project faithfully onto the framework (the
engine fills at the next bar's open, exactly where Freqtrade fills the
projected signal). Both `strategy.close` calls are market closes and project
too. This source therefore has no resting-entry or resting-exit boundary.

Sizing is worth stating because it drives the framework: `risk_percentage`
defaults to 1.0, so `position_size = strategy.equity * 0.01 / atr_value` -- a
position whose NOTIONAL is `0.01 * equity * close / atr_value`, roughly 40% of
equity at BTC's price/ATR ratio, and it grows with the equity the engine
accumulates. The port hands the framework the engine's own recorded fill
notional (PINE_SEMANTICS.md 1.4) rather than re-deriving it.

The header declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is
"1h"; its `basePeriod: 15m` is the FMZ backtester's own granularity for filling
those hourly bars, not the strategy's period. (`start`/`end` there span only a
week; the chain verifier runs its own window, not the header's.)

FIDELITY:

* `ta.atr(length)` is Pine's `ta.rma(ta.tr(true), length)`, i.e.
  `pine_ta.pine_atr`, whose first bar is `high - low` rather than na. The
  modelled `ta.rma` seeds on the SMA of the first `length` observations, so the
  ATR is defined from bar `length - 1` and everything before it is na, which is
  what makes `upper_bound` na and every band condition false during warm-up (a
  comparison against na is false, and `na` does not propagate through `and` /
  `or` into a true).
* The md's prose says the exit fires "when price returns INSIDE the bands". The
  code exits when price pierces FURTHER beyond them (`low < lower band -
  atr*sl%` for a long, `high > upper band + atr*tp%` for a short). The code is
  followed; the disagreement is recorded.
* `strategy()` declares only `title` and `overlay`, so `strategy.fixed` / 1
  contract, initial capital 1000000, commission 0%, `pyramiding 0` and
  `process_orders_on_close=false` are Pine's defaults. `qty` is explicit, so
  the default quantity never binds.
* `strategy.equity` is read from the engine's bar-close equity, the same
  quantity the source reads when it sizes the order on the signal bar.
* No `strategy.exit` exists, so `source_reproduce_stops` is False: both exits
  are market closes and are projected as `exit_long` / `exit_short`.
* `position_size` is na while `atr_value` is na, and a na `qty` makes the
  engine fall back to `strategy.fixed` / 1 contract -- the same thing Pine does
  with `qty = na`. Unreachable on a real signal bar (an entry needs a finite
  `upper_bound` / `lower_bound`, hence a finite ATR), but written out.
* If a bar satisfies both an entry and the SAME side's exit condition, the
  engine opens on the next open and closes it on the following one; the
  projection has no separate bar for the close (PINE_SEMANTICS.md 1.13). The
  source is not of that shape here (its exits need the opposite band), so it is
  recorded as a boundary rather than measured on this port.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures that rounding separately rather
  than treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAtrAverageBreakout_e5ca8c(PinePortBase, IStrategy):
    source_id = "SM_e5ca8cb5744904e6"
    source_file = "ATR均线突破策略-ATR-Average-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "length": 20,
        "multiplier": 2.0,
        "risk_percentage": 1.0,
        "stop_loss_percentage": 1.0,
        "take_profit_percentage": 2.0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No stop/limit exit exists: both exits are strategy.close market orders.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both entries are plain market orders (no stop=/limit=) and both exits "
        "are strategy.close market orders, so this source has no resting-order "
        "boundary: the engine's next-open fill is where the framework's projected "
        "signal fills too.",
        "ta.atr(length) is pine_ta.pine_atr, i.e. ta.rma(ta.tr(true), length); the "
        "modelled rma seeds on the SMA of the first `length` observations, so the "
        "ATR is na before bar length-1 and every band condition is false during "
        "warm-up (a comparison against na is false and na does not AND/OR into a "
        "true). PINE_SEMANTICS.md 3.7 records the first-bar ta.tr choice.",
        "`not is_consolidating` is redundant against `high > upper_bound` and is "
        "kept as written rather than reduced; the two spellings differ in their na "
        "behaviour.",
        "The md's prose calls the exit 'price returning inside the bands'; the code "
        "exits when price pierces FURTHER beyond them (low < lower band - atr*sl% "
        "for a long). Code followed, disagreement recorded.",
        "stop_loss_percentage / take_profit_percentage are percent-scaled "
        "multipliers on ATR (1.0 and 2.0), used directly and never divided by 100, "
        "matching the source's arithmetic.",
        "Sizing is position_size = strategy.equity * risk_percentage/100 / atr_value "
        "with risk_percentage defaulting to 1.0, so the committed notional is about "
        "0.01*equity*close/atr and grows as the engine's equity grows; the framework "
        "is handed the engine's recorded fill notional (PINE_SEMANTICS.md 1.4).",
        "strategy() declares only title/overlay, so strategy.fixed / 1 contract, "
        "initial capital 1000000, commission 0%, pyramiding 0 and "
        "process_orders_on_close=false are Pine's documented defaults; qty is passed "
        "explicitly so the default quantity never binds.",
        "No strategy.exit exists, so source_reproduce_stops is False.",
        "The /*backtest header's basePeriod: 15m is the FMZ backtester's own "
        "granularity for filling the hourly bars, not the strategy's period; the "
        "header's one-week start/end window is not used by the chain verifier.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]
        length = int(params["length"])
        multiplier = float(params["multiplier"])

        atr_value = ta.pine_atr(dataframe, length)
        average_price = ta.pine_sma(close, length)
        upper_bound = average_price + multiplier * atr_value
        lower_bound = average_price - multiplier * atr_value

        # A comparison against na is FALSE in Pine's boolean context, and na does
        # not OR into a true; pandas yields False for those comparisons too.
        is_consolidating = (high < upper_bound) & (low > lower_bound)
        is_breakout_up = high > upper_bound
        is_breakout_down = low < lower_bound

        enter_long = is_breakout_up & (~is_consolidating)
        enter_short = is_breakout_down & (~is_consolidating)

        stop_loss_percentage = float(params["stop_loss_percentage"])
        take_profit_percentage = float(params["take_profit_percentage"])
        exit_long = (low < (average_price - atr_value * stop_loss_percentage)) | (
            high > (average_price + atr_value * take_profit_percentage)
        )
        exit_short = (high > (average_price + atr_value * stop_loss_percentage)) | (
            low < (average_price - atr_value * take_profit_percentage)
        )

        dataframe["pine_atr"] = atr_value
        dataframe["pine_average_price"] = average_price
        dataframe["pine_upper_bound"] = upper_bound
        dataframe["pine_lower_bound"] = lower_bound
        dataframe["pine_is_consolidating"] = is_consolidating
        dataframe["pine_enter_long"] = enter_long
        dataframe["pine_enter_short"] = enter_short
        dataframe["pine_exit_long"] = exit_long
        dataframe["pine_exit_short"] = exit_short
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "atr": dataframe["pine_atr"].to_numpy(dtype=float),
            "enter_long": dataframe["pine_enter_long"].to_numpy(dtype=bool),
            "enter_short": dataframe["pine_enter_short"].to_numpy(dtype=bool),
            "exit_long": dataframe["pine_exit_long"].to_numpy(dtype=bool),
            "exit_short": dataframe["pine_exit_short"].to_numpy(dtype=bool),
            "risk_fraction": float(params["risk_percentage"]) / 100.0,
        }

    def pine_script(self, broker, i, ctx):
        # risk_per_trade = strategy.equity * (risk_percentage / 100)
        risk_per_trade = broker.equity * ctx["risk_fraction"]
        # position_size = risk_per_trade / atr_value  (na while the ATR is na)
        atr_value = ctx["atr"][i]
        if np.isfinite(atr_value) and atr_value != 0.0:
            position_size = risk_per_trade / atr_value
        else:
            position_size = float("nan")

        # if (enter_long)  strategy.entry("Long", strategy.long, qty=position_size)
        if ctx["enter_long"][i]:
            broker.entry("Long", "long", qty=position_size)
        # if (enter_short) strategy.entry("Short", strategy.short, qty=position_size)
        if ctx["enter_short"][i]:
            broker.entry("Short", "short", qty=position_size)

        # if (exit_long)  strategy.close("Long")
        if ctx["exit_long"][i]:
            broker.close("Long")
        # if (exit_short) strategy.close("Short")
        if ctx["exit_short"][i]:
            broker.close("Short")
