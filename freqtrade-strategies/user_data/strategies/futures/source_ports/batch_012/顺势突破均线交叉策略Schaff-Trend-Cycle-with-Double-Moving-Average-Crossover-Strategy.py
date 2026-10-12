"""batch_012 port of 顺势突破均线交叉策略Schaff-Trend-Cycle-with-Double-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-11 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// Shaff Trend Cycle coded by Alex Orekhov (everget)\n// Strategy and its additional conditions provided by greenmask\n// Schaff Trend Cycle script may be freely distributed under the MIT license.\nstrategy("STC", shorttitle="STC")\n\nfastLength = input(title="MACD Fast Length", type=input.integer, defval=23)\nslowLength = input(title="MACD Slow Length", type=input.integer, defval=50)\ncycleLength = input(title="Cycle Length", type=input.integer, defval=10)\nd1Length = input(title="1st %D Length", type=input.integer, defval=3)\nd2Length = input(title="2nd %D Length", type=input.integer, defval=3)\nsrc = close\nhighlightBreakouts = input(title="Highlight Breakouts ?", type=input.bool, defval=true)\n\nmacd = ema(src, fastLength) - ema(src, slowLength)\nk = nz(fixnan(stoch(macd, macd, macd, cycleLength)))\nd = ema(k, d1Length)\nkd = nz(fixnan(stoch(d, d, d, cycleLength)))\nstc = ema(kd, d2Length)\nstc := \tstc > 100 ? 100 : stc < 0 ? 0 : stc\nstcColor = not highlightBreakouts ? (stc > stc[1] ? color.green : color.red) : #ff3013\nstcPlot = plot(stc, title="STC", color=stcColor, transp=0)\nupper = 75\nlower = 25\ntransparent = color.new(color.white, 100)\nupperLevel = plot(upper, title="Upper", color=color.gray)\nhline(50, title="Middle", linestyle=hline.style_dotted)\nlowerLevel = plot(lower, title="Lower", color=color.gray)\n\nfill(upperLevel, lowerLevel, color=#f9cb9c, transp=90)\n\nupperFillColor = stc > upper and highlightBreakouts ? color.green : transparent\nlowerFillColor = stc < lower and highlightBreakouts ? color.red : transparent\n\nfill(upperLevel, stcPlot, color=upperFillColor, transp=80)\nfill(lowerLevel, stcPlot, color=lowerFillColor, transp=80)\nstrategy.initial_capital = 50000\nordersize=floor(strategy.initial_capital/close)\ntargetvalue = input(title="Target/stop", type=input.integer, defval=400)\n\nma1length = input(title="SMA1", type=input.integer, defval=35)\nma2length = input(title="SMA2", type=input.integer, defval=200)\nma1 = ema(close,ma1length)\nma2 = ema(close,ma2length)\n\nbullbuy = crossover(stc, lower) and ma1>ma2 and close>ma1\nbearsell = crossunder(stc, upper) and ma1<ma2 and close<ma1\n\nif (bullbuy)\n    strategy.entry("Riposte", strategy.long, ordersize)\n    strategy.exit( "Riposte close", from_entry="Riposte", qty_percent=100, profit=targetvalue,loss=targetvalue)\n\nif (bearsell)\n    strategy.entry("Riposte", strategy.short, ordersize)\n    strategy.exit( "Riposte close", from_entry="Riposte", qty_percent=100, profit=targetvalue,loss=targetvalue)\n\n//plotshape(bullbuy,  title= "Purple", location=location.belowbar, color=#006600, transp=0, style=shape.circle, size=size.tiny, text="Riposte")\n//plotshape(bearsell,  title= "Purple", location=location.abovebar, color=#006600, transp=0, style=shape.circle, size=size.tiny, text="Riposte")\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'

class SMSchaffTrendCyclewithDoubleMovingAverageCrossoverStrateg3fb625(PinePortBase, IStrategy):
    source_id = "SM_3fb62571baafd28e"
    source_file = '顺势突破均线交叉策略Schaff-Trend-Cycle-with-Double-Moving-Average-Crossover-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'fastLength': 23, 'slowLength': 50, 'cycleLength': 10, 'd1Length': 3, 'd2Length': 3, 'highlightBreakouts': True, 'targetvalue': 400, 'ma1length': 35, 'ma2length': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
