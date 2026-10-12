"""batch_011 port of 空间导向价格反转策略Price-Reversal-Strategy-Guided-by-Price-Channel.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-19 00:00:00\nend: 2023-11-26 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy(title = "Noro\'s PriceChannel for D1 v1.0", shorttitle = "PriceChannel D1", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100.0, pyramiding = 0)\n\n//Settings\nneedlong = input(true, "long")\nneedshort = input(true, "short")\nslowlen = input(30, defval = 30, minval = 2, maxval = 200, title = "PriceChannel Period")\npcbars = input(1, defval = 1, minval = 1, maxval = 20, title = "PriceChannel Bars")\nusecol = input(true, "Use color-filter")\nusebod = input(true, "Use body-filter")\nneedbg = input(false, defval = false, title = "Need trend Background?")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\nsrc = close\n\n//PriceChannel\nlasthigh = highest(src, slowlen)\nlastlow = lowest(src, slowlen)\ncenter = (lasthigh + lastlow) / 2\n\n//Trend\nub = low > center ? 1 : 0\ndb = high < center ? 1 : 0\ntrend = sma(ub, pcbars) == 1 ? 1 : sma(db, pcbars) == 1 ? -1 : trend[1]\n\n//Body\nbody = abs(close - open)\nabody = sma(body, 10)\n\n//Signals\nup = trend == 1 and (close < open or usecol == false) and (body > abody / 5 or usebod == false)\ndn = trend == -1 and (close > open or usecol == false) and (body > abody / 5 or usebod == false)\n\n//Lines\nplot(center, color = blue, linewidth = 3, transp = 0, title = "PriceChannel Center")\n\n//Background\ncol = needbg == false ? na : trend == 1 ? lime : red\nbgcolor(col, transp = 80)\n\n//Trading\nif up\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()\n    '

class SMB5EA73FC36884B88(PinePortBase, IStrategy):
    source_id = "SM_b5ea73fc36884b88"
    source_file = '空间导向价格反转策略Price-Reversal-Strategy-Guided-by-Price-Channel.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'slowlen': 30, 'pcbars': 1, 'usecol': True, 'usebod': True, 'needbg': False, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
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
