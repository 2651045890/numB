"""batch_012 port of 连续N根K线收阴策略N-Bar-Close-Below-Open-Short-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-18 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 05/02/2020\n// Evaluates for n number of consecutive lower closes. Returns a value \n// of 1 when the condition is true or 0 when false.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="N Bars Down", shorttitle="NBD Backtest", overlay = false) \nnLength = input(4, minval=1)\ninput_takeprofit = input(20, title="Take Profit pip", step=0.01)\ninput_stoploss = input(10, title="Stop Loss pip", step=0.01)\nnCounter = 0\nnCounter := iff(close[1] <= open[1], nz(nCounter[1],0)+1,\n             iff(close[1] > open[1], 0, nCounter))\nC2 = iff(nCounter >= nLength, 1, 0)\nposprice = 0.0\npos = 0\nbarcolor(nz(pos[1], 0) == -1 ? color.red: nz(pos[1], 0) == 1 ? color.green : color.blue ) \nposprice := iff(C2== 1, close, nz(posprice[1], 0)) \npos := iff(posprice > 0, -1, 0)\nif (pos == 0) \n    strategy.close_all()\nif (pos == -1)\n    strategy.entry("Short", strategy.short)\nposprice := iff(low <= posprice - input_takeprofit and posprice > 0, 0 ,  nz(posprice, 0))\nposprice := iff(high >= posprice + input_stoploss and posprice > 0, 0 ,  nz(posprice, 0))\nplot(C2, title=\'NBD\', color=color.red)\n'

class SMNKNBarCloseBelowOpenShortStrategyb8c45a(PinePortBase, IStrategy):
    source_id = "SM_b8c45a60e242a3ad"
    source_file = '连续N根K线收阴策略N-Bar-Close-Below-Open-Short-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'nLength': 4, 'input_takeprofit': 20, 'input_stoploss': 10}
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
