"""batch_011 port of 移动布林线策略-Modified-Bollinger-Bands-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Modified Bollinger Bands Strategy", shorttitle="Mod BB Strategy", overlay=true)\n\n// Input parameters for Bollinger Bands\nlength = input.int(20, minval=1, title="BB Length")\nmult = input.float(2.0, minval=0.001, maxval=50, title="BB StdDev")\n\n// Input parameters for moving average\nmaLength = input.int(50, minval=1, title="MA Length")\n\n// Input parameters for Stochastic RSI\nkLength = input.int(14, title="Stoch RSI K Length")\ndLength = input.int(3, title="Stoch RSI D Length")\nrsiLength = input.int(14, title="Stoch RSI Length")\noversold = input.float(20, title="Stoch RSI Oversold Level")\n\n// Calculate Bollinger Bands\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// Calculate Moving Average\nmovingAvg = ta.sma(close, maLength)\n\n// Calculate Stochastic RSI\nrsi = ta.rsi(close, rsiLength)\nk = ta.sma(ta.stoch(rsi, rsi, rsi, kLength), dLength)\nd = ta.sma(k, dLength)\n\n// Define buy and sell conditions\nlongCondition = close < lowerBB and close > movingAvg and k < oversold\nexitCondition = close > upperBB\n\n// Plotting\nplot(basis, "Basis", color=color.new(#FF6D00, 0))\nplot(upperBB, "Upper", color=color.new(#2962FF, 0))\nplot(lowerBB, "Lower", color=color.new(#2962FF, 0))\nplot(movingAvg, "Moving Average", color=color.new(#FFFF00, 0))\n\n// Execute strategy\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\nif (exitCondition)\n    strategy.close("Buy")\n'

class SM3D2D39BF104E919B(PinePortBase, IStrategy):
    source_id = "SM_3d2d39bf104e919b"
    source_file = '移动布林线策略-Modified-Bollinger-Bands-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'length': 20, 'mult': 2.0, 'maLength': 50, 'kLength': 14, 'dLength': 3, 'rsiLength': 14, 'oversold': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
