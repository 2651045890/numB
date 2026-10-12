"""batch_011 port of 趋势过滤Pin-Bar反转策略-Trend-Filtered-Pin-Bar-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-01 00:00:00\nend: 2024-05-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Filtered Pin Bar Strategy with Relaxed Volume", overlay=true)\n\n// Define the size of the pin bar\'s wick and body\nwickSize = 0.6\nbodySize = 0.3\n\n// Calculate the size of the wicks and body\nupperWick = high - math.max(open, close)\nlowerWick = math.min(open, close) - low\nbody = math.abs(close - open)\n\n// Define a simple moving average to determine the trend\nsmaLength = 50\nsma = ta.sma(close, smaLength)\n\n// Define a more relaxed volume threshold\nvolumeThreshold = ta.sma(volume, 20) * 1.0\n\n// Define RSI parameters\nrsiLength = 14\nrsiOverbought = 70\nrsiOversold = 30\nrsi = ta.rsi(close, rsiLength)\n\n// Define the conditions for a bullish pin bar\nbullishPinBar = (lowerWick > (wickSize * (high - low))) and\n     (body < (bodySize * (high - low))) and\n     (close > open) and\n     (close > sma) and\n     (volume > volumeThreshold)\n\n// Define the conditions for a bearish pin bar\nbearishPinBar = (upperWick > (wickSize * (high - low))) and\n     (body < (bodySize * (high - low))) and\n     (close < open) and\n     (close < sma) and\n     (volume > volumeThreshold)\n\n// Plot the bullish and bearish pin bars on the chart\nplotshape(series=bullishPinBar, title="Bullish Pin Bar", location=location.belowbar, color=color.green, style=shape.labelup, text="PB")\nplotshape(series=bearishPinBar, title="Bearish Pin Bar", location=location.abovebar, color=color.red, style=shape.labeldown, text="PB")\n\n// Entry and exit rules\nif (bullishPinBar)\n    strategy.entry("Bullish Pin Bar", strategy.long)\nif (bearishPinBar)\n    strategy.entry("Bearish Pin Bar", strategy.short)\n\n// Optional: Set stop loss and take profit\nstopLoss = 2 * body\ntakeProfit = 3 * body\nstrategy.exit("Exit Long", from_entry="Bullish Pin Bar", stop=low - stopLoss, limit=high + takeProfit)\nstrategy.exit("Exit Short", from_entry="Bearish Pin Bar", stop=high + stopLoss, limit=low - takeProfit)\n'

class SM29B10D84B22AE93B(PinePortBase, IStrategy):
    source_id = "SM_29b10d84b22ae93b"
    source_file = '趋势过滤Pin-Bar反转策略-Trend-Filtered-Pin-Bar-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
