"""batch_011 port of 超趋势均线BOLL指标策略Supertrend-Bollinger-Bands-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-24 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © KivancOzbilgic\n\n\n//@version=4\nstrategy("SuperTrend STRATEGY", overlay=true)\nPeriods = input(title="ATR Period", type=input.integer, defval=10)\nsrc = input(hl2, title="Source")\nMultiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)\nchangeATR= input(title="Change ATR Calculation Method ?", type=input.bool, defval=true)\nshowsignals = input(title="Show Buy/Sell Signals ?", type=input.bool, defval=false)\nhighlighting = input(title="Highlighter On/Off ?", type=input.bool, defval=true)\nbarcoloring = input(title="Bar Coloring On/Off ?", type=input.bool, defval=true)\natr2 = sma(tr, Periods)\natr= changeATR ? atr(Periods) : atr2\nup=src-(Multiplier*atr)\nup1 = nz(up[1],up)\nup := close[1] > up1 ? max(up,up1) : up\ndn=src+(Multiplier*atr)\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? min(dn, dn1) : dn\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\nupPlot = plot(trend == 1 ? up : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=color.green)\nbuySignal = trend == 1 and trend[1] == -1\nplotshape(buySignal ? up : na, title="UpTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.green, transp=0)\nplotshape(buySignal and showsignals ? up : na, title="Buy", text="Buy", location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white, transp=0)\ndnPlot = plot(trend == 1 ? na : dn, title="Down Trend", style=plot.style_linebr, linewidth=2, color=color.red)\nsellSignal = trend == -1 and trend[1] == 1\nplotshape(sellSignal ? dn : na, title="DownTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.red, transp=0)\nplotshape(sellSignal and showsignals ? dn : na, title="Sell", text="Sell", location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white, transp=0)\nmPlot = plot(ohlc4, title="", style=plot.style_circles, linewidth=0)\nlongFillColor = highlighting ? (trend == 1 ? color.green : color.white) : color.white\nshortFillColor = highlighting ? (trend == -1 ? color.red : color.white) : color.white\nfill(mPlot, upPlot, title="UpTrend Highligter", color=longFillColor)\nfill(mPlot, dnPlot, title="DownTrend Highligter", color=shortFillColor)\nFromMonth = input(defval = 9, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2018, title = "From Year", minval = 999)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999, title = "To Year", minval = 999)\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  \nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)       \nwindow()  => time >= start and time <= finish ? true : false\nlongCondition = buySignal\nif (longCondition)\n    strategy.entry("BUY", strategy.long)\nshortCondition = sellSignal\nif (shortCondition)\n    strategy.entry("SELL", strategy.short)\nbuy1= barssince(buySignal)\nsell1 = barssince(sellSignal)\ncolor1 = buy1[1] < sell1[1] ? color.green : buy1[1] > sell1[1] ? color.red : na\nbarcolor(barcoloring ? color1 : na)'

class SM5F1EA2A1F13B0052(PinePortBase, IStrategy):
    source_id = "SM_5f1ea2a1f13b0052"
    source_file = '超趋势均线BOLL指标策略Supertrend-Bollinger-Bands-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Periods': 10, 'Multiplier': 3.0, 'changeATR': True, 'showsignals': False, 'highlighting': True, 'barcoloring': True, 'FromMonth': 9, 'FromDay': 1, 'FromYear': 2018, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
