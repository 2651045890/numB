"""batch_012 port of 震荡跟踪短线策略Oscillation-Tracking-Short-term-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-16 00:00:00\nend: 2024-01-16 22:45:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s ZZ-3 Strategy", shorttitle = "ZZ-3 str", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\ncorr = input(0.0, title = "Correction, %")\nbars = input(1, minval = 1)\nrevers = input(false, defval = false, title = "revers")\nshowll = input(true, defval = true, title = "Show Levels")\nshowbg = input(false, defval = false, title = "Show Background")\nshowar = input(false, defval = false, title = "Show Arrows")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Levels\nhbar = 0\nhbar := high > high[1] ? 1 : high < high[1] ? -1 : 0\nlbar = 0\nlbar := low > low[1] ? 1 : low < low[1] ? -1 : 0\nuplevel = 0.0\ndnlevel = 0.0\nhh = highest(high, bars + 1)\nll = lowest(low, bars + 1)\nuplevel := hbar == -1 and sma(hbar, bars)[1] == 1 ? hh + ((hh / 100) * corr) : uplevel[1]\ndnlevel := lbar == 1 and sma(lbar, bars)[1] == -1 ? ll - ((ll / 100) * corr) : dnlevel[1]\n\n//Lines\nupcol = na\nupcol := showll == false ? na : uplevel != uplevel[1] ? na : lime\nplot(uplevel, color = upcol, linewidth = 2)\ndncol = na\ndncol := showll == false ? na : dnlevel != dnlevel[1] ? na : red\nplot(dnlevel, color = dncol, linewidth = 2)\n\n//Background\nsize = strategy.position_size\ntrend = 0\ntrend := size > 0 ? 1 : size < 0 ? -1 : high >= uplevel ? 1 : low <= dnlevel ? -1 : trend[1]\ncol = showbg == false ? na : trend == 1 ? lime : trend == -1 ? red : na\nbgcolor(col)\n\n//Arrows\nlongsignal = false\nshortsignal = false\nlongsignal := size > size[1]\nshortsignal := size < size[1]\nplotarrow(longsignal and showar and needlong ? 1 : na, colorup = blue, colordown = blue, transp = 0)\nplotarrow(shortsignal and showar and needshort ? -1 : na, colorup = blue, colordown = blue, transp = 0)\n\n//Trading\nlot = 0.0\nlot := size != size[1] ? strategy.equity / close * capital / 100 : lot[1]\nif uplevel > 0 and dnlevel > 0 and revers == false\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = uplevel, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dnlevel, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif uplevel > 0 and dnlevel > 0 and revers == true\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, limit = dnlevel, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, limit = uplevel, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()\n'

class SMOscillationTrackingShorttermStrategy765aff(PinePortBase, IStrategy):
    source_id = "SM_765aff6b27078528"
    source_file = '震荡跟踪短线策略Oscillation-Tracking-Short-term-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'corr': 0.0, 'bars': 1, 'revers': False, 'showll': True, 'showbg': False, 'showar': False, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
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
