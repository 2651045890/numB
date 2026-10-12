"""batch_012 port of 追踪移动平均跳空策略Gap-Trading-Moving-Average-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-19 00:00:00\nend: 2023-10-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s Shift Close Strategy v1.0", shorttitle = "Shift Close 1.0", default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 5)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot, %")\nlimit = input(10)\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From Day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To Day")\n\n//Shift MA\nsma = sma(ohlc4, 3)\nind = ((close / sma) - 1) * 100\n\n//Oscilator\nplot(3 * limit, color = na, transp = 0)\nplot(limit, color = black, transp = 0)\nplot(0, color = black, transp = 0)\nplot(-1 * limit, color = black, transp = 0)\nplot(-3 * limit, color = na, transp = 0)\nplot(ind, linewidth = 3, transp = 0)\ncol = ind > limit ? red : ind < -1 * limit ? lime : na\nbgcolor(col, transp = 0)\n\n//Signals\nsize = strategy.position_size\nup = ind < -1 * limit\ndn = ind > limit\nexit = ind > -1 * limit and ind < limit\n\n//Trading\nlot = 0.0 \nlot := size == 0 ? strategy.equity / close * capital / 100 : lot[1]\n\nif up\n    if strategy.position_size < 0\n        strategy.close_all()\n        \n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn\n    if strategy.position_size > 0\n        strategy.close_all()\n        \n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif exit\n    strategy.close_all()\n'

class SMGapTradingMovingAverageStrategy242616(PinePortBase, IStrategy):
    source_id = "SM_242616fc7bdee19f"
    source_file = '追踪移动平均跳空策略Gap-Trading-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'limit': 10, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
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
