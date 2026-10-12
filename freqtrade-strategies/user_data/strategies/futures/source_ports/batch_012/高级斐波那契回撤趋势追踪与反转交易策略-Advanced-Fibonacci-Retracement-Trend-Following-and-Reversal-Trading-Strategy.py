"""batch_012 port of 高级斐波那契回撤趋势追踪与反转交易策略-Advanced-Fibonacci-Retracement-Trend-Following-and-Reversal-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-06 00:00:00\nend: 2025-01-05 00:00:00\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci Retracement Strategy for Crypto", overlay=true)\n\n// Input parameters\nlookback = input.int(50, title="Lookback Period", minval=1)\nplotLevels = input.bool(true, title="Plot Fibonacci Levels?")\ncompactLines = input.bool(true, title="Compact Fibonacci Lines?")\n\n// Calculate highest high and lowest low for the lookback period\nhighestHigh = ta.highest(high, lookback)\nlowestLow = ta.lowest(low, lookback)\n\n// Fibonacci retracement levels\ndiff = highestHigh - lowestLow\nlevel0 = highestHigh\nlevel23_6 = highestHigh - diff * 0.236\nlevel38_2 = highestHigh - diff * 0.382\nlevel50 = highestHigh - diff * 0.5\nlevel61_8 = highestHigh - diff * 0.618\nlevel78_6 = highestHigh - diff * 0.786\nlevel100 = lowestLow\n\n// Plot Fibonacci levels (compact mode to make lines shorter)\n// if plotLevels\n//     lineStyle = compactLines ? line.style_dashed : line.style_solid\n//     line.new(bar_index[lookback], level0, bar_index, level0, color=color.green, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level23_6, bar_index, level23_6, color=color.blue, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level38_2, bar_index, level38_2, color=color.blue, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level50, bar_index, level50, color=color.orange, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level61_8, bar_index, level61_8, color=color.red, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level78_6, bar_index, level78_6, color=color.red, width=1, style=lineStyle)\n//     line.new(bar_index[lookback], level100, bar_index, level100, color=color.green, width=1, style=lineStyle)\n\n// Long trade: Buy when price crosses above 61.8% retracement\nlongCondition = ta.crossover(close, level61_8)\nif longCondition\n    strategy.entry("Long", strategy.long, alert_message="Price bounced off Fibonacci level - Enter Long")\n\n// Short trade: Sell when price crosses below 38.2% retracement\nshortCondition = ta.crossunder(close, level38_2)\nif shortCondition\n    strategy.entry("Short", strategy.short, alert_message="Price crossed below Fibonacci level - Enter Short")\n\n// Exit conditions\nexitLong = close >= level23_6\nif exitLong\n    strategy.close("Long", alert_message="Price reached 23.6% Fibonacci level - Exit Long")\n\nexitShort = close <= level78_6\nif exitShort\n    strategy.close("Short", alert_message="Price reached 78.6% Fibonacci level - Exit Short")\n\n'

class SMAdvancedFibonacciRetracementTrendFollowingandReversalTrc52ba0(PinePortBase, IStrategy):
    source_id = "SM_c52ba0df64795cc9"
    source_file = '高级斐波那契回撤趋势追踪与反转交易策略-Advanced-Fibonacci-Retracement-Trend-Following-and-Reversal-Trading-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'lookback': 50, 'plotLevels': True, 'compactLines': True}
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
