"""batch_011 port of 移动平均线趋势跟踪策略Trend-Following-SMA-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-26 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("SMA STRATEGY", shorttitle="SMA TREND", overlay=true, calc_on_order_fills=true)\nlength = input(title="Length", type=input.integer, defval=50)\nsrc_=input(close, title="Source", type=input.source)\nmult=input(6.0, title="Mult")\nbarc=input(true, title="Use barcolor?")\nplots=input(false, title="Show plots?")\ntri=input(false, title="Use triangles?")\n\n\nr(src, n)=>\n    s = 0.0\n    for i = 0 to n-1\n        s := s + ((n-(i*2+1))/2)*src[i]\n    x=s/(n*(n+1))\n    x\n\nl=sma(low, length)\nh=sma(high, length)\nlr= l+mult*r(low, length)\nhr= h+mult*r(high, length)\n\ntrend=0\ntrend:=src_ > lr and src_ > hr ? 1 : src_ < lr and src_ < hr ? -1 : trend[1]\n\nstrategy.close("Long", when=trend==-1)\nstrategy.close("Short", when=trend==1)\nstrategy.entry("Long", strategy.long, when=trend==1 and src_>h)\nstrategy.entry("Short", strategy.short, when=trend==-1 and src_<l)\n\nlong=0\nshort=0\nlong:= trend==1 and src_>h ? 1 : trend==-1 ? -1 : long[1]\nshort:= trend==-1 and src_<l ? 1 : trend==1 ? -1 : short[1]\n\nbarcolor(barc? (long>0? color.green : short>0? color.red : trend>0? color.orange: trend<0 ? color.white : color.blue) : na)\nplotshape(tri? close : na, style= shape.diamond, color= long>0? color.green : short>0? color.red : trend>0? color.orange: trend<0 ? color.white : color.blue, location=location.top)\n\n//shortenter=\na1=plot(plots? l : na, color=color.blue, linewidth=1)\n//longenter=\na2=plot(plots? h : na, color=color.blue, linewidth=1)\nfill(a1, a2, color=color.blue)\n//stopshort=\nb1=plot(plots? hr : na, color=color.navy, linewidth=1)\n//stoplong=\nb2=plot(plots? lr : na, color=color.navy, linewidth=1)\nfill(b1, b2, color=color.navy)'

class SMB413CC94612FBF15(PinePortBase, IStrategy):
    source_id = "SM_b413cc94612fbf15"
    source_file = '移动平均线趋势跟踪策略Trend-Following-SMA-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 50, 'mult': 6.0, 'barc': True, 'plots': False, 'tri': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
