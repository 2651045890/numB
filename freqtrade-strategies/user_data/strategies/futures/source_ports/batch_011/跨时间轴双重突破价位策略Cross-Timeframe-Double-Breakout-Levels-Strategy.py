"""batch_011 port of 跨时间轴双重突破价位策略Cross-Timeframe-Double-Breakout-Levels-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-15 00:00:00\nend: 2023-11-14 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy(title = "Noro\'s Levels Strategy v1.0", shorttitle = "Levels str 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\ntf = input(\'W\',  title = "timeframe 1")\ntf2 = input(\'D\',  title = "timeframe 2")\nsrc = input(ohlc4, "Source")\nap = input(true, defval = true, title = "antipila")\ncf = input(true, defval = true, title = "color filter")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Signals\nlevel = request.security(syminfo.tickerid, tf, src[1])\nlevel2 = request.security(syminfo.tickerid, tf2, src[1])\nplot(level, linewidth = 3, color = silver)\nplot(level2, linewidth = 3, color = gray)\nup1 = close > level and ap == false ? true : low > level ? true : false\ndn1 = close < level and ap == false ? true : high < level ? true : false\nup2 = close > level2 and ap == false ? true : low > level2 ? true : false\ndn2 = close < level2 and ap == false ? true : high < level2 ? true : false\n\n//Trading\nlot = strategy.position_size != strategy.position_size[1] ? strategy.equity / close * capital / 100 : lot[1]\n\nif up1 and up2 and (close < open or cf == false)\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif dn1 and dn2 and (close > open or cf == false)\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()'

class SM1D198A9DAE2EA278(PinePortBase, IStrategy):
    source_id = "SM_1d198a9dae2ea278"
    source_file = '跨时间轴双重突破价位策略Cross-Timeframe-Double-Breakout-Levels-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'tf': 'W', 'tf2': 'D', 'ap': True, 'cf': True, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
