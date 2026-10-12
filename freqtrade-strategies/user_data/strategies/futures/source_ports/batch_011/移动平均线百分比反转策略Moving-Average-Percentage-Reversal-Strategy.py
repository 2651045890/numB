"""batch_011 port of 移动平均线百分比反转策略Moving-Average-Percentage-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 30/07/2018\n// Percent difference between price and MA\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Percent difference between price and MA Backtest")\nLength = input(14, minval=1)\nSellZone = input(0.54, minval=0.01, step = 0.01)\nBuyZone = input(0.03, minval=0.01, step = 0.01)\nreverse = input(false, title="Trade reverse")\nhline(BuyZone, color=green, linestyle=line)\nhline(SellZone, color=red, linestyle=line)\nxSMA = sma(close, Length)\nnRes = abs(close - xSMA) * 100 / close\npos = iff(nRes < BuyZone, 1,\n       iff(nRes > SellZone, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(nRes, color=blue, title="PD MA")'

class SM93186DC4BD1EAB08(PinePortBase, IStrategy):
    source_id = "SM_93186dc4bd1eab08"
    source_file = '移动平均线百分比反转策略Moving-Average-Percentage-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'SellZone': 0.54, 'BuyZone': 0.03, 'reverse': False}
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
