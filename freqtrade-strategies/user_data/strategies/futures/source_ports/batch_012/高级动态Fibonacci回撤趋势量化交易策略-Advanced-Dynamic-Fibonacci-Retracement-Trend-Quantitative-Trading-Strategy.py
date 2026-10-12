"""batch_012 port of 高级动态Fibonacci回撤趋势量化交易策略-Advanced-Dynamic-Fibonacci-Retracement-Trend-Quantitative-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-11 00:00:00\nend: 2024-12-10 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci Retracement Strategy", overlay=true)\n\n// Inputs\nlookback_period = input.int(100, title="Lookback Period")\nlevel_1 = input.float(0.236, title="Fibonacci Level 1")\nlevel_2 = input.float(0.382, title="Fibonacci Level 2")\nlevel_3 = input.float(0.5, title="Fibonacci Level 3")\nlevel_4 = input.float(0.618, title="Fibonacci Level 4")\nlevel_5 = input.float(0.786, title="Fibonacci Level 5")\n\n// Calculate highest high and lowest low over the lookback period\nhigh_level = ta.highest(high, lookback_period)\nlow_level = ta.lowest(low, lookback_period)\n\n// Calculate Fibonacci retracement levels\nfib_236 = low_level + (high_level - low_level) * level_1\nfib_382 = low_level + (high_level - low_level) * level_2\nfib_50 = low_level + (high_level - low_level) * level_3\nfib_618 = low_level + (high_level - low_level) * level_4\nfib_786 = low_level + (high_level - low_level) * level_5\n\n// Plot Fibonacci levels on the chart\nplot(fib_236, color=color.green, title="Fib 23.6%")\nplot(fib_382, color=color.blue, title="Fib 38.2%")\nplot(fib_50, color=color.orange, title="Fib 50%")\nplot(fib_618, color=color.red, title="Fib 61.8%")\nplot(fib_786, color=color.purple, title="Fib 78.6%")\n\n// Entry and Exit Conditions\nbuy_signal = ta.crossover(close, fib_618)\nsell_signal = ta.crossunder(close, fib_382)\n\n// Strategy Orders\nif buy_signal\n    strategy.entry("Buy", strategy.long)\n\n// Exit based on stop-loss and take-profit conditions\ntake_profit = high_level // Exit at the highest Fibonacci level (100%)\nstop_loss = low_level    // Exit at the lowest Fibonacci level (0%)\n\nstrategy.exit("Sell", from_entry="Buy", limit=take_profit, stop=stop_loss)\n\n// Visualization of Signals\nplotshape(series=buy_signal, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sell_signal, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n\n'

class SMFibonacciAdvancedDynamicFibonacciRetracementTrendQuanti845878(PinePortBase, IStrategy):
    source_id = "SM_845878b520dba396"
    source_file = '高级动态Fibonacci回撤趋势量化交易策略-Advanced-Dynamic-Fibonacci-Retracement-Trend-Quantitative-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'lookback_period': 100, 'level_1': 0.236, 'level_2': 0.382, 'level_3': 0.5, 'level_4': 0.618, 'level_5': 0.786}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
