"""batch_011 port of 移动平均线区间突破策略Moving-Average-Channel-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2023-08-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Robot WhiteBox ShiftMA", shorttitle = "Robot WhiteBox ShiftMA", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot, %")\nper = input(3, title = "Length")\nsrc = input(ohlc4, title = "Source")\nshortlevel = input(10.0, title = "Short line (red)")\nlonglevel = input(-5.0, title = "Long line (lime)")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//SMAs\nsma = sma(src, per) \nshortline = sma * ((100 + shortlevel) / 100)\nlongline = sma * ((100 + longlevel) / 100)\nplot(shortline, linewidth = 2, color = red, title = "Short line")\nplot(sma, linewidth = 2, color = blue, title = "SMA line")\nplot(longline, linewidth = 2, color = lime, title = "Long line")\n\n//Trading\nsize = strategy.position_size\nlot = 0.0\nlot := size == 0 ? strategy.equity / close * capital / 100 : lot[1]\n\nif (not na(close[per])) and size == 0 and needlong\n    strategy.entry("L", strategy.long, lot, limit = longline)\n    \nif (not na(close[per])) and size == 0 and needshort\n    strategy.entry("S", strategy.short, lot, limit = shortline)\n    \nif (not na(close[per])) and size > 0 \n    strategy.entry("Close", strategy.short, 0, limit = sma)\n    \nif (not na(close[per])) and size < 0 \n    strategy.entry("Close", strategy.long, 0, limit = sma)\n\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()'

class SM9F02CCA8FDD98ACB(PinePortBase, IStrategy):
    source_id = "SM_9f02cca8fdd98acb"
    source_file = '移动平均线区间突破策略Moving-Average-Channel-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'per': 3, 'shortlevel': 10.0, 'longlevel': -5.0, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
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
