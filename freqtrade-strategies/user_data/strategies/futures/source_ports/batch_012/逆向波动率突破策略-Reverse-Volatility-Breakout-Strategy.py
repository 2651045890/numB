"""batch_012 port of 逆向波动率突破策略-Reverse-Volatility-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Volatility Breakout Strategy (Reversed)", overlay=true)\n\n// Indicator Inputs\natrLength = input(14, "ATR Length")\nbbLength = input(20, "Bollinger Bands Length")\nbbMultiplier = input(2, "Bollinger Bands Multiplier")\nrsiLength = input(14, "RSI Length")\nmacdShortLength = input(12, "MACD Short Length")\nmacdLongLength = input(26, "MACD Long Length")\nmacdSignalSmoothing = input(9, "MACD Signal Smoothing")\n\n// Calculate Indicators\natrValue = ta.atr(atrLength)\nbasis = ta.sma(close, bbLength)\ndeviation = bbMultiplier * ta.stdev(close, bbLength)\nupperBand = basis + deviation\nlowerBand = basis - deviation\nrsiValue = ta.rsi(close, rsiLength)\n[macdLine, signalLine, _] = ta.macd(close, macdShortLength, macdLongLength, macdSignalSmoothing)\n\n// Strategy Conditions (Reversed)\nlongCondition = ta.crossover(close[1], upperBand[1]) and rsiValue > 50 and macdLine > signalLine\nshortCondition = ta.crossunder(close[1], lowerBand[1]) and rsiValue < 50 and macdLine < signalLine\n\n// Strategy Entry (Reversed)\nif (longCondition)\n    strategy.entry("Sell", strategy.short)  // Reversed: Buy signal triggers a sell\nif (shortCondition)\n    strategy.entry("Buy", strategy.long)  // Reversed: Sell signal triggers a buy\n\n// Plotting\nplot(basis, color=color.blue, title="Basis")\nplot(upperBand, color=color.red, title="Upper Band")\nplot(lowerBand, color=color.green, title="Lower Band")\n\n'

class SMReverseVolatilityBreakoutStrategy298d81(PinePortBase, IStrategy):
    source_id = "SM_298d8165aa165a58"
    source_file = '逆向波动率突破策略-Reverse-Volatility-Breakout-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'atrLength': 14, 'bbLength': 20, 'bbMultiplier': 2, 'rsiLength': 14, 'macdShortLength': 12, 'macdLongLength': 26, 'macdSignalSmoothing': 9}
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
