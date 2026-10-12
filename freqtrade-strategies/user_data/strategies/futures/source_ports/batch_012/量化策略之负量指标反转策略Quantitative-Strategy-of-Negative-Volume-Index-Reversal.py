"""batch_012 port of 量化策略之负量指标反转策略Quantitative-Strategy-of-Negative-Volume-Index-Reversal.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-13 00:00:00\nend: 2023-12-20 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter 11/08/2017\n// The theory behind the indexes is as follows: On days of increasing \n// volume, you can expect prices to increase, and on days of decreasing \n// volume, you can expect prices to decrease. This goes with the idea of \n// the market being in-gear and out-of-gear. Both PVI and NVI work in similar \n// fashions: Both are a running cumulative of values, which means you either \n// keep adding or subtracting price rate of change each day to the previous day`s \n// sum. In the case of PVI, if today`s volume is less than yesterday`s, don`t add \n// anything; if today`s volume is greater, then add today`s price rate of change. \n// For NVI, add today`s price rate of change only if today`s volume is less than \n// yesterday`s.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Negative Volume Index Backtest", shorttitle="NVI Str")\nEMA_Len = input(255, minval=1)\nreverse = input(false, title="Trade reverse")\nxROC = roc(close, 1)\nnRes = iff(volume < volume[1], nz(nRes[1], 0) + xROC, nz(nRes[1], 0))\nnResEMA = ema(nRes, EMA_Len)\npos = iff(nRes > nResEMA, 1,\n\t     iff(nRes < nResEMA, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(nRes, color=red, title="NVI")\nplot(nResEMA, color=blue, title="EMA")\n'

class SMQuantitativeStrategyofNegativeVolumeIndexReversalc1e8a3(PinePortBase, IStrategy):
    source_id = "SM_c1e8a3087f18e7a9"
    source_file = '量化策略之负量指标反转策略Quantitative-Strategy-of-Negative-Volume-Index-Reversal.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'EMA_Len': 255, 'reverse': False}
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
