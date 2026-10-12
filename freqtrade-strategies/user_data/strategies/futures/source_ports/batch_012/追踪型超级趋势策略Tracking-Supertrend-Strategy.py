"""batch_012 port of 追踪型超级趋势策略Tracking-Supertrend-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Supertrend TEST 2 Strategy", overlay = true, format=format.price, precision=2)\n\nPeriods = input(title="ATR Period", type=input.integer, defval=4)\nsrc = input(hl2, title="Source")\nMultiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=4.7)\nchangeATR= input(title="Change ATR Calculation Method ?", type=input.bool, defval=true)\nshowsignals = input(title="Show Buy/Sell Signals ?", type=input.bool, defval=true)\nhighlighting = input(title="Highlighter On/Off ?", type=input.bool, defval=true)\ntp=close\nsl=close\n\natr2 = sma(tr, Periods)\natr= changeATR ? atr(Periods) : atr2\nup=src-(Multiplier*atr)\nup1 = nz(up[1],up)\nup := close[1] > up1 ? max(up,up1) : up\ndn=src+(Multiplier*atr)\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? min(dn, dn1) : dn\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\nupPlot = plot(trend == 1 ? up : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=color.green)\nbuySignal = trend == 1 and trend[1] == -1\nplotshape(buySignal ? up : na, title="UpTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.green )\nplotshape(buySignal and showsignals ? up : na, title="Лонг", text="Лонг", location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white )\ndnPlot = plot(trend == 1 ? na : dn, title="Down Trend", style=plot.style_linebr, linewidth=2, color=color.red)\nsellSignal = trend == -1 and trend[1] == 1\nplotshape(sellSignal ? dn : na, title="DownTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.red )\nplotshape(sellSignal and showsignals ? dn : na, title="Шорт", text="Шорт", location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white )\nmPlot = plot(ohlc4, title="", style=plot.style_circles, linewidth=0)\nlongFillColor = highlighting ? (trend == 1 ? color.green : color.white) : color.white\nshortFillColor = highlighting ? (trend == -1 ? color.red : color.white) : color.white\n\nsPeriods=input(title="ATR Period", type=input.integer, defval=8)\nsMultiplier=input(title="dop ATR Multiplier", type=input.float, step=0.1, defval=1.5)\nsatr2 = sma(tr, sPeriods)\nsatr= changeATR ? atr(sPeriods) : satr2\nssup=ohlc4-(sMultiplier*satr)\nssup1 = nz(ssup[1],ssup)\nssup := close[1] > ssup1 ? max(ssup,ssup1) : ssup\nsdn=ohlc4+(sMultiplier*satr)\nsdn1 = nz(sdn[1], sdn)\nsdn := close[1] < sdn1 ? min(sdn, sdn1) : sdn\nstrend = 1\nstrend := nz(strend[1], strend)\nstrend := strend == -1 and close > sdn1 ? 1 : strend == 1 and close < ssup1 ? -1 : strend\nsbuySignal = strend == 1 and strend[1] == -1\nssellSignal = strend == -1 and strend[1] == 1\n\nfPeriods=input(title="ATR Period", type=input.integer, defval=10)\nfMultiplier=input(title="filter ATR Multiplier", type=input.float, step=0.1, defval=5)\nfatr2 = sma(tr, fPeriods)\nfatr= changeATR ? atr(fPeriods) : fatr2\nfup=ohlc4-(fMultiplier*fatr)\nfup1 = nz(fup[1],fup)\nfup := close[1] > fup1 ? max(fup,fup1) : fup\nfdn=ohlc4+(fMultiplier*fatr)\nfdn1 = nz(fdn[1], fdn)\nfdn := close[1] < fdn1 ? min(fdn, fdn1) : fdn\nftrend = 1\nftrend := nz(ftrend[1], ftrend)\nftrend := ftrend == -1 and close > fdn1 ? 1 : ftrend == 1 and close < fup1 ? -1 : ftrend\nfbuySignal = ftrend == 1 and ftrend[1] == -1\nfsellSignal = ftrend == -1 and ftrend[1] == 1\ntcolor=color.new(color.gray,50)\nfdnPlot = plot(ftrend == 1 ? na : fdn, title="Down Trend", style=plot.style_linebr, linewidth=2, color=tcolor)\nfupPlot = plot(ftrend == 1 ? fup : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=tcolor)\n\n\n\nif (strategy.position_size > 0)\n\ttp:=tp[1]\n\tsl:=up\n\tstrategy.exit("Long_TP/SL","Long",limit=tp, stop=sl)\n\t\nif (strategy.position_size < 0)\n\ttp:=tp[1]\n\tsl:=dn\n\tstrategy.exit("Short_TP/SL","Short",limit=tp, stop=sl)\n\n\n\nif ((buySignal and  ftrend==1) or (sbuySignal and trend==1 and  ftrend==1)) \n\ttp:=close+(close-up)*0.382\n    strategy.entry("Long", strategy.long,  limit=tp, comment=tostring(round(tp)))\nif ((sellSignal and ftrend==-1) or (ssellSignal and trend==-1 and  ftrend==-1)) \n\ttp:=close-(dn-close)*0.382\n    strategy.entry("Short", strategy.short, limit=tp, comment=tostring(round(tp)))\n\n'

class SMTrackingSupertrendStrategy539406(PinePortBase, IStrategy):
    source_id = "SM_53940685a63a1238"
    source_file = '追踪型超级趋势策略Tracking-Supertrend-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Periods': 4, 'src': 'hl2', 'Multiplier': 4.7, 'changeATR': True, 'showsignals': True, 'highlighting': True, 'sPeriods': 8, 'sMultiplier': 1.5, 'fPeriods': 10, 'fMultiplier': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
