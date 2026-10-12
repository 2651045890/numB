"""batch_011 port of 超趋势盲从策略Supertrend-Blind-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-06 00:00:00\nend: 2023-12-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Supertrend blind follow", overlay=true)\n\nFactor=input(3, minval=1,maxval = 100)\nPd=input(7, minval=1,maxval = 100)\n\n\nUp=hl2-(Factor*atr(Pd))\nDn=hl2+(Factor*atr(Pd))\n\n\nTrendUp=close[1]>TrendUp[1]? max(Up,TrendUp[1]) : Up\nTrendDown=close[1]<TrendDown[1]? min(Dn,TrendDown[1]) : Dn\n\nTrend = close > TrendDown[1] ? 1: close< TrendUp[1]? -1: nz(Trend[1],1)\nTsl = Trend==1? TrendUp: TrendDown\n\nlinecolor = Trend == 1 ? green : red\n\nplot(Tsl, color = linecolor , style = line , linewidth = 2,title = "SuperTrend")\n\nplotshape(cross(close,Tsl) and close>Tsl , "Up Arrow", shape.triangleup,location.belowbar,green,0,0)\nplotshape(cross(Tsl,close) and close<Tsl , "Down Arrow", shape.triangledown , location.abovebar, red,0,0)\n//plot(Trend==1 and Trend[1]==-1,color = linecolor, style = circles, linewidth = 3,title="Trend")\n\nplotarrow(Trend == 1 and Trend[1] == -1 ? Trend : na, title="Up Entry Arrow", colorup=lime, maxheight=60, minheight=50, transp=0)\nplotarrow(Trend == -1 and Trend[1] == 1 ? Trend : na, title="Down Entry Arrow", colordown=red, maxheight=60, minheight=50, transp=0)\n\nlongCondition = cross(close,Tsl) and close>Tsl\nif (longCondition)\n    strategy.entry("long", strategy.long)\nshortCondition = cross(Tsl,close) and close<Tsl\nif (shortCondition)\n    strategy.entry("short", strategy.short)\n\n'

class SM7A5F0B4BB8ED8063(PinePortBase, IStrategy):
    source_id = "SM_7a5f0b4bb8ed8063"
    source_file = '超趋势盲从策略Supertrend-Blind-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Factor': 3, 'Pd': 7}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
