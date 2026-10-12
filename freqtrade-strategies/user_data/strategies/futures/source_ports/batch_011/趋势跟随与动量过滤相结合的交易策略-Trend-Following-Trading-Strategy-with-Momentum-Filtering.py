"""batch_011 port of 趋势跟随与动量过滤相结合的交易策略-Trend-Following-Trading-Strategy-with-Momentum-Filtering.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-05-28 00:00:00\nend: 2024-06-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Trend-Following Strategy with MACD and RSI Filter", overlay=true)\n\n// Input variables\nfastLength = input(12, title="Fast MA Length")\nslowLength = input(26, title="Slow MA Length")\nsignalLength = input(9, title="Signal Line Length")\nstopLossPct = input(1.0, title="Stop Loss %") / 100\nrsiLength = input(14, title="RSI Length")\nrsiThreshold = input(50, title="RSI Threshold")\n\n// Moving averages\nfastMA = ta.sma(close, fastLength)\nslowMA = ta.sma(close, slowLength)\n\n// MACD\n[macdLine, signalLine, _] = ta.macd(close, fastLength, slowLength, signalLength)\n\n// RSI\nrsi = ta.rsi(close, rsiLength)\n\n// Entry conditions with RSI filter\nbullishSignal = ta.crossover(macdLine, signalLine) and rsi > rsiThreshold\nbearishSignal = ta.crossunder(macdLine, signalLine) and rsi < rsiThreshold\n\n// Calculate stop loss levels\nlongStopLoss = ta.highest(close, 10)[1] * (1 - stopLossPct)\nshortStopLoss = ta.lowest(close, 10)[1] * (1 + stopLossPct)\n\n// Execute trades\nstrategy.entry("Long", strategy.long, when=bullishSignal)\nstrategy.entry("Short", strategy.short, when=bearishSignal)\nstrategy.exit("Exit Long", "Long", stop=longStopLoss)\nstrategy.exit("Exit Short", "Short", stop=shortStopLoss)\n\n// Plotting signals\nplotshape(bullishSignal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title="Bullish Signal")\nplotshape(bearishSignal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title="Bearish Signal")\n\n// Plot MACD\nplot(macdLine, color=color.blue, title="MACD Line")\nplot(signalLine, color=color.orange, title="Signal Line")\n\n// Plot RSI\nhline(rsiThreshold, "RSI Threshold", color=color.gray)\nplot(rsi, color=color.purple, title="RSI")\n\n'

class SM1BB37DB5C115C62E(PinePortBase, IStrategy):
    source_id = "SM_1bb37db5c115c62e"
    source_file = '趋势跟随与动量过滤相结合的交易策略-Trend-Following-Trading-Strategy-with-Momentum-Filtering.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9, 'stopLossPct': 1.0, 'rsiLength': 14, 'rsiThreshold': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
