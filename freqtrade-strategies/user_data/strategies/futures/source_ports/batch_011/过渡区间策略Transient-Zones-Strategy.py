"""batch_011 port of 过渡区间策略Transient-Zones-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-28 00:00:00\nend: 2023-12-28 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy("Noro\'s Transient Zones Strategy v1.0", shorttitle = "TZ str 1.0", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings \nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\n\nusecol = input(true, defval = true, title = "Use Color-Filter")\nusebod = input(true, defval = true, title = "Use Body-Filter")\n\nh_left = input(title = "H left", defval = 10)\nh_right = -1\nsample_period = input(title = "Sample bars for % TZ",  defval = 5000)\nshow_ptz = input(title = "Show PTZ", type = bool, defval = true)\nshow_channel = input(title = "Show channel", type = bool, defval = true)\n\nfromyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//By Jurij w/ TZ percent occurrence by SPYderCrusher\n\n//barCount = nz(barCount[1]) + 1\n//check history and realtime PTZ\nh_left_low = lowest(h_left)\nh_left_high = highest(h_left)\nnewlow = low <= h_left_low\nnewhigh = high >= h_left_high\nplotshape(newlow and show_ptz, style=shape.triangledown, location=location.belowbar, color=red)\nplotshape(newhigh and show_ptz, style=shape.triangleup, location=location.abovebar, color=green)\nchannel_high = plot(show_channel ? h_left_low : 0, color=silver)\nchannel_low = plot (show_channel ? h_left_high : 0, color=silver)\n\n//check true TZ back in history\ncentral_bar_low = low[h_right + 1]\ncentral_bar_high = high[h_right + 1]\nfull_zone_low = lowest(h_left + h_right + 1)\nfull_zone_high = highest(h_left + h_right + 1)\ncentral_bar_is_highest = central_bar_high >= full_zone_high\ncentral_bar_is_lowest = central_bar_low <= full_zone_low\nplotarrow(central_bar_is_highest ? -1 : 0, offset=-h_right-1)\nplotarrow(central_bar_is_lowest ? 1 : 0, offset=-h_right-1)\n\n//Color Filter\nbar = close > open ? 1 : close < open ? -1 : 0\n\n//Body Filter\nnbody = abs(close - open)\nabody = sma(nbody, 10)\nbody = nbody > abody / 3 or usebod == false\n\n//Signals\nup1 = central_bar_is_lowest and body and (bar == -1 or usecol == false)\ndn1 = central_bar_is_highest and body and (bar == 1 or usecol == false)\nexit = ((strategy.position_size > 0 and close > open) or (strategy.position_size < 0 and close < open)) and body\n\n//Trading\nlot = strategy.position_size == 0 ? strategy.equity / close * capital / 100 : lot[1]\n\nif up1\n    if strategy.position_size < 0\n        strategy.close_all()\n        \n    strategy.entry("long", strategy.long, needlong == false ? 0 : lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn1\n    if strategy.position_size > 0\n        strategy.close_all()\n        \n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59) or exit\n    strategy.close_all()'

class SM7A9A5EE4FD7BD746(PinePortBase, IStrategy):
    source_id = "SM_7a9a5ee4fd7bd746"
    source_file = '过渡区间策略Transient-Zones-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'usecol': True, 'usebod': True, 'h_left': 10, 'sample_period': 5000, 'show_ptz': True, 'show_channel': True, 'fromyear': 2018, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
