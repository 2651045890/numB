"""batch_011 port of 趋势交叉交易策略Trend-Bull-Bear-Crossover-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-30 00:00:00\nend: 2023-10-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © dadashkadir\n\n//@version=4\nstrategy("Mount MaV - Day MaV CrossOver Strgty", shorttitle="Yusram Str.", overlay=true)\nsrc = input(title= "Kaynak", type=input.source, defval=close)\nmav = input(title="Hareketli Ortlama Tipi", defval="SMA", options=["SMA", "EMA", "WMA"])\nGbar = input(title="Günlük Bar Sayısı", defval=7, minval=1, maxval=999)\nAbar = input(title="Aylık Bar Sayısı", defval=5, minval=1, maxval=999)\n//displacement = input(20, minval=1, title="Displacement")\ngetMA(src, length) =>\n    ma = 0.0\n    if mav == "SMA"\n        ma := sma(src, length)\n        ma\n\n    if mav == "EMA"\n        ma := ema(src, length)\n        ma\n\n    if mav == "WMA"\n        ma := wma(src, length)\n        ma\n    ma\nlong = "M" //Aylık\nln = security(syminfo.ticker, long, src)\nlnma = getMA(ln, Abar)\ngnma = getMA(src, Gbar)\ncol1= gnma>gnma[1]\ncol3= gnma<gnma[1]\ncolorM = col1 ? color.green : col3 ? color.navy : color.yellow\nl1 = plot(lnma, title="MhO", trackprice = true, style=plot.style_line, color=color.red, linewidth=3)\nl2 = plot(gnma, title="DhO", trackprice = true, style=plot.style_line, color=colorM, linewidth=3)\nfill(l1, l2, color = lnma < gnma ? color.green : color.red, title="Gölgelendirme", transp=90)\nzamanaralik = input (2020, title="Backtest Başlangıç Tarihi")\nal  = crossover (gnma, lnma) and zamanaralik <= year\nsat = crossover (lnma, gnma) and zamanaralik <= year\nplotshape(al,  title = "Giriş",  text = \'Al\',  style = shape.labelup,   location = location.belowbar, color= color.green, textcolor = color.white, transp = 0, size = size.tiny)\nplotshape(sat, title = "Çıkış", text = \'Sat\', style = shape.labeldown, location = location.abovebar, color= color.red,   textcolor = color.white, transp = 0, size = size.tiny)\n\nFromDay    = input(defval = 1, title = "Str. Başlama Tarihi Gün", minval = 1, maxval = 31)\nFromMonth  = input(defval = 1, title = "Str. Başlama Tarihi Ay", minval = 1, maxval = 12)\nFromYear   = input(defval = 2015, title = "Str. Başlama Tarihi Yıl", minval = 2005)\nToDay      = input(defval = 1, title = "Str. Bitiş Tarihi Gün", minval = 1, maxval = 31)\nToMonth    = input(defval = 1, title = "Str. Bitiş Tarihi Ay", minval = 1, maxval = 12)\nToYear     = input(defval = 9999, title = "Str. Bitiş Tarihi Yıl", minval = 2006)\nStart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)\nFinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)\nTimerange() =>\n    time >= Start and time <= Finish ? true : false\nif al\n    strategy.entry("Al", strategy.long, when=Timerange())\nif sat\n    strategy.entry("Sat", strategy.short, when=Timerange())\n'

class SM827C3B6DFA43C8A7(PinePortBase, IStrategy):
    source_id = "SM_827c3b6dfa43c8a7"
    source_file = '趋势交叉交易策略Trend-Bull-Bear-Crossover-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'mav': 'SMA', 'Gbar': 7, 'Abar': 5, 'zamanaralik': 2020, 'FromDay': 1, 'FromMonth': 1, 'FromYear': 2015, 'ToDay': 1, 'ToMonth': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
