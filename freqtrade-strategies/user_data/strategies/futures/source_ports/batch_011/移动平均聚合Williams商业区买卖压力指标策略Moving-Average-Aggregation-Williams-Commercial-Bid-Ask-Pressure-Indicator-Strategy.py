"""batch_011 port of 移动平均聚合Williams商业区买卖压力指标策略Moving-Average-Aggregation-Williams-Commercial-Bid-Ask-Pressure-Indicator-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-01 00:00:00\nend: 2023-11-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 23/01/2018\n// Accumulation is a term used to describe a market controlled by buyers;\n// whereas distribution is defined by a market controlled by sellers.\n// Williams recommends trading this indicator based on divergences:\n//\n//  Distribution of the security is indicated when the security is making \n//  a new high and the A/D indicator is failing to make a new high. Sell.\n//\n//  Accumulation of the security is indicated when the security is making \n//  a new low and the A/D indicator is failing to make a new low. Buy.\n//\n//You can change long to short in the Input Settings\n//WARNING:\n//- For purpose educate only\n//- This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Smoothened Williams Accumulation/Distribution (Williams AD)", shorttitle="Williams AD")\nLength = input(14, step = 1)\nreverse = input(false, title="Trade reverse")\nhline(0, color=blue, linestyle=line)\nxPrice = close\nxWAD = iff(close > nz(close[1], 0), nz(xWAD[1],0) + close - low[1], \n         iff(close < nz(close[1],0), nz(xWAD[1],0) + close - high[1],0))\nxWADMA = sma(xWAD, Length)\npos = iff(xWAD > xWADMA, 1,\n       iff(xWAD < xWADMA, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )           \nplot(xWAD, color=green, title="Williams AD")\nplot(xWADMA, color=red, title="MA(AD)")'

class SMF5710DA3F43DD70E(PinePortBase, IStrategy):
    source_id = "SM_f5710da3f43dd70e"
    source_file = '移动平均聚合Williams商业区买卖压力指标策略Moving-Average-Aggregation-Williams-Commercial-Bid-Ask-Pressure-Indicator-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'reverse': False}
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
