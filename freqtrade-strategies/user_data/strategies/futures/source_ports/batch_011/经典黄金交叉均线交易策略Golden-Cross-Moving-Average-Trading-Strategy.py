"""batch_011 port of 经典黄金交叉均线交易策略Golden-Cross-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-03 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © CJDeegan\n\n//@version=4\nstrategy(title = "[LIVE] Golden Cross", overlay=true)\n\n// ------------Functions------------\n\n//Percent to Decimal Conversion\nperToDec(a) => a * 0.01\n//Price Difference to Tick\ndiffToTick(a,b) => (a - b) / syminfo.mintick \n\n    \n// ------------Strategy Inputs------------\ntakeProfitInput = input(300, "Take Profit Price (% Gain)")\nstopLossInput = input(25, "Stop Loss (% Loss)")\n\n\nstartDate = input(title="Start Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nstartMonth = input(title="Start Month", type=input.integer,\n     defval=1, minval=1, maxval=12)\nstartYear = input(title="Start Year", type=input.integer,\n     defval=2018, minval=1800, maxval=2100)\n\nendDate = input(title="End Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nendMonth = input(title="End Month", type=input.integer,\n     defval=1, minval=1, maxval=12)\nendYear = input(title="End Year", type=input.integer,\n     defval=2031, minval=1800, maxval=2100)\n\ninDateRange = (time >= timestamp(syminfo.timezone, startYear,\n         startMonth, startDate, 0, 0)) and\n     (time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0))\n     \n\n// ------------Populate Indicators------------\n\n//EMA\nsma50 = sma(close,50)\nsma100 = sma(close,100)\nsma200 = sma(close,200)\n\n\n// ------------Entry Logic------------\n//Guards\nentryGuard = true\n//Triggers\nentryTrigger = crossover(sma50,sma100)\n//Conditions\nentryCondition = entryGuard and entryTrigger\n//Calculations\n//Execution\nif (inDateRange and entryCondition)\n    strategy.entry("Long", strategy.long, when = entryCondition, comment = "Entry")\n\n//------------Exit Logic------------\n\n//Guards\n//Triggers\nexitTrigger = crossunder(sma50,sma100) or close < sma100 or crossunder(sma100,sma200)\n//Conditions\nexitCondition = exitTrigger\n\n//Calculations\n//Take Profit\ntakeProfitPrice = strategy.position_avg_price + (strategy.position_avg_price * perToDec(takeProfitInput))\n//Take Profit Ticks\ntakeProfitTicks = diffToTick(takeProfitPrice, strategy.position_avg_price)\n//StopLoss\nstopLossPrice = strategy.position_avg_price - (strategy.position_avg_price * perToDec(stopLossInput))\n\n//Execution\nif (inDateRange)\n    strategy.close("Long", when = exitCondition, comment = "Sell Trigger")\n    strategy.exit("Exit", "Long", comment="Stop", profit=takeProfitTicks, stop=stopLossPrice)\n\n//Plots\nplot(sma50, "SMA 50", color = color.blue)\nplot(sma100, "SMA 100", color = color.green)\nplot(sma200, "SMA 200", color = color.yellow)\nentry = plot(strategy.position_size <= 0 ? na : strategy.position_avg_price, "Entry Price", color = color.yellow, style = plot.style_linebr)\nprofit = plot(strategy.position_size <= 0 ? na : takeProfitPrice, "Take Profit (Price)", color = color.green, style = plot.style_linebr)\nstop = plot(strategy.position_size <= 0 ? na : stopLossPrice, "Stop Loss", color = color.red, style = plot.style_linebr)\nfill(entry,profit, color=color.green)\nfill(entry,stop, color=color.red)\n'

class SMFB1888552E2A7057(PinePortBase, IStrategy):
    source_id = "SM_fb1888552e2a7057"
    source_file = '经典黄金交叉均线交易策略Golden-Cross-Moving-Average-Trading-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'takeProfitInput': 300, 'stopLossInput': 25, 'startDate': 1, 'startMonth': 1, 'startYear': 2018, 'endDate': 1, 'endMonth': 1, 'endYear': 2031}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
