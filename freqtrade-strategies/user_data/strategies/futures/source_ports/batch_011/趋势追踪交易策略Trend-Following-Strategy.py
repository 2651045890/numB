"""batch_011 port of 趋势追踪交易策略Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-25 00:00:00\nend: 2023-09-24 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(title = "Noro\'s TrendMaster Strategy v1.0", shorttitle = "TrendMaster str 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "long")\nneedshort = input(true, defval = true, title = "short")\nlen = input(21, defval = 20, minval = 2, maxval = 200, title = "MA Period")\nneedbg = input(false, defval = false, title = "Need trend Background?")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//PriceChannel 1\nlasthigh = highest(close, len)\nlastlow = lowest(close, len)\ncenter = (lasthigh + lastlow) / 2\n\n//Trend\ntrend = low > center and low[1] > center[1] ? 1 : high < center and high[1] < center[1] ? -1 : trend[1]\n\n//Bars\nbar = close > open ? 1 : close < open ? -1 : 0\n\n//Fast RSI\nfastup = rma(max(change(close), 0), 2)\nfastdown = rma(-min(change(close), 0), 2)\nrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\n\n//Body filter\nnbody = abs(close - open)\nabody = sma(nbody, 10)\nbody = nbody > abody / 2\n\n//Signals\nup1 = trend == 1 and rsi < 60 and (strategy.position_avg_price > close or strategy.position_size <= 0) and body\ndn1 = trend == -1 and rsi > 40 and (strategy.position_avg_price < close or strategy.position_size >= 0) and body\n\n//Lines\nplot(center, color = blue, linewidth = 3, transp = 0, title = "MA")\n\n//Background\ncol = needbg == false ? na : trend == 1 ? lime : red\nbgcolor(col, transp = 80)\n\n//Trading\n\nif up1\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn1\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()\n    '

class SMA9E7525FABBA0A7E(PinePortBase, IStrategy):
    source_id = "SM_a9e7525fabba0a7e"
    source_file = '趋势追踪交易策略Trend-Following-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'len': 20, 'needbg': False, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
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
