"""batch_012 port of 高级斐波那契回调与成交量加权价格行为交易策略-Advanced-Fibonacci-Retracement-and-Volume-Weighted-Price-Action-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-29 00:00:00\nend: 2024-07-29 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci and Price Action with Volume Strategy", overlay=true)\n\n// Inputs for Fibonacci levels\nfibLength = input.int(20, title="Fibonacci Length")\nfibonacciLevels = array.new_float(5, 0)\nvar float fibHigh = na\nvar float fibLow = na\n\n// Inputs for Volume\nvolumeMA_length = input.int(20, title="Volume MA Length")  // Moving average length for volume\nvolumeThreshold = input.float(1.5, title="Volume Threshold Multiplier")  // Multiplier for volume condition\n\n// Calculate Fibonacci retracement levels\nif (na(fibHigh) or na(fibLow))\n    fibHigh := high\n    fibLow := low\n\nif (high > fibHigh)\n    fibHigh := high\nif (low < fibLow)\n    fibLow := low\n\nif (bar_index % fibLength == 0)\n    fibHigh := high\n    fibLow := low\n    array.set(fibonacciLevels, 0, fibHigh)\n    array.set(fibonacciLevels, 1, fibHigh - 0.236 * (fibHigh - fibLow))\n    array.set(fibonacciLevels, 2, fibHigh - 0.382 * (fibHigh - fibLow))\n    array.set(fibonacciLevels, 3, fibHigh - 0.618 * (fibHigh - fibLow))\n    array.set(fibonacciLevels, 4, fibLow)\n\n// Plot Fibonacci levels\nplot(array.get(fibonacciLevels, 0), color=color.gray, linewidth=1, title="Fib 0%")\nplot(array.get(fibonacciLevels, 1), color=color.gray, linewidth=1, title="Fib 23.6%")\nplot(array.get(fibonacciLevels, 2), color=color.gray, linewidth=1, title="Fib 38.2%")\nplot(array.get(fibonacciLevels, 3), color=color.gray, linewidth=1, title="Fib 61.8%")\nplot(array.get(fibonacciLevels, 4), color=color.gray, linewidth=1, title="Fib 100%")\n\n// Price Action Patterns\nisPinBar(bullish) =>\n    wickSize = bullish ? high - math.max(open, close) : math.min(open, close) - low\n    bodySize = math.abs(close - open)\n    wickSize > bodySize * 2\n\nisBullishEngulfing() =>\n    open[1] > close[1] and close > open and open <= close[1] and close >= open[1]\n\nisBearishEngulfing() =>\n    close[1] > open[1] and open > close and open >= close[1] and close <= open[1]\n\n// Calculate Volume Moving Average\nvolumeMA = ta.sma(volume, volumeMA_length)\nvolumeCondition = volume > volumeThreshold * volumeMA\n\n// Buy and Sell Conditions with Volume\nlongEntry = (isPinBar(true) or isBullishEngulfing()) and close > array.get(fibonacciLevels, 2) and volumeCondition\nshortEntry = (isPinBar(false) or isBearishEngulfing()) and close < array.get(fibonacciLevels, 2) and volumeCondition\n\n// Execute Trades\nif (longEntry)\n    strategy.entry("Buy", strategy.long)\n\nif (shortEntry)\n    strategy.entry("Sell", strategy.short)\n\n// Plot buy and sell signals\nplotshape(series=longEntry, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(series=shortEntry, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n\n// Plot Volume MA\nplot(volumeMA, title="Volume MA", color=color.orange, linewidth=1, style=plot.style_line)\n\n// Plot Performance Metrics\n// if (strategy.closedtrades > 0)\n//     winRate = (strategy.wintrades / strategy.closedtrades) * 100\n//     profitFactor = strategy.grossprofit / strategy.grossloss\n//     label.new(bar_index, high, "Win Rate: " + str.tostring(winRate, "#.##") + "%\\nProfit Factor: " + str.tostring(profitFactor, "#.##"), \n//               color=color.new(color.blue, 80), style=label.style_label_down, size=size.small)\n'

class SMAdvancedFibonacciRetracementandVolumeWeightedPriceActioad7f4f(PinePortBase, IStrategy):
    source_id = "SM_ad7f4fa066e2aec5"
    source_file = '高级斐波那契回调与成交量加权价格行为交易策略-Advanced-Fibonacci-Retracement-and-Volume-Weighted-Price-Action-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fibLength': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Array/matrix operations are present and are not parity-certified by the generic adapter.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
