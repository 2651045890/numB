"""batch_012 port of 高频混合技术分析量化策略-High-Frequency-Hybrid-Technical-Analysis-Quantitative-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-26 00:00:00\nend: 2024-12-03 00:00:00\nperiod: 15m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("BTC Scalping Strategy with Risk-Reward 1:3", overlay=true)\n\n// Heiken Ashi Candle Calculation\nvar float haOpen = na\nhaClose = (open + high + low + close) / 4\nhaOpen := na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2\nhaHigh = math.max(high, math.max(haOpen, haClose))\nhaLow = math.min(low, math.min(haOpen, haClose))\n\n// Plot Heiken Ashi Candles\nplotcandle(haOpen, haHigh, haLow, haClose, color=haClose >= haOpen ? color.green : color.red)\n\n// Bollinger Bands Calculation\nlengthBB = 20\nsrc = close\nmult = 2.0\nbasis = ta.sma(src, lengthBB)\ndev = mult * ta.stdev(src, lengthBB)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// Stochastic RSI Calculation (fixed parameters)\nkLength = 14\ndSmoothing = 3\nstochRSI = ta.stoch(close, high, low, kLength)\n\n// Average True Range (ATR) for stop loss and take profit\natrLength = 14\natrValue = ta.atr(atrLength)\n\n// Entry conditions\nlongCondition = ta.crossover(close, lowerBB) and stochRSI < 20\nshortCondition = ta.crossunder(close, upperBB) and stochRSI > 80\n\n// Alerts and trade signals\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit", "Long", profit=atrValue*3, loss=atrValue)\n    alert("Buy Signal Triggered", alert.freq_once_per_bar_close)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit", "Short", profit=atrValue*3, loss=atrValue)\n    alert("Sell Signal Triggered", alert.freq_once_per_bar_close)\n\n'

class SMHighFrequencyHybridTechnicalAnalysisQuantitativeStrategb05a1f(PinePortBase, IStrategy):
    source_id = "SM_b05a1f951629352b"
    source_file = '高频混合技术分析量化策略-High-Frequency-Hybrid-Technical-Analysis-Quantitative-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {}
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
