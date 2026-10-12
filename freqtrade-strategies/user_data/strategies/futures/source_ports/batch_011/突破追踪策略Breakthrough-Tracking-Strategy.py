"""batch_011 port of 突破追踪策略Breakthrough-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="MARKET DYNAMICS HH LL BREAKOUT", shorttitle="BREAKOUT STRATEGY", overlay=true)\n\n////\n\n\n//Higher High or Lower Low Entry Inputs\nprice = input(close)\nLookBack = input(26)\nHighest = highest(LookBack)\nLowest = lowest(LookBack)\n\nlong = price > Highest[1] \nshort = price < Lowest[1]\n\n\n\n\n//Safety Confirmation Inputs - Helps to thin out false breakouts or break downs\nlength = input(10)\nHigh_Guard = highest(length)\nLow_Guard = lowest(length)\nlength2 = input(1)\n\nlong1 = long == 1 and Highest[1] > High_Guard[length2]\nshort1 = short == 1 and Lowest[1] < Low_Guard[length2]\n\n\nstrategy.entry("Long", strategy.long, when=long1)\nstrategy.entry("Short", strategy.short, when=short1)\n'

class SMEA6EC3F7D01A6A1E(PinePortBase, IStrategy):
    source_id = "SM_ea6ec3f7d01a6a1e"
    source_file = '突破追踪策略Breakthrough-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'LookBack': 26, 'length': 10, 'length2': 1}
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
