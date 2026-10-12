"""batch_012 port of 迪纳波利去趋势震荡器策略DiNapoli-Detrended-Oscillator-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-23 00:00:00\nend: 2023-09-22 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version = 2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 05/12/2016\n// DiNapoli Detrended Oscillator Strategy\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="DiNapoli Detrended Oscillator Strategy Backtest")\nLength = input(14, minval=1)\nTrigger = input(0)\nreverse = input(true, title="Trade reverse")\nhline(Trigger, color=gray, linestyle=line)\nxSMA = sma(close, Length)\nnRes = close - xSMA\npos = iff(nRes > Trigger, 1,\n\t   iff(nRes <= Trigger, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n         iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nplot(nRes, color=blue, title="DiNapoli")\nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\n'

class SMDiNapoliDetrendedOscillatorStrategya6d831(PinePortBase, IStrategy):
    source_id = "SM_a6d83100f8c19722"
    source_file = '迪纳波利去趋势震荡器策略DiNapoli-Detrended-Oscillator-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'Length': 14, 'Trigger': 0, 'reverse': True}
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
