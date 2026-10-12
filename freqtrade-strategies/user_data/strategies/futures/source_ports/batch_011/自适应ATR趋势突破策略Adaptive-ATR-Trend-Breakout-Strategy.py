"""batch_011 port of 自适应ATR趋势突破策略Adaptive-ATR-Trend-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-30 00:00:00\nend: 2023-10-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s Volty Strategy v1.0", shorttitle = "Volty 1.0", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 100)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(false, defval = false, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot, %")\nlength = input(5)\nnumATRs = input(0.75)\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Indicator\natrs = sma(tr, length) * numATRs\n\n//Trading\nsize = strategy.position_size\nlot = 0.0\nlot := size == 0 ? strategy.equity / close * capital / 100 : lot[1]\nif (not na(close[length])) and needlong\n    strategy.entry("L", strategy.long, lot, stop = close + atrs, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif (not na(close[length])) and needlong == false\n    strategy.entry("L", strategy.long, 0, stop = close + atrs, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif (not na(close[length])) and needshort\n    strategy.entry("S", strategy.short, lot, stop = close - atrs, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif (not na(close[length])) and needshort == false\n    strategy.entry("S", strategy.short, 0, stop = close - atrs, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))'

class SM84CA6CE4AD668825(PinePortBase, IStrategy):
    source_id = "SM_84ca6ce4ad668825"
    source_file = '自适应ATR趋势突破策略Adaptive-ATR-Trend-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': False, 'capital': 100, 'length': 5, 'numATRs': 0.75, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 100
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
