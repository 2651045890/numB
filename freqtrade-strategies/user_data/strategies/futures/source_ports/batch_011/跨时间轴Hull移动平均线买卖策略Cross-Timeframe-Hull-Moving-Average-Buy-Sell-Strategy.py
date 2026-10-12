"""batch_011 port of 跨时间轴Hull移动平均线买卖策略Cross-Timeframe-Hull-Moving-Average-Buy-Sell-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-07 00:00:00\nend: 2023-11-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//\nstrategy("wtfBUYorSELLffs",overlay=true,currency="USD",initial_capital=100000,default_qty_type=strategy.percent_of_equity,default_qty_value=100,commission_type=strategy.commission.percent,commission_value=0.1)\nPeriod=input(title="Hull MA Period",type=input.integer,defval=6,minval=1)\nResolution2=input(title="HMA2 Resolution", type=input.resolution,defval="60")\nResolution3=input(title="HMA3 Resolution", type=input.resolution,defval="240")\nPrice=input(title="Source of Price",type=input.source,defval=open)\nxOffset       = input(40, title="Panel offset (X-Axis)")\nyOffset       = input(0, title="Panel offset (y-Axis)")\nlightgray = #D3D3D3FF\npnlTextColor = color.silver\npnlColor = color.black\nHMA = hma(Price,Period)\nHMA2 = security(syminfo.tickerid, Resolution2, HMA,barmerge.gaps_off,barmerge.lookahead_off)\nHMA3 = security(syminfo.tickerid, Resolution3, HMA,barmerge.gaps_off,barmerge.lookahead_off) \nHUP = HMA > HMA[1]\nH1UP = security(syminfo.tickerid, Resolution2, HUP,barmerge.gaps_off,barmerge.lookahead_off)\nH2UP = security(syminfo.tickerid, Resolution3, HUP,barmerge.gaps_off,barmerge.lookahead_off) \n\nint barSize = timeframe.isdaily ? timeframe.multiplier*86400000 : \n           timeframe.isseconds? timeframe.multiplier*1000 :\n           timeframe.isminutes? timeframe.multiplier*60000 : (time[0]-time[1])\nint   lapos_x = timenow + barSize*xOffset\nfloat lapos_y = highest(20) + yOffset*syminfo.mintick * syminfo.pointvalue\nf_draw_infopanel(_x, _y, _line, _text)=>\n    _rep_text = ""\n    for _l = 0 to _line\n        _rep_text := _rep_text + "\\n"\n    _rep_text := _rep_text + _text\n    // var label _la = na\n    // label.delete(_la)\n//     _la := label.new(\n//          x=_x, y=_y, \n//          text=_rep_text, xloc=xloc.bar_time, yloc=yloc.price, \n//          color=pnlColor, style=label.style_labelup, textcolor=pnlTextColor, size=size.normal)\n// f_draw_infopanel(lapos_x, lapos_y, 8, "╚═══════════════════════╝")\nf_draw_infopanel(lapos_x, lapos_y, 6,  "HMA3 on TF " + Resolution3 + "  = " + tostring(HMA3,"#.####") + (H2UP ? " BUY" : " SELL"))\nf_draw_infopanel(lapos_x, lapos_y, 4,  "HMA2 on TF " + Resolution2 + "  = " +  tostring(HMA2,"#.####") + (H1UP ? " BUY" : " SELL"))\nf_draw_infopanel(lapos_x, lapos_y, 2,  "HMA1 on TF " + timeframe.period + "  = " + tostring(HMA,"#.####") + (HUP ? " BUY" : " SELL"))\nf_draw_infopanel(lapos_x, lapos_y, 0,  "╔═════════ HMA(" + tostring(Period,"#") +") ════════╗")\nchange_color=HMA>HMA3?color.green:color.red\nchange_color2=HMA2>HMA3?color.lime:color.yellow\nplot1=plot(HMA3,color=change_color2,title="3 Hull MA Line",linewidth=2,transp=75)\nplot2=plot(HMA2,color=change_color,title="2 Hull MA Line",linewidth=2,transp=75)\nplot3=plot(HMA,color=color.white,title="Hull MA Line",linewidth=2,transp=75)\nfill(plot1,plot3,color=change_color,transp=90)\nfill(plot2,plot3,color=change_color2,transp=75)\nif (H2UP and H1UP and HUP)\n    strategy.entry("BUY",strategy.long)\nif (not H2UP and not H1UP and not HUP)\n    strategy.entry("SELL",strategy.short)'

class SM5397DA892394A0B7(PinePortBase, IStrategy):
    source_id = "SM_5397da892394a0b7"
    source_file = '跨时间轴Hull移动平均线买卖策略Cross-Timeframe-Hull-Moving-Average-Buy-Sell-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Period': 6, 'Resolution2': '60', 'Resolution3': '240', 'xOffset': 40, 'yOffset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'loop', 'var_state', 'timeframe', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
