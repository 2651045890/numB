"""batch_011 port of 移动平均线聚合MACD策略Moving-Average-Aggregation-MACD-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '//@version=2\nstrategy(title="MACD Multi-MA Strategy", overlay=false )\n\nsrc = close \nlen1 = input(8, "FAST LOOKBACK") \nlen2 = input(144, "SLOW LOOKBACK")\n\n/////////////////////////////////////////////\nlength = len2-len1\nma = vwma(src, length)\nplot(ma, title="VWMA", color=lime)\n\n\nlength1 = len2-len1\nma1 = rma(src, length1)\nplot(ma1, title="RMA", color=purple)\n\nlength2 = len2-len1\nma2 = sma(src, length2)\nplot(ma2, title="SMA", color=red)\n\n\nlength3 = len2-len1\nma3 = wma(src, length3)\nplot(ma3, title="WMA", color=orange)\n\nlength4 = len2-len1\nma4 = ema(src, length4)\nplot(ma4, title="EMA", color=yellow)\n\n\n\n\n\nlong = ma > ma[1] and ma1 > ma1[1] and ma2 > ma2[1] and ma3 > ma3[1] and ma4 > ma4[1]\nshort = ma < ma[1] and ma1 < ma1[1] and ma2 < ma2[1] and ma3 < ma3[1] and ma4 < ma4[1]\n\n\nstrategy.entry("Long", strategy.long, when=long)\nstrategy.entry("Short", strategy.short, when=short)\n\n'

class SM1563665459E3B724(PinePortBase, IStrategy):
    source_id = "SM_1563665459e3b724"
    source_file = '移动平均线聚合MACD策略Moving-Average-Aggregation-MACD-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'len1': 8, 'len2': 144}
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
