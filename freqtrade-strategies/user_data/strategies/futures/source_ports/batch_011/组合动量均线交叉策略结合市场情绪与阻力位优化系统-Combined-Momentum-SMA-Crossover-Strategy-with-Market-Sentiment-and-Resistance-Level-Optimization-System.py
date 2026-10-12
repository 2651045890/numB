"""batch_011 port of 组合动量均线交叉策略结合市场情绪与阻力位优化系统-Combined-Momentum-SMA-Crossover-Strategy-with-Market-Sentiment-and-Resistance-Level-Optimization-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("XAUUSD SMA with MACD & Market Sentiment (Enhanced RR)", overlay=true)\n\n// Input parameters for moving averages\nshortSMA_length = input.int(10, title="Short SMA Length", minval=1)\nlongSMA_length = input.int(30, title="Long SMA Length", minval=1)\n\n// MACD settings\n[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)\n\n// Lookback period for identifying major resistance (swing highs)\nresistance_lookback = input.int(20, title="Resistance Lookback Period", tooltip="Lookback period for identifying major resistance")\n\n// Calculate significant resistance (local swing highs over the lookback period)\nmajor_resistance = ta.highest(close, resistance_lookback)\n\n// Calculate SMAs\nshortSMA = ta.sma(close, shortSMA_length)\nlongSMA = ta.sma(close, longSMA_length)\n\n// RSI for market sentiment\nrsiLength = input.int(14, title="RSI Length", minval=1)\nrsiOverbought = input.int(70, title="RSI Overbought Level", minval=50, maxval=100)\nrsiOversold = input.int(30, title="RSI Oversold Level", minval=0, maxval=50)\nrsi = ta.rsi(close, rsiLength)\n\n// Define buy condition based on SMA and MACD\nbuyCondition = ta.crossover(shortSMA, longSMA) and macdLine > signalLine\n\n// Define sell condition: only sell if price is at or above the identified major resistance\nsellCondition = close >= major_resistance and macdLine < signalLine\n\n// Define sentiment-based exit conditions\ncloseEarlyCondition = strategy.position_size < 0 and rsi > rsiOverbought  // Close losing trade early if RSI is overbought\nholdWinningCondition = strategy.position_size > 0 and rsi < rsiOversold   // Hold winning trade if RSI is oversold\n\n// Execute strategy: Enter long position when buy conditions are met\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\n// Close the position when the sell condition is met (price at resistance)\nif (sellCondition and not holdWinningCondition)\n    strategy.close("Buy")\n\n// Close losing trades early if sentiment is against us\nif (closeEarlyCondition)\n    strategy.close("Buy")\n\n// Visual cues for buy and sell signals\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sellCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Add alert for buy condition\nalertcondition(buyCondition, title="Buy Signal Activated", message="Buy signal activated: Short SMA has crossed above Long SMA and MACD is bullish.")\n\n// Add alert for sell condition to notify when price hits major resistance\nalertcondition(sellCondition, title="Sell at Major Resistance", message="Sell triggered at major resistance level.")\n\n// Add alert for early close condition (for losing trades)\nalertcondition(closeEarlyCondition, title="Close Losing Trade Early", message="Sentiment is against your position, close trade.")\n\n// Add alert for holding winning condition (optional)\nalertcondition(holdWinningCondition, title="Hold Winning Trade", message="RSI indicates oversold conditions, holding winning trade.")\n'

class SMB176E58A4DE5C22D(PinePortBase, IStrategy):
    source_id = "SM_b176e58a4de5c22d"
    source_file = '组合动量均线交叉策略结合市场情绪与阻力位优化系统-Combined-Momentum-SMA-Crossover-Strategy-with-Market-Sentiment-and-Resistance-Level-Optimization-System.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'shortSMA_length': 10, 'longSMA_length': 30, 'resistance_lookback': 20, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
