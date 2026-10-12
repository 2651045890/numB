"""batch_012 port of 黄金复合移动平均线交叉RSI混入策略Gold-Trading-with-Simons-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Gold Trading with Simons Strategy", overlay=true)\n\n// Parameters\nlength21 = input(21, minval=1, title="Length for 21 MA")\nlength50 = input(50, minval=1, title="Length for 50 MA")\nlength200 = input(200, minval=1, title="Length for 200 MA")\nrsiLength = input(14, minval=1, title="RSI Length")\nrsiOverbought = input(70, title="RSI Overbought Level")\nrsiOversold = input(30, title="RSI Oversold Level")\ntakeProfitPercent = input(4, title="Take Profit %")\nstopLossPercent = input(1, title="Stop Loss %")\n\n// Moving Averages\nma21 = sma(close, length21)\nma50 = sma(close, length50)\nma200 = sma(close, length200)\n\n// RSI\nrsi = rsi(close, rsiLength)\n\n// Engulfing Pattern\nisBullishCandle(c) => close[c] > open[c]\nisBearishCandle(c) => close[c] < open[c]\n\nbearishEngulfing = isBullishCandle(1) and isBearishCandle(0) and close < open[1] and open > close[1]\nbullishEngulfing = isBearishCandle(1) and isBullishCandle(0) and close > open[1] and open < close[1]\n\n// Calculate Take Profit and Stop Loss Levels\ntakeProfitLevel(entryPrice) => entryPrice * (1 + takeProfitPercent / 100)\nstopLossLevel(entryPrice) => entryPrice * (1 - stopLossPercent / 100)\n\n// Entry Conditions\nlongCondition = crossover(ma21, ma200) and close > ma21 and close > ma50 and rsi < rsiOverbought and bullishEngulfing\nshortCondition = crossunder(ma21, ma200) and close < ma21 and close < ma50 and rsi > rsiOversold and bearishEngulfing\n\n// Entry\nif (longCondition)\n    entryPrice = close\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit", "Long", limit=takeProfitLevel(entryPrice))\n    strategy.exit("Stop Loss", "Long", stop=stopLossLevel(entryPrice))\nif (shortCondition)\n    entryPrice = close\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit", "Short", limit=takeProfitLevel(entryPrice))\n    strategy.exit("Stop Loss", "Short", stop=stopLossLevel(entryPrice))\n\n// Plotting\nplot(ma21, color=color.blue, title="21 MA")\nplot(ma50, color=color.orange, title="50 MA")\nplot(ma200, color=color.red, title="200 MA")\nhline(rsiOverbought, "RSI Overbought", color=color.green)\nhline(rsiOversold, "RSI Oversold", color=color.red)\nplot(rsi, "RSI", color=color.purple)\n'

class SMRSIGoldTradingwithSimonsStrategya09bf2(PinePortBase, IStrategy):
    source_id = "SM_a09bf297a96796d3"
    source_file = '黄金复合移动平均线交叉RSI混入策略Gold-Trading-with-Simons-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'length21': 21, 'length50': 50, 'length200': 200, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30, 'takeProfitPercent': 4, 'stopLossPercent': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
