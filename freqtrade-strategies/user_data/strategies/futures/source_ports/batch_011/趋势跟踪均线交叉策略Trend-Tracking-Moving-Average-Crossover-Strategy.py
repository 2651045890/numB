"""batch_011 port of 趋势跟踪均线交叉策略Trend-Tracking-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n//Author @divonn1994\n\ninitial_balance = 100\nstrategy(title=\'Close v Open Moving Averages Strategy\', shorttitle = \'Close v Open\', overlay=true, pyramiding=0, default_qty_value=100, default_qty_type=strategy.percent_of_equity, precision=7, currency=currency.USD, commission_value=0.1, commission_type=strategy.commission.percent, initial_capital=initial_balance)\n\n//Input for number of bars for moving average, Switch to choose moving average type, Display Options and Time Frame of trading----------------------------------------------------------------\n\nbars = input.int(66, "Moving average length (number of bars)", minval=1, group=\'Strategy\') //66 bars and VWMA for BTCUSD on 12 Hours.. 35 bars and VWMA for BTCUSD on 1 Day\nstrategy = input.string("VWMA", "Moving Average type", options = ["EMA", "SMA", "RMA", "WMA", "VWMA"], group=\'Strategy\')\n\nredOn = input.string("On", "Red Background Color On/Off", options = ["On", "Off"], group=\'Display\')\ngreenOn = input.string("On", "Green Background Color On/Off", options = ["On", "Off"], group=\'Display\')\nmaOn = input.string("On", "Moving Average Plot On/Off", options = ["On", "Off"], group=\'Display\')\n\nstartMonth = input.int(title=\'Start Month 1-12 (set any start time to 0 for furthest date)\', defval=1, minval=0, maxval=12, group=\'Beginning of Strategy\')\nstartDate = input.int(title=\'Start Date 1-31 (set any start time to 0 for furthest date)\', defval=1, minval=0, maxval=31, group=\'Beginning of Strategy\')\nstartYear = input.int(title=\'Start Year 2000-2100 (set any start time to 0 for furthest date)\', defval=2011, minval=2000, maxval=2100, group=\'Beginning of Strategy\')\n\nendMonth = input.int(title=\'End Month 1-12 (set any end time to 0 for today\\\'s date)\', defval=0, minval=0, maxval=12, group=\'End of Strategy\')\nendDate = input.int(title=\'End Date 1-31 (set any end time to 0 for today\\\'s date)\', defval=0, minval=0, maxval=31, group=\'End of Strategy\')\nendYear = input.int(title=\'End Year 2000-2100 (set any end time to 0 for today\\\'s date)\', defval=0, minval=0, maxval=2100, group=\'End of Strategy\')\n\n//Strategy Calculations-----------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\ninDateRange = true\n\nmaMomentum = switch strategy\n    "EMA" => (ta.ema(close, bars) > ta.ema(open, bars)) ? 1 : -1\n    "SMA" => (ta.sma(close, bars) > ta.sma(open, bars)) ? 1 : -1\n    "RMA" => (ta.rma(close, bars) > ta.rma(open, bars)) ? 1 : -1\n    "WMA" => (ta.wma(close, bars) > ta.wma(open, bars)) ? 1 : -1\n    "VWMA" => (ta.vwma(close, bars) > ta.vwma(open, bars)) ? 1 : -1\n    =>\n        runtime.error("No matching MA type found.")\n        float(na)\n\nopenMA = switch strategy\n    "EMA" => ta.ema(open, bars)\n    "SMA" => ta.sma(open, bars)\n    "RMA" => ta.rma(open, bars)\n    "WMA" => ta.wma(open, bars)\n    "VWMA" => ta.vwma(open, bars)\n    =>\n        runtime.error("No matching MA type found.")\n        float(na)\n        \ncloseMA = switch strategy\n    "EMA" => ta.ema(close, bars)\n    "SMA" => ta.sma(close, bars)\n    "RMA" => ta.rma(close, bars)\n    "WMA" => ta.wma(close, bars)\n    "VWMA" => ta.vwma(close, bars)\n    =>\n        runtime.error("No matching MA type found.")\n        float(na)\n\n//Enter or Exit Positions--------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\nif ta.crossover(maMomentum, 0)\n    if inDateRange\n        strategy.entry(\'long\', strategy.long, comment=\'long\')\nif ta.crossunder(maMomentum, 0)\n    if inDateRange\n        strategy.close(\'long\')\n\n//Plot Strategy Behavior---------------------------------------------------------------------------------------------------------------------------------------------------------------------\n\nplot(series = maOn == "On" ? openMA : na, title = "Open moving Average", color = color.new(color.purple,0), linewidth=3, offset=1)\nplot(series = maOn == "On" ? closeMA : na, title = "Close Moving Average", color = color.new(color.white,0), linewidth=2, offset=1)\nbgcolor(color = inDateRange and (greenOn == "On") and maMomentum > 0 ? color.new(color.green,75) : inDateRange and (redOn == "On") and maMomentum <= 0 ? color.new(color.red,75) : na, offset=1)'

class SM6A6A2228E4064195(PinePortBase, IStrategy):
    source_id = "SM_6a6a2228e4064195"
    source_file = '趋势跟踪均线交叉策略Trend-Tracking-Moving-Average-Crossover-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'bars': 66, 'strategy': 'VWMA', 'redOn': 'On', 'greenOn': 'On', 'maOn': 'On', 'startMonth': 1, 'startDate': 1, 'startYear': 2011, 'endMonth': 0, 'endDate': 0, 'endYear': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'switch']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
