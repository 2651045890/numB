"""batch_011 port of 趋势均线交易策略Trend-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-21 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(title = "Noro\'s Trend MAs Strategy v2.3", shorttitle = "Trend MAs str 2.3", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value=100.0, pyramiding=0)\n\n//Settings\nneedlong = input(true, "long")\nneedshort = input(true, "short")\nneedstops = input(false, "stops")\nstoppercent = input(5, defval = 5, minval = 1, maxval = 50, title = "Stop, %")\nusefastsma = input(true, "Use fast MA Filter")\nfastlen = input(5, defval = 5, minval = 1, maxval = 50, title = "fast MA Period")\nslowlen = input(21, defval = 20, minval = 2, maxval = 200, title = "slow MA Period")\nbars = input(2, defval = 2, minval = 0, maxval = 3, title = "Bars Q")\nneedbg = input(false, defval = false, title = "Need trend Background?")\nneedex = input(true, defval = true, title = "Need extreme? (crypto/fiat only!!!)")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\nsrc = close\n\n//PriceChannel 1\nlasthigh = highest(src, slowlen)\nlastlow = lowest(src, slowlen)\ncenter = (lasthigh + lastlow) / 2\n\n//PriceChannel 2\nlasthigh2 = highest(src, fastlen)\nlastlow2 = lowest(src, fastlen)\ncenter2 = (lasthigh2 + lastlow2) / 2\n\n//Trend\ntrend = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend[1]\n\n//Bars\nbar = close > open ? 1 : close < open ? -1 : 0\nredbars = bars == 0 ? 1 : bars == 1 and bar == -1 ? 1 : bars == 2 and bar == -1 and bar[1] == -1 ? 1 : bars == 3 and bar == -1 and bar[1] == -1 and bar[2] == -1 ? 1 : 0\ngreenbars = bars == 0 ? 1 : bars == 1 and bar == 1 ? 1 : bars == 2 and bar == 1 and bar[1] == 1 ? 1 : bars == 3 and bar == 1 and bar[1] == 1 and bar[2] == 1 ? 1 : 0\n\n//Fast RSI\nfastup = rma(max(change(close), 0), 2)\nfastdown = rma(-min(change(close), 0), 2)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\n\n//CryptoBottom\nmac = sma(close, 10)\nlen = abs(close - mac)\nsma = sma(len, 100)\nmax = max(open, close)\nmin = min(open, close)\n\n//Signals\nup1 = trend == 1 and (low < center2 or usefastsma == false) and redbars == 1\ndn1 = trend == -1 and (high > center2 or usefastsma == false) and greenbars == 1\nup2 = high < center and high < center2 and bar == -1 and needex\ndn2 = low > center and low > center2 and bar == 1 and needex\nup3 = close < open and len > sma * 3 and min < min[1] and fastrsi < 10 ? 1 : 0\n\n//Lines\nplot(center2, color = red, linewidth = 3, transp = 0, title = "Fast MA")\nplot(center, color = blue, linewidth = 3, transp = 0, title = "Slow MA")\n\n//Background\ncol = needbg == false ? na : trend == 1 ? lime : red\nbgcolor(col, transp = 80)\n\n//Trading\nstoplong = up1 == 1 and needstops == true ? close - (close / 100 * stoppercent) : stoplong[1]\nstopshort = dn1 == 1 and needstops == true ? close + (close / 100 * stoppercent) : stopshort[1]\n\nif up1 or up2 or up3\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.exit("Stop Long", "Long", stop = stoplong)\n\nif dn1\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.exit("Stop Short", "Short", stop = stopshort)\n    \nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()\n    '

class SM9324047D3654C5AF(PinePortBase, IStrategy):
    source_id = "SM_9324047d3654c5af"
    source_file = '趋势均线交易策略Trend-Moving-Average-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'needstops': False, 'stoppercent': 5, 'usefastsma': True, 'fastlen': 5, 'slowlen': 20, 'bars': 2, 'needbg': False, 'needex': True, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
