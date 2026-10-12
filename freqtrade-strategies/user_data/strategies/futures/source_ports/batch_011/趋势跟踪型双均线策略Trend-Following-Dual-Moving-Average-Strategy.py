"""batch_011 port of 趋势跟踪型双均线策略Trend-Following-Dual-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-17 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 04/05/2018\n// The Average Directional Movement Index Rating (ADXR) measures the strength \n// of the Average Directional Movement Index (ADX). It\'s calculated by taking \n// the average of the current ADX and the ADX from one time period before \n// (time periods can vary, but the most typical period used is 14 days).\n// Like the ADX, the ADXR ranges from values of 0 to 100 and reflects strengthening \n// and weakening trends. However, because it represents an average of ADX, values \n// don\'t fluctuate as dramatically and some analysts believe the indicator helps \n// better display trends in volatile markets.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nfADX(Len) =>\n    up = change(high)\n    down = -change(low)\n    trur = rma(tr, Len)\n    plus = fixnan(100 * rma(up > down and up > 0 ? up : 0, Len) / trur)\n    minus = fixnan(100 * rma(down > up and down > 0 ? down : 0, Len) / trur)\n    sum = plus + minus \n    100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), Len)\n\nstrategy(title="Average Directional Movement Index Rating Backtest", shorttitle="ADXR")\nLengthADX = input(title="Length ADX", defval=14)\nLengthADXR = input(title="Length ADXR", defval=14)\nreverse = input(false, title="Trade reverse")\nSignal1 = input(13, step=0.01)\nSignal2 = input(45, step=0.01)\nhline(Signal1, color=green, linestyle=line)\nhline(Signal2, color=red, linestyle=line)\nxADX = fADX(LengthADX)\nxADXR = (xADX + xADX[LengthADXR]) / 2\npos = iff(xADXR < Signal1, 1,\n       iff(xADXR > Signal2, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xADXR, color=green, title="ADXR")'

class SM4B314DC68D487069(PinePortBase, IStrategy):
    source_id = "SM_4b314dc68d487069"
    source_file = '趋势跟踪型双均线策略Trend-Following-Dual-Moving-Average-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'LengthADX': 14, 'LengthADXR': 14, 'reverse': False, 'Signal1': 13, 'Signal2': 45}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
