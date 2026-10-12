"""batch_011 port of 穿越限价单双向跨期交易策略Cross-Limit-Order-Cross-Period-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-27 00:00:00\nend: 2023-03-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2020\n\n//@version=4\nstrategy(title = "Noro\'s CrossLimit", shorttitle = "CrossLimit", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100.0, pyramiding = 0, commission_value = 0.0)\n\nneedlong = input(true, "long")\nneedshort = input(true, "short")\nlotsize = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot, %")\nsrc = input(close, defval = close, title = "MA Source")\nlen = input(5, defval = 5, minval = 1, title = "SMA length")\noff = input(0, defval = 0, minval = 0, title = "SMA offset")\nanti = input(true, defval = true, title = "Anti-saw filter")\nrev = input(false, defval = false, title = "Reverse")\nshowma = input(true, defval = true, title = "Show MA")\nshowbg = input(false, defval = false, title = "Show background")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//MA\nma = sma(src, len)[off]\nmacol = showma ? color.blue : na\nplot(ma, color = macol, linewidth = 3, transp = 0)\n\n//Background\ntrend = 0\ntrend := anti == false and close > ma ? 1 : anti == false and close < ma ? -1 : low > ma ? 1 : high < ma ? -1 : trend[1]\nbgcol = showbg ? trend == 1 ? color.lime : trend == -1 ? color.red : na : na\nbgcolor(bgcol, transp = 70)\n\n//Signals\nbar = close > open ? 1 : close < open ? -1 : 0\nup = (trend == 1 and rev == false) or (trend == -1 and rev == true)\ndn = (trend == -1 and rev == false) or (trend == 1 and rev == true)\n\n//Trading\nsize = strategy.position_size\ntruetime = time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)\nlot = 0.0\nlot := size != size[1] ? strategy.equity / close * lotsize / 100 : lot[1]\nif trend != 0\n    strategy.entry("Long", strategy.long, lot, limit = ma, when = needlong and truetime and up)\n    strategy.entry("Short", strategy.short, lot, limit = ma, when = needshort and truetime and dn)\nif size > 0 and needshort == false and trend == -1\n    strategy.exit("Stop Long", "Long", limit = ma)\nif size < 0 and needlong == false and trend == 1\n    strategy.exit("Stop Short", "Short", limit = ma)\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()\n    strategy.cancel("Long")\n    strategy.cancel("Short")'

class SM1DA24867B3995EC1(PinePortBase, IStrategy):
    source_id = "SM_1da24867b3995ec1"
    source_file = '穿越限价单双向跨期交易策略Cross-Limit-Order-Cross-Period-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'lotsize': 100, 'len': 5, 'off': 0, 'anti': True, 'rev': False, 'showma': True, 'showbg': False, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
