"""batch_012 port of 鲍威尔指数快速突破策略Fast-RSI-Breakthrough-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-23 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title = "Noro\'s Fast RSI Strategy v1.2", shorttitle = "Fast RSI str 1.2", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 5)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\nrsiperiod = input(7, defval = 7, minval = 2, maxval = 50, title = "RSI Period")\nlimit = input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")\nrsisrc = input(close, defval = close, title = "RSI Price")\nrb = input(1, defval = 1, minval = 1, maxval = 5, title = "RSI Bars")\nfromyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Fast RSI\nfastup = rma(max(change(rsisrc), 0), rsiperiod)\nfastdown = rma(-min(change(rsisrc), 0), rsiperiod)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\nuplimit = 100 - limit\ndnlimit = limit\n\n//RSI Bars\nur = fastrsi > uplimit\ndr = fastrsi < dnlimit\nuprsi = rb == 1 and ur ? 1 : rb == 2 and ur and ur[1] ? 1 : rb == 3 and ur and ur[1] and ur[2] ? 1 : rb == 4 and ur and ur[1] and ur[2] and ur[3] ? 1 : rb == 5 and ur and ur[1] and ur[2] and ur[3] and ur[4] ? 1 : 0\ndnrsi = rb == 1 and dr ? 1 : rb == 2 and dr and dr[1] ? 1 : rb == 3 and dr and dr[1] and dr[2] ? 1 : rb == 4 and dr and dr[1] and dr[2] and dr[3] ? 1 : rb == 5 and dr and dr[1] and dr[2] and dr[3] and dr[4] ? 1 : 0\n\n//Body\nbody = abs(close - open)\nemabody = ema(body, 30)\n\n//Signals\nbar = close > open ? 1 : close < open ? -1 : 0\nup = bar == -1 and (strategy.position_size == 0 or close < strategy.position_avg_price) and dnrsi and body > emabody / 4\ndn = bar == 1 and (strategy.position_size == 0 or close > strategy.position_avg_price) and uprsi and body > emabody / 4\nexit = ((strategy.position_size > 0 and fastrsi > dnlimit and bar == 1) or (strategy.position_size < 0 and fastrsi < uplimit and bar == -1)) and body > emabody / 2\n\n//Trading\nif up\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))\n\nif dn\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 00, 00)))\n    \nif time > timestamp(toyear, tomonth, today, 00, 00) or exit\n    strategy.close_all()\n'

class SMFastRSIBreakthroughStrategy353dba(PinePortBase, IStrategy):
    source_id = "SM_353dba952ba77788"
    source_file = '鲍威尔指数快速突破策略Fast-RSI-Breakthrough-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'rsiperiod': 7, 'limit': 30, 'rsisrc': 'close', 'rb': 1, 'fromyear': 2018, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 5
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
