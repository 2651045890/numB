"""Port of sources/SM_3c67723544afef58.pine (batch_001/Backtesting-Indicator.md).

Pine v5. Three EMAs of close (14 / 22 / 200) drive a buy alert, and a trailing
stop built on the buy price drives the sell alert:

    alertBuy       = ta.crossover(ema1, ema2) and close > ema3
    buyAlert       = alertBuy and the last signal was not a buy
    alertBuyValue  = ta.valuewhen(buyAlert, close, 0)
    alertSellValueLow = alertBuyValue - alertBuyValue * sellLow

    # trailing stop, armed at buy + trailStopArm and following close up
    TSLTriggerValue := alertBuyValue * (1 + trailStopArm)   # on buyAlert
    beginTrail = TSLRunning and not TSLActive and
                 close > alertBuyValue * (1 + trailStopArm) and
                 ta.crossover(close, TSLTriggerValue)
    runTrail   = TSLActive and (ta.crossover(close, TSLTriggerValue) or
                                close >= TSLTriggerValue)
    TSL        = TSLActive and (ta.crossunder(close, TSLStop) or
                                (close[1] > TSLStop and close < TSLStop))
    Sell1 = TSL ; Sell2 = ta.crossunder(close, alertSellValueLow)
    sellAlert = (Sell1 or Sell2) and the last signal was not a sell

and the order block appended at the end of the file:

    if buyAlert
        strategy.entry("Enter Long", strategy.long)
    else if sellAlert
        strategy.entry("Enter Short", strategy.short)

The sell alert does NOT close the long: it opens a SHORT. There is no exit call
anywhere in the appended block (see FIDELITY on the commented-out original), so
a position is only left by the opposite entry reversing it, and the trailing
stop only decides when the reverse happens.

The file declares `indicator(...)`, not `strategy(...)`, so no strategy()
properties exist: Pine's documented defaults are recorded in the source_*
attributes -- fixed 1-unit sizing, 0% commission, pyramiding 0, initial capital
1000000 USD.

FIDELITY:

* The trade behaviour is the indicator plus the appended block
  (PINE_SEMANTICS.md 1.17), NOT the strategy the source has commented out a few
  lines above it. That commented block would have been a `percent_of_equity`
  90% long-only strategy with 0.075% commission and `strategy.close_all` on the
  sell signal; it is dead text and none of it is reproduced. The `openBalance`,
  `pctAllocated` and `commission` inputs belong to that dead block and are never
  read by any live line -- they are carried in source_defaults but affect
  nothing.
* Everything that feeds the two alerts runs in one bar-by-bar pass, in the
  source's statement order, because the `var` state and the same-bar
  reassignments interact: a buy arms the trailing stop at the raw buy value and
  the very same bar can then run the trail, move the trigger to `close` and
  cross back below the stop.
* `and` / `or` with na: Pine treats a comparison with na as false, so the first
  bars (before the EMAs or the trailing levels exist) evaluate false rather than
  raising. The port builds every comparison with na-as-false.
* `ta.valuewhen(buyAlert, close, 0)` is reproduced as a carry inside that same
  pass (pine_ta.pine_valuewhen computes the identical series but cannot share
  the pass, because the trailing state reads it in the same bar it updates).
* The strategy has no `when=` on any entry and never passes qty, stop or limit,
  so both entries are plain market orders filling at the next bar's open.
* `buyActive` is written but never read by any live line; the dead state is kept
  so the source's assignments are all on the record.
* No exit call exists, so `source_reproduce_stops` is False.
* plot / plotshape / alertcondition / the commented-out alerts are display-only.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _cross_over(left_now, left_prev, right_now, right_prev):
    """Pine `ta.crossover`, false when any side is na."""
    if not (np.isfinite(left_now) and np.isfinite(left_prev)
            and np.isfinite(right_now) and np.isfinite(right_prev)):
        return False
    return left_now > right_now and left_prev <= right_prev


def _cross_under(left_now, left_prev, right_now, right_prev):
    """Pine `ta.crossunder`, false when any side is na."""
    if not (np.isfinite(left_now) and np.isfinite(left_prev)
            and np.isfinite(right_now) and np.isfinite(right_prev)):
        return False
    return left_now < right_now and left_prev >= right_prev


def _above(value, other):
    """A Pine comparison: false whenever either side is na."""
    return np.isfinite(value) and np.isfinite(other) and value > other


class SMBacktestingIndicator_3c6772(PinePortBase, IStrategy):
    source_id = "SM_3c67723544afef58"
    source_file = "Backtesting-Indicator.md"
    timeframe = "1h"
    can_short = True
    source_defaults = {
        # "Back Test" group -- declared, never read by a live line (see notes).
        "openBalance": 3000.0,
        "pctAllocated": 0.9,
        "commission": 0.075,
        # "Sell Settings" group -- these drive the trailing stop.
        "sellLow": 0.035,
        "trailStopArm": 0.0065,
        "trailStopPct": 0.003,
        # "Trend Line Settings" group.
        "ema1Len": 14,
        "ema1Src": "close",
        "ema2Len": 22,
        "ema2Src": "close",
        "ema3Len": 200,
        "ema3Src": "close",
    }
    # indicator(...) declares no strategy() properties, so Pine's documented
    # defaults apply: fixed 1 unit, 0% commission, pyramiding 0, capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares `indicator(...)`, not `strategy(...)` "
        "(PINE_SEMANTICS.md 1.17). The trading behaviour is the indicator plus "
        "the order block appended at the end of the file: long on buyAlert, "
        "short on sellAlert, and NO exit call -- so a position is only left by "
        "the opposite entry reversing it and source_reproduce_stops is False.",
        "The block the source has COMMENTED OUT above the live one would have "
        "been a percent_of_equity 90% strategy with 0.075% commission, "
        "margin_long/short 100 and `strategy.close_all(sellAlert, 'Sell')`. It is "
        "dead text and is NOT reproduced; the live block uses Pine's defaults "
        "(fixed 1 unit, 0% commission).",
        "openBalance / pctAllocated / commission are inputs of that dead block "
        "and are read by no live line; they are carried in source_defaults so "
        "the source's defaults are all on the record, but they cannot affect a "
        "signal.",
        "The sell alert opens a SHORT; it does not close the long. Reading "
        "'Sell' as an exit would make this a different strategy.",
        "The whole alert/TSL chain runs in one bar-by-bar pass in the source's "
        "statement order: the `var` state plus same-bar reassignment matter (a "
        "buy arms the trailing trigger and the same bar can then move it to "
        "`close`), so it cannot be vectorised faithfully.",
        "Pine treats a comparison involving na as false and an na condition as "
        "false, so the warmup bars (EMAs not yet defined, no buy price yet) "
        "evaluate false; the port builds each comparison that way instead of "
        "letting na propagate into a signal.",
        "The `[1]` side of every cross is the value the series held at the END of "
        "the previous bar: the trailing trigger and stop are reassigned inside "
        "the bar, so their previous values are captured separately rather than "
        "read off the freshly updated ones.",
        "ta.valuewhen(buyAlert, close, 0) is reproduced as a carry inside that "
        "same pass; pine_ta.pine_valuewhen computes the identical series but is "
        "not usable here because the trailing state reads the carried value in "
        "the bar that (re)sets it.",
        "buyActive is written but never read by any live line; the assignments "
        "are kept verbatim so the source's state machine is on the record.",
        "plot / plotshape / alertcondition and the commented-out alerts are "
        "display-only and place no order.",
        "The /*backtest header's basePeriod: 15m is the host's intrabar "
        "granularity, not the strategy's period; the header's start/end window "
        "is not applied -- the port runs on whatever range the caller supplies.",
    ]

    def pine_indicators(self, dataframe, params):
        ema1 = ta.pine_ema(
            ta.pine_source(dataframe, params["ema1Src"]), int(params["ema1Len"])
        )
        ema2 = ta.pine_ema(
            ta.pine_source(dataframe, params["ema2Src"]), int(params["ema2Len"])
        )
        ema3 = ta.pine_ema(
            ta.pine_source(dataframe, params["ema3Src"]), int(params["ema3Len"])
        )
        dataframe["pine_ema1"] = ema1
        dataframe["pine_ema2"] = ema2
        dataframe["pine_ema3"] = ema3

        # alertBuy = ta.crossover(ema1, ema2) and close > ema3
        alert_buy = (
            ta.pine_crossover(ema1, ema2) & (dataframe["close"] > ema3)
        ).to_numpy()

        close = dataframe["close"].to_numpy(dtype=float)
        count = len(close)
        sell_low = float(params["sellLow"])
        arm = float(params["trailStopArm"])
        trail = float(params["trailStopPct"])

        buy_alert = np.zeros(count, dtype=bool)
        sell_alert = np.zeros(count, dtype=bool)

        # `var` state, initialised on the first bar only.
        last_signal = 0
        buy_active = 0
        tsl_active = 0
        tsl_running = 0
        tsl_trigger = 0.0
        tsl_stop = 0.0
        buy_value = np.nan          # alertBuyValue, carried by valuewhen
        previous_close = np.nan
        # The `[1]` side of every cross is the value the series had at the END
        # of the previous bar, which the same-bar reassignments below can change.
        previous_trigger = np.nan
        previous_stop = np.nan
        previous_sell_value_low = np.nan

        for i in range(count):
            # ---- buy side: filter redundant signals -----------------------
            if alert_buy[i] and last_signal != 1:
                last_signal = 1
                buy_alert[i] = True
            if buy_alert[i]:
                buy_active = 1
                buy_value = close[i]            # valuewhen(buyAlert, close, 0)
            sell_value_low = buy_value - buy_value * sell_low

            # ---- trailing stop --------------------------------------------
            if buy_alert[i]:
                tsl_trigger = buy_value + buy_value * arm
                tsl_active = 0
                tsl_running = 1
                tsl_stop = tsl_trigger - tsl_trigger * trail

            begin_trail = (
                tsl_running == 1
                and tsl_active == 0
                and _above(close[i], buy_value + buy_value * arm)
                and _cross_over(close[i], previous_close, tsl_trigger, previous_trigger)
            )
            if begin_trail:
                tsl_trigger = close[i]
                tsl_active = 1
                tsl_stop = tsl_trigger - tsl_trigger * trail

            run_trail = tsl_active == 1 and (
                _cross_over(close[i], previous_close, tsl_trigger, previous_trigger)
                or close[i] >= tsl_trigger
            )
            if run_trail:
                tsl_trigger = close[i]
                tsl_stop = tsl_trigger - tsl_trigger * trail

            tsl = tsl_active == 1 and (
                _cross_under(close[i], previous_close, tsl_stop, previous_stop)
                or (_above(previous_close, tsl_stop) and close[i] < tsl_stop)
            )

            # ---- sell side: filter redundant signals ----------------------
            alert_sell = tsl or _cross_under(
                close[i], previous_close, sell_value_low, previous_sell_value_low
            )
            if alert_sell and last_signal != -1:
                last_signal = -1
                sell_alert[i] = True
            if sell_alert[i]:
                tsl_active = 0
                tsl_running = 0
                buy_active = 0

            previous_close = close[i]
            previous_trigger = tsl_trigger
            previous_stop = tsl_stop
            previous_sell_value_low = sell_value_low

        dataframe["pine_buy_alert"] = buy_alert
        dataframe["pine_sell_alert"] = sell_alert
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "buy_alert": dataframe["pine_buy_alert"].to_numpy(),
            "sell_alert": dataframe["pine_sell_alert"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buyAlert
        #     strategy.entry("Enter Long", strategy.long)
        # else if sellAlert
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_alert"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_alert"][i]:
            broker.entry("Enter Short", "short")
