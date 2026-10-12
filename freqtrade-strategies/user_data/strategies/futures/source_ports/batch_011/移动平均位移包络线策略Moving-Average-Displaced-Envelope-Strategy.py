"""batch_011 port of 移动平均位移包络线策略Moving-Average-Displaced-Envelope-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-25 00:00:00\nend: 2024-02-01 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 14/08/2020\n// Moving Average Displaced Envelope. These envelopes are calculated \n// by multiplying percentage factors with their displaced expotential \n// moving average (EMA) core.\n// How To Trade Using:\n// Adjust the envelopes percentage factors to control the quantity and \n// quality of the signals. If a previous high goes above the envelope \n// a sell signal is generated. Conversely, if the previous low goes below \n// the envelope a buy signal is given.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Moving Average Displaced Envelope Backtest", shorttitle="MA DE", overlay = true)\nPrice = input(title="Source", type=input.source, defval=close)\nPeriod =input(defval=9, minval=1)\nperAb = input(title = "Percent above", defval=.5, minval=0.01, step = 0.1)\nperBl = input(title = "Percent below", defval=.5, minval=0.01, step = 0.1)\ndisp = input(title = "Displacement", defval=13, minval=1) \nreverse = input(false, title="Trade reverse")\npos = 0\nsEMA = ema(Price, Period)\ntop = sEMA[disp] * ((100 + perAb)/100)\nbott = sEMA[disp]* ((100 - perBl)/100)\npos := iff(close < bott , 1,\n\t     iff(close > top, -1, pos[1])) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM5B8628C61832DF4D(PinePortBase, IStrategy):
    source_id = "SM_5b8628c61832df4d"
    source_file = '移动平均位移包络线策略Moving-Average-Displaced-Envelope-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'Period': 9, 'perAb': 0.5, 'perBl': 0.5, 'disp': 13, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
