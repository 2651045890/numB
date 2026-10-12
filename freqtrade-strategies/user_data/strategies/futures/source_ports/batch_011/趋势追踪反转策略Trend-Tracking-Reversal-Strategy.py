"""batch_011 port of 趋势追踪反转策略Trend-Tracking-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2019\n\n//@version=3\nstrategy(title = "Noro\'s 3Bars Strategy by Larry Williams", shorttitle = "3Bars", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\ncorr = input(0.0, title = "Correction, %")\nbars = input(1, minval = 1)\nrevers = input(false, defval = false, title = "revers")\nshowll = input(true, defval = true, title = "Show Levels")\nshowos = input(true, defval = true, title = "Show Levels one side")\nshowcl = input(false, defval = false, title = "Show Levels continuous line")\nshowbg = input(false, defval = false, title = "Show Background")\nshowar = input(false, defval = false, title = "Show Arrows")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\nlen = input(3)\n\nhma = sma(high, len)\nlma = sma(low, len)\nplot(hma)\nplot(lma)\n\n//Levels\nhbar = 0\nhbar := high > high[1] ? 1 : high < high[1] ? -1 : 0\nlbar = 0\nlbar := low > low[1] ? 1 : low < low[1] ? -1 : 0\nuplevel = 0.0\ndnlevel = 0.0\nhh = highest(high, bars + 1)\nll = lowest(low, bars + 1)\nuplevel := hbar == -1 and sma(hbar, bars)[1] == 1 ? hh + ((hh / 100) * corr) : uplevel[1]\ndnlevel := lbar == 1 and sma(lbar, bars)[1] == -1 ? ll - ((ll / 100) * corr) : dnlevel[1]\n\n//Background\nsize = strategy.position_size\ntrend = 0\ntrend := size > 0 ? 1 : size < 0 ? -1 : high >= uplevel ? 1 : low <= dnlevel ? -1 : trend[1]\ncol = showbg == false ? na : trend == 1 ? lime : trend == -1 ? red : na\nbgcolor(col)\n\n//Lines\nupcol = na\nupcol := showll == false ? na : uplevel != uplevel[1] and showcl == false ? na : showos and trend[1] == 1 ? na : lime\nplot(uplevel, color = upcol, linewidth = 2)\ndncol = na\ndncol := showll == false ? na : dnlevel != dnlevel[1] and showcl == false ? na : showos and trend[1] == -1 ? na : red\nplot(dnlevel, color = dncol, linewidth = 2)\n\n//Arrows\nlongsignal = false\nshortsignal = false\nlongsignal := size > size[1]\nshortsignal := size < size[1]\nplotarrow(longsignal and showar and needlong ? 1 : na, colorup = blue, colordown = blue, transp = 0)\nplotarrow(shortsignal and showar and needshort ? -1 : na, colorup = blue, colordown = blue, transp = 0)\n\n//Trading\nlot = 0.0\nlot := size != size[1] ? strategy.equity / close * capital / 100 : lot[1]\nif uplevel > 0 and dnlevel > 0 and revers == false\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = uplevel)\n    strategy.entry("Long stop", strategy.short, 0, stop = lma)\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dnlevel)\n    strategy.entry("Short stop", strategy.long, 0, stop = hma)\n    \n// if time > timestamp(toyear, tomonth, today, 23, 59)\n//     strategy.close_all()'

class SM1ADA9F0B5EACFF71(PinePortBase, IStrategy):
    source_id = "SM_1ada9f0b5eacff71"
    source_file = '趋势追踪反转策略Trend-Tracking-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'corr': 0.0, 'bars': 1, 'revers': False, 'showll': True, 'showos': True, 'showcl': False, 'showbg': False, 'showar': False, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31, 'len': 3}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
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
