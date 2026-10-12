"""batch_011 port of 自适应布林通道趋势跟踪策略Adaptive-Bollinger-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-16 00:00:00\nend: 2023-11-09 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Linear Regression (Backtest / Trailing Stop)",overlay=true)\nclose_price = close[0]\n\nlen = input(40)\nlinear_reg = linreg(close_price, len, 0)\n\ncalculationToPlotAverageMeanLine=linear_reg\nuseUpperDeviation = input(true, "Upper Deviation", bool)\nuseLowerDeviation = input(true, "Lower Deviation", bool)\nratio2=input(defval=2,title=" Ratio 2")\navg=atr(len)\nr2=avg*ratio2\ntop=linear_reg+r2\nbott=linear_reg-r2\n\ncalculationToPlotUpperLine=top\ncalculationToPlotLowerLine=bott\n\nplotUpperDeviationLine = plot(not useUpperDeviation ? na : calculationToPlotUpperLine, color=color(blue,0))\nplotAverageMeanLine = plot(calculationToPlotAverageMeanLine, color=color(olive,0))\nplotLowererDeviationLine = plot(not useLowerDeviation ? na : calculationToPlotLowerLine, color=color(red,0))\nfill(plotUpperDeviationLine, plotAverageMeanLine, color=color(blue,85))\nfill(plotLowererDeviationLine, plotAverageMeanLine, color=color(red,85))\n\n\n//\nlength = input(title="linear Length",  defval=40, minval=1)\nmultiplier = input(title="linear Deviation", type=float, defval=2, minval=1)\noverbought = input(title="Overbought",  defval=1, minval=1)\noversold = input(title="Oversold",  defval=0, minval=1)\ncustom_timeframe = input(title="Use another Timeframe?", type=bool, defval=false)\nhighTimeFrame = input(title="Select The Timeframe",  defval="60")\nres1 = custom_timeframe ? highTimeFrame : timeframe.period\n\nfixedSL = input(title="SL Activation", defval=70)\ntrailSL = input(title="SL Trigger", defval=10)\nfixedTP = input(title="TP Activation", defval=50)\ntrailTP = input(title="TP Trigger", defval=10)\n\n// === INPUT BACKTEST RANGE ===\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2019, title = "From Year", minval = 2015)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999, title = "To Year", minval = 2015)\n\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false // create function "within window of time"\n\nsmabasis = linreg(close_price, length, 0)\nstdev = stdev(close, length)\ncierre = request.security(syminfo.tickerid, res1, close, false)\nalta = request.security(syminfo.tickerid, res1, high, false)\nbaja = request.security(syminfo.tickerid, res1, low, false)\nbasis1 = request.security(syminfo.tickerid, res1, smabasis, false)\nstdevb = request.security(syminfo.tickerid, res1, stdev, false)\ndev = multiplier * stdevb // stdev(cierre, length)\nupper = basis1 + dev\nlower = basis1 - dev\n\nbbr = (cierre - lower)/(upper - lower)\n\n// plot(bbr)\n\n// // MARCA LAS RESISTENCIAS\npintarojo = 0.0\npintarojo := nz(pintarojo[1])\npintarojo := bbr[1] > overbought and bbr < overbought ? alta[1] :  nz(pintarojo[1])\np = plot(pintarojo, color = red, style=circles, linewidth=2)\n\n// // MARCA LOS SOPORTES\npintaverde = 0.0\npintaverde := nz(pintaverde[1])\npintaverde := bbr[1] < oversold and bbr > oversold ? baja[1] :  nz(pintaverde[1])\ng = plot(pintaverde, color = black, style=circles, linewidth=2)\nzz= crossover(pintaverde,pintaverde[1]) or crossunder(pintaverde,pintaverde[1])\nkp= crossover(pintarojo,pintarojo[1]) or crossunder(pintarojo,pintarojo[1]) \nplotshape(zz,  title="buy", style=shape.triangleup,location=location.belowbar, color=green, transp=0, size=size.small)\nplotshape(kp, title="sell", style=shape.triangledown,location=location.abovebar, color=red, transp=0, size=size.small)\n\n\nstrategy.entry("BUY", strategy.long, qty=10, oca_name="BUY",  when=zz and window())\nstrategy.exit("B.Exit", "BUY", qty_percent = 100, loss=fixedSL, trail_offset=trailTP, trail_points=fixedTP)\n\nstrategy.entry("SELL", strategy.short, qty=10, oca_name="SELL",  when=kp and window())\nstrategy.exit("S.Exit", "SELL", qty_percent = 100, loss=fixedSL, trail_offset=trailSL, trail_points=fixedTP)\n'

class SM3396FD73C7C1A1DC(PinePortBase, IStrategy):
    source_id = "SM_3396fd73c7c1a1dc"
    source_file = '自适应布林通道趋势跟踪策略Adaptive-Bollinger-Trend-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'len': 40, 'useUpperDeviation': True, 'useLowerDeviation': True, 'ratio2': 2, 'length': 40, 'multiplier': 2, 'overbought': 1, 'oversold': 0, 'custom_timeframe': False, 'highTimeFrame': '60', 'fixedSL': 70, 'trailSL': 10, 'fixedTP': 50, 'trailTP': 10, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2019, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'func', 'exit_order', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
