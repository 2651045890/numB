"""batch_011 port of 聚合动量指标策略Chaikin-Oscillator-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-11 00:00:00\nend: 2023-10-11 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 18/09/2017\n//    Indicator plots Money Flow Indicator (Chaikin). This indicator looks \n//    to improve on Larry William\'s Accumulation Distribution formula that \n//    compared the closing price with the opening price. In the early 1970\'s, \n//    opening prices for stocks stopped being transmitted by the exchanges. \n//    This made it difficult to calculate Williams\' formula. The Chaikin \n//    Oscillator uses the average price of the bar calculated as follows \n//    (High + Low) /2 instead of the Open.\n//    The indicator subtracts a 10 period exponential moving average of the \n//    AccumDist function from a 3 period exponential moving average of the \n//    AccumDist function.    \n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Money Flow Indicator (Chaikin Oscillator)", shorttitle="MFI")\nFast = input(3, minval=1)\nSlow = input(10, minval=1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=gray, linestyle=hline.style_dashed)\nlenMax = max(Fast, Slow)\nlenMin = min(Fast, Slow)\nxDiv = (high - low) * volume\nSumMax = sum(iff(xDiv > 0, (close - open) / (high - low) * volume , 0) , lenMax)\nSumMin = sum(iff(xDiv > 0, (close - open) / (high - low) * volume , 0) , lenMin)\nemaMax = ema(SumMax, lenMax)\nemaMin = ema(SumMin, lenMin)\nnRes = emaMax - emaMin\npos = iff(nRes > 0, 1,\n\t   iff(nRes < 0, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(nRes, color=blue, title="RMI")'

class SM8E4211E54F1CCDC2(PinePortBase, IStrategy):
    source_id = "SM_8e4211e54f1ccdc2"
    source_file = '聚合动量指标策略Chaikin-Oscillator-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'Fast': 3, 'Slow': 10, 'reverse': False}
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
