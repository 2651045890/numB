"""batch_011 port of 突破拉回中的隐形风暴Breakback-Storm-Strategy-in-Hidden-Opportunities.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Smash Day Pattern (Type B)", overlay=true, default_qty_type = strategy.fixed, default_qty_value = 1, initial_capital = 10000)\nin1 = input(40, "Max Days to Hold") - 1\n\nisLong = strategy.position_size > 0\nisShort = strategy.position_size < 0\n\nlongTrigger = close[1]<low[2]\nshortTrigger = close[1]>high[2]\n\nlongFilter = close[1] > close[80]\nshortFilter = close[1] < close[80]\n\nlongEntry = (not isLong) and longTrigger and longFilter\nshortEntry = (not isShort) and shortTrigger and shortFilter\n\nlongStop = valuewhen(longEntry, low[1], 0)\nlongPrice = valuewhen(longEntry, high[1], 0)\nshortStop = valuewhen(shortEntry, high[1],0)\nshortPrice = valuewhen(shortEntry, low[1], 0)\n\nstrategy.entry(id = "Long", long = true, stop = longPrice+.001, when = longEntry)\nstrategy.exit(id = "Stop Long", from_entry = "Long", stop = longStop, when = isLong)\nstrategy.close("Long", barssince(longEntry==true)>=in1)\n\nstrategy.entry(id = "Short", long = false, stop = shortPrice-.001, when = shortEntry)\nstrategy.exit(id = "Stop Short", from_entry = "Short", stop = shortStop, when = isShort)\nstrategy.close("Short", barssince(shortEntry==true)>=in1)'

class SMEA1DF88C73947B6E(PinePortBase, IStrategy):
    source_id = "SM_ea1df88c73947b6e"
    source_file = '突破拉回中的隐形风暴Breakback-Storm-Strategy-in-Hidden-Opportunities.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'in1': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
