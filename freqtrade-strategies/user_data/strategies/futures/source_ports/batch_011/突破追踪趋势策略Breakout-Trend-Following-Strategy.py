"""batch_011 port of 突破追踪趋势策略Breakout-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-01 00:00:00\nend: 2023-12-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © JstMtlQC\n\n//@version=4\nstrategy("Trend Following Breakout",calc_on_order_fills=true,calc_on_every_tick =false, overlay=true, initial_capital=2000,commission_value=.1,default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n\n/////////////// INPUT ENTRY EXIT\nentry= input(100, "ENTRY H/L")\nexit= input(50, "EXIT H/L")\n\n/////////////// Backtest Input\nFromYear = input(2015, "Backtest Start Year")\nFromMonth = input(1, "Backtest Start Month")\nFromDay = input(1, "Backtest Start Day")\nToYear = input(2999, "Backtest End Year")\nToMonth = input(1, "Backtest End Month")\nToDay = input(1, "Backtest End Day")\n\n/////////////// Backtest Setting\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  \nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)       \nwindow()  => time >= start and time <= finish ? true : false \n\n/////////////// BUY OPEN PLOT\nhighestpricelong = highest(high,entry)[1]\nplot(highestpricelong, color=color.green, linewidth=2)\n\n/////////////// BUY CLOSE PLOT\nlowestpricelong = lowest(high,exit)[1]\nplot(lowestpricelong, color=color.green, linewidth=2)\n\n/////////////// SHORT OPEN PLOT\nlowestpriceshort = lowest(low,entry)[1]\nplot(lowestpriceshort, color=color.red, linewidth=2)\n\n/////////////// SHORT CLOSE PLOT\nhighestpriceshort = highest(low,exit)[1]\nplot(highestpriceshort, color=color.red, linewidth=2)\n\n///////////////////////////////////////////////////////////////////////////////////////////\n/////////////////////////////// CONDITION LONG SHORT //////////////////////////////////////\n///////////////////////////////////////////////////////////////////////////////////////////\n\n/////////////// SHORT \n\nentryshort= crossunder(close, lowestpriceshort)\nexitshort= crossover(close,highestpriceshort)\n\n/////////////// LONG \n\nexitlong= crossover(close, lowestpricelong)\nentrylong= crossover(close,highestpricelong)\n\n///////////////////////////////////////////////////////////////////////////////////////////\n/////////////////////////////// LONG and SHORT ORDER //////////////////////////////////////\n///////////////////////////////////////////////////////////////////////////////////////////\n\n/////////////// LONG \n\nif (entrylong)\n    strategy.entry("LongEntry", strategy.long, when = window())\nif (exitlong or entryshort)\n    strategy.close("LongEntry", when=window())\n\n/////////////// SHORT \n\nif (entryshort)\n    strategy.entry("short", strategy.short, when = window())\nif (exitshort or entrylong)\n    strategy.close("short", when=window())\n\n'

class SM59CF7E0366167D8E(PinePortBase, IStrategy):
    source_id = "SM_59cf7e0366167d8e"
    source_file = '突破追踪趋势策略Breakout-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'entry': 100, 'exit': 50, 'FromYear': 2015, 'FromMonth': 1, 'FromDay': 1, 'ToYear': 2999, 'ToMonth': 1, 'ToDay': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 2000
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
