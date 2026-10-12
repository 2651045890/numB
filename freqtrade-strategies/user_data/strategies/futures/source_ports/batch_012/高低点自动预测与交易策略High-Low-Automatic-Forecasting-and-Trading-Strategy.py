"""batch_012 port of 高低点自动预测与交易策略High-Low-Automatic-Forecasting-and-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("9:15 AM High/Low with Automatic Forecasting", overlay=true)\n\n// Parameters\nshowSignals = input(true, title="Show Signals")\n\n// Define session time\nsessionStartHour = input(9, title="Session Start Hour")\nsessionStartMinute = input(0, title="Session Start Minute")\nsessionEndHour = input(9, title="Session End Hour")\nsessionEndMinute = input(15, title="Session End Minute")\n\n// Calculate session high and low\nvar float sessionHigh = na\nvar float sessionLow = na\nif (hour == sessionStartHour and minute == sessionStartMinute)\n    sessionHigh := high\n    sessionLow := low\n\n// Update session high and low if within session time\nif (hour == sessionStartHour and minute >= sessionStartMinute and minute < sessionEndMinute)\n    sessionHigh := high > sessionHigh or na(sessionHigh) ? high : sessionHigh\n    sessionLow := low < sessionLow or na(sessionLow) ? low : sessionLow\n\n// Plot horizontal lines for session high and low\nplot(sessionHigh, color=color.green, title="9:00 AM High", style=plot.style_stepline, linewidth=1)\nplot(sessionLow, color=color.red, title="9:00 AM Low", style=plot.style_stepline, linewidth=1)\n\n// Calculate targets and stop loss\nlongTarget = sessionHigh + 200\nlongStopLoss = sessionLow\nshortTarget = sessionLow - 200\nshortStopLoss = sessionHigh\n\n// Plot targets and stop loss\nplot(longTarget, color=color.blue, title="Long Target", style=plot.style_cross, linewidth=1)\nplot(longStopLoss, color=color.red, title="Long Stop Loss", style=plot.style_cross, linewidth=1)\nplot(shortTarget, color=color.blue, title="Short Target", style=plot.style_cross, linewidth=1)\nplot(shortStopLoss, color=color.red, title="Short Stop Loss", style=plot.style_cross, linewidth=1)\n\n// RSI\nrsiLength = input(14, title="RSI Length")\noverboughtLevel = input(60, title="Overbought Level")\noversoldLevel = input(40, title="Oversold Level")\nrsi = ta.rsi(close, rsiLength)\n\n// Entry conditions\nlongCondition = close > sessionHigh and rsi > overboughtLevel\nshortCondition = close < sessionLow and rsi < oversoldLevel\n\n// Long entry\nif (showSignals and longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short entry\nif (showSignals and shortCondition)\n    strategy.entry("Short", strategy.short)\n\n'

class SMHighLowAutomaticForecastingandTradingStrategy3683cb(PinePortBase, IStrategy):
    source_id = "SM_3683cb7ebb061f51"
    source_file = '高低点自动预测与交易策略High-Low-Automatic-Forecasting-and-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'showSignals': True, 'sessionStartHour': 9, 'sessionStartMinute': 0, 'sessionEndHour': 9, 'sessionEndMinute': 15, 'rsiLength': 14, 'overboughtLevel': 60, 'oversoldLevel': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
