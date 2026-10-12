"""batch_012 port of 闭合阳线策略Harami-Closing-Price-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-20 00:00:00\nend: 2023-11-27 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s Harami Strategy v1.0", shorttitle = "Harami str 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(false, defval = false, title = "Short")\n\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Body\nbody = abs(close - open)\nabody = sma(body, 10)\n\n//MinMax Bars\nmin = min(close, open)\nmax = max(close, open)\nbar = close > open ? 1 : close < open ? -1 : 0\n\n//Signals\nup = bar == 1 and bar[1] == -1 and min > min[1] and max < max[1]\ndn = bar == -1 and bar[1] == 1 and min > min[1] and max < max[1]\nexit = ((strategy.position_size > 0 and bar == 1) or (strategy.position_size < 0 and bar == -1)) and body > abody / 2\n\n//Trading\nif up\n    if strategy.position_size < 0\n        strategy.close_all()\n        \n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn\n    if strategy.position_size > 0\n        strategy.close_all()\n        \n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59) or exit\n    strategy.close_all()\n'

class SMHaramiClosingPriceStrategy2b479d(PinePortBase, IStrategy):
    source_id = "SM_2b479d23feacf157"
    source_file = '闭合阳线策略Harami-Closing-Price-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': False, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
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
