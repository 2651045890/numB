"""batch_011 port of 自适应双向EMA趋势交易系统与反向交易优化策略-Adaptive-Dual-Direction-EMA-Trend-Trading-System-with-Reverse-Trade-Optimization-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-02 00:00:00\nend: 2025-01-09 00:00:00\nperiod: 3m\nbasePeriod: 3m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SPX EMA Strategy with Opposite Trades", overlay=true)\n\n// User-defined inputs\ntradeIntervalMinutes = input.int(30, title="Main Trade Interval (in minutes)", minval=1)\noppositeTradeDelayMinutes = input.int(1, title="Opposite Trade time from next trade (in minutes)", minval=1) // Delay of opposite trade (1 min before the next trade)\nstartHour = input.int(10, title="Start Hour", minval=0, maxval=23)\nstartMinute = input.int(30, title="Start Minute", minval=0, maxval=59)\nstopHour = input.int(15, title="Stop Hour", minval=0, maxval=23)\nstopMinute = input.int(0, title="Stop Minute", minval=0, maxval=59)\n\n// User-defined EMA periods for main trade and opposite trade\nmainEmaShortPeriod = input.int(5, title="Main Trade EMA Short Period", minval=1)\nmainEmaLongPeriod = input.int(40, title="Main Trade EMA Long Period", minval=1)\noppositeEmaShortPeriod = input.int(5, title="Opposite Trade EMA Short Period", minval=1)\noppositeEmaLongPeriod = input.int(10, title="Opposite Trade EMA Long Period", minval=1)\n\n// Calculate the EMAs for main trade\nemaMainShort = ta.ema(close, mainEmaShortPeriod)\nemaMainLong = ta.ema(close, mainEmaLongPeriod)\n\n// Calculate the EMAs for opposite trade (using different periods)\nemaOppositeShort = ta.ema(close, oppositeEmaShortPeriod)\nemaOppositeLong = ta.ema(close, oppositeEmaLongPeriod)\n\n// Condition to check if it is during the user-defined time window\nstartTime = timestamp(year, month, dayofmonth, startHour, startMinute)\nstopTime = timestamp(year, month, dayofmonth, stopHour, stopMinute)\ncurrentTime = timestamp(year, month, dayofmonth, hour, minute)\n\n// Ensure the script only trades within the user-defined time window\nisTradingTime = currentTime >= startTime and currentTime <= stopTime\n\n// Time condition: Execute the trade every tradeIntervalMinutes\nvar float lastTradeTime = na\ntimePassed = na(lastTradeTime) or (currentTime - lastTradeTime) >= tradeIntervalMinutes * 60 * 1000\n\n// Entry Conditions for Main Trade\nlongCondition = emaMainShort > emaMainLong // Enter long if short EMA is greater than long EMA\nshortCondition = emaMainShort < emaMainLong // Enter short if short EMA is less than long EMA\n\n// Detect EMA crossovers for opposite trade (bullish or bearish)\nbullishCrossoverOpposite = ta.crossover(emaOppositeShort, emaOppositeLong)  // Opposite EMA short crosses above long\nbearishCrossoverOpposite = ta.crossunder(emaOppositeShort, emaOppositeLong) // Opposite EMA short crosses below long\n\n// Track the direction of the last main trade (true for long, false for short)\nvar bool isLastTradeLong = na\n// Track whether an opposite trade has already been executed after the last main trade\nvar bool oppositeTradeExecuted = false\n\n// Execute the main trades if within the time window and at the user-defined interval\nif isTradingTime and timePassed\n    if longCondition\n        strategy.entry("Main Long", strategy.long) \n        isLastTradeLong := true // Mark the last trade as long\n        oppositeTradeExecuted := false // Reset opposite trade status\n        lastTradeTime := currentTime\n       // label.new(bar_index, low, "Main Long", color=color.green, textcolor=color.white, size=size.small)\n    else if shortCondition\n        strategy.entry("Main Short", strategy.short) \n        isLastTradeLong := false // Mark the last trade as short\n        oppositeTradeExecuted := false // Reset opposite trade status\n        lastTradeTime := currentTime\n       // label.new(bar_index, high, "Main Short", color=color.red, textcolor=color.white, size=size.small)\n\n// Execute the opposite trade only once after the main trade\nif isTradingTime and not oppositeTradeExecuted\n    // 1 minute before the next main trade or EMA crossover\n    if (currentTime - lastTradeTime) >= (tradeIntervalMinutes - oppositeTradeDelayMinutes) * 60 * 1000 or bullishCrossoverOpposite or bearishCrossoverOpposite\n        if isLastTradeLong\n            // If the last main trade was long, enter opposite short trade\n            strategy.entry("Opposite Short", strategy.short) \n            //label.new(bar_index, high, "Opposite Short", color=color.red, textcolor=color.white, size=size.small)\n        else\n            // If the last main trade was short, enter opposite long trade\n            strategy.entry("Opposite Long", strategy.long) \n            //label.new(bar_index, low, "Opposite Long", color=color.green, textcolor=color.white, size=size.small)\n        \n        // After entering the opposite trade, set the flag to true so no further opposite trades are placed\n        oppositeTradeExecuted := true\n\n// Plot the EMAs for visual reference\nplot(emaMainShort, title="Main Trade Short EMA", color=color.blue)\nplot(emaMainLong, title="Main Trade Long EMA", color=color.red)\nplot(emaOppositeShort, title="Opposite Trade Short EMA", color=color.purple)\nplot(emaOppositeLong, title="Opposite Trade Long EMA", color=color.orange)\n\n'

class SM49479C88F8C5B400(PinePortBase, IStrategy):
    source_id = "SM_49479c88f8c5b400"
    source_file = '自适应双向EMA趋势交易系统与反向交易优化策略-Adaptive-Dual-Direction-EMA-Trend-Trading-System-with-Reverse-Trade-Optimization-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'tradeIntervalMinutes': 30, 'oppositeTradeDelayMinutes': 1, 'startHour': 10, 'startMinute': 30, 'stopHour': 15, 'stopMinute': 0, 'mainEmaShortPeriod': 5, 'mainEmaLongPeriod': 40, 'oppositeEmaShortPeriod': 5, 'oppositeEmaLongPeriod': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
