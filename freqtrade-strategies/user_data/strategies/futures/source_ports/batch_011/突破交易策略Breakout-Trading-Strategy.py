"""batch_011 port of 突破交易策略Breakout-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s Brakeout Strategy v2.0", shorttitle = "Brakeout str 2.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\nlen = input(4, defval = 4, minval = 1, maxval = 1000, title = "Length")\nbod = input(false, defval = false, title = "Body mode")\nrev = input(false, defval = false, title = "Revers")\nshowlines = input(true, defval = true, title = "Show Lines?")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Extremums\nmin = bod ? min(open, close) : low\nmax = bod ? max(open, close) : high\nupex = highest(max, len) + syminfo.mintick * 10\ndnex = lowest(min, len) - syminfo.mintick * 10\ncol = showlines ? blue : na\nplot(upex, color = col, linewidth = 2)\nplot(dnex, color = col, linewidth = 2)\n\n//Trading\nlot = 0.0\nlot := strategy.position_size != strategy.position_size[1] ? strategy.equity / close * capital / 100 : lot[1]\n\nif (not na(close[len])) and rev == false\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = upex)\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dnex)\n    \nif (not na(close[len])) and rev == true\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, limit = dnex)\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, limit = upex)\n\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()'

class SM3F354BE4D510C22E(PinePortBase, IStrategy):
    source_id = "SM_3f354be4d510c22e"
    source_file = '突破交易策略Breakout-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'len': 4, 'bod': False, 'rev': False, 'showlines': True, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
