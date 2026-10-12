"""batch_012 port of 针对加密货币的快速RSI跳空策略Fast-RSI-Gap-Trading-Strategy-for-Cryptocurrencies.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-27 00:00:00\nend: 2023-11-26 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\nstrategy(title = "Noro\'s Fast RSI Strategy v1.5", shorttitle = "Fast RSI str 1.5", overlay = true)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\nusersi = input(true, defval = true, title = "Use Fast RSI Strategy")\nusemm = input(true, defval = true, title = "Use Min/Max Strategy")\nusesma = input(false, defval = false, title = "Use SMA Filter")\nsmaperiod = input(20, defval = 20, minval = 2, maxval = 1000, title = "SMA Filter Period")\nfast = input(7, defval = 7, minval = 2, maxval = 50, title = "Fast RSI Period")\nlimit = input(30, defval = 30, minval = 1, maxval = 100, title = "RSI limit")\nrsisrc = input(close, defval = close, title = "RSI Price")\nrsibars = input(1, defval = 1, minval = 1, maxval = 20, title = "RSI Bars")\nmmbars = input(1, defval = 1, minval = 1, maxval = 5, title = "Min/Max Bars")\nshowsma = input(false, defval = false, title = "Show SMA Filter")\nshowarr = input(false, defval = false, title = "Show Arrows")\nfromyear = input(2018, defval = 2018, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Fast RSI\nfastup = rma(max(change(rsisrc), 0), fast)\nfastdown = rma(-min(change(rsisrc), 0), fast)\nfastrsi = fastdown == 0 ? 100 : fastup == 0 ? 0 : 100 - (100 / (1 + fastup / fastdown))\n\n//Limits\nbar = close > open ? 1 : close < open ? -1 : 0\nuplimit = 100 - limit\ndnlimit = limit\n\n//RSI Bars\nupsignal = fastrsi > uplimit ? 1 : 0\ndnsignal = fastrsi < dnlimit ? 1 : 0\nuprsi = sma(upsignal, rsibars) == 1\ndnrsi = sma(dnsignal, rsibars) == 1\n\n//Body\nbody = abs(close - open)\nabody = sma(body, 10)\n\n//MinMax Bars\nmin = min(close, open)\nmax = max(close, open)\nminsignal = min < min[1] and bar == -1 and bar[1] == -1 ? 1 : 0\nmaxsignal = max > max[1] and bar == 1 and bar[1] == 1 ? 1 : 0\nmins = sma(minsignal, mmbars) == 1\nmaxs = sma(maxsignal, mmbars) == 1\n\n//SMA Filter\nsma = sma(close, smaperiod)\ncolorsma = showsma ? blue : na\nplot(sma, color = colorsma, linewidth = 3)\n\n//Signals\nup1 = bar == -1 and (strategy.position_size == 0 or close < strategy.position_avg_price) and dnrsi and body > abody / 5 and usersi\ndn1 = bar == 1 and (strategy.position_size == 0 or close > strategy.position_avg_price) and uprsi and body > abody / 5 and usersi\nup2 = mins and (close > sma or usesma == false) and fastrsi < 70 and usemm\ndn2 = maxs and (close < sma or usesma == false) and fastrsi > 30 and usemm \nexit = ((strategy.position_size > 0 and fastrsi > dnlimit and bar == 1) or (strategy.position_size < 0 and fastrsi < uplimit and bar == -1)) and body > abody / 2\n\n//Arrows\ncol = exit ? black : up1 or dn1 ? blue : up2 or dn2 ? red : na\nneedup = up1 or up2\nneeddn = dn1 or dn2\nneedexitup = exit and strategy.position_size < 0\nneedexitdn = exit and strategy.position_size > 0\nplotarrow(showarr and needup ? 1 : na, colorup = blue, colordown = blue, transp = 0)\nplotarrow(showarr and needdn ? -1 : na, colorup = blue, colordown = blue, transp = 0)\nplotarrow(showarr and needexitup ? 1 : na, colorup = black, colordown = black, transp = 0)\nplotarrow(showarr and needexitdn ? -1 : na, colorup = black, colordown = black, transp = 0)\n\n//Trading\nif up1 or up2\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif dn1 or dn2\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when=(time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    \nif time > timestamp(toyear, tomonth, today, 23, 59) or exit\n    strategy.close_all()\n'

class SMRSIFastRSIGapTradingStrategyforCryptocurrencies42181a(PinePortBase, IStrategy):
    source_id = "SM_42181a39a50de3b6"
    source_file = '针对加密货币的快速RSI跳空策略Fast-RSI-Gap-Trading-Strategy-for-Cryptocurrencies.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'usersi': True, 'usemm': True, 'usesma': False, 'smaperiod': 20, 'fast': 7, 'limit': 30, 'rsisrc': 'close', 'rsibars': 1, 'mmbars': 1, 'showsma': False, 'showarr': False, 'fromyear': 2018, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
