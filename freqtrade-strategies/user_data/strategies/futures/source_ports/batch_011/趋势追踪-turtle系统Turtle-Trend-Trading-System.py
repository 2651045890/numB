"""batch_011 port of 趋势追踪-turtle系统Turtle-Trend-Trading-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-19 00:00:00\nend: 2023-12-19 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © racer8\n//@version=4\nstrategy("Turtle System", overlay=true)\n\nn = input(55,"Entry Length")\ne = input(20,"Exit Length")\n\nHI = highest(n)\nLO = lowest(n)\nhi = highest(e)\nlo = lowest(e)\n\nif close>HI[1]\n    strategy.entry("Buy", strategy.long)\n\nif close<LO[1]\n    strategy.entry("Sell", strategy.short)\n    \nif low<lo[1]\n    strategy.close("Buy")\n\nif high>hi[1]\n    strategy.close("Sell")\n\nplot(HI,color=color.lime)\nplot(LO,color=color.red)\nplot(hi,color=color.blue)\nplot(lo,color=color.maroon)\n'

class SME61E29857CDE3C81(PinePortBase, IStrategy):
    source_id = "SM_e61e29857cde3c81"
    source_file = '趋势追踪-turtle系统Turtle-Trend-Trading-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'n': 55, 'e': 20}
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
