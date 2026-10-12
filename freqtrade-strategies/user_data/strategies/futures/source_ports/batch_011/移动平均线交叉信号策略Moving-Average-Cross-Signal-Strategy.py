"""batch_011 port of 移动平均线交叉信号策略Moving-Average-Cross-Signal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Moving averages-Strategy", overlay=true)\n//Created by user ChrisMoody 4-24-2014\n//Plots The Majority of Moving Averages\n//Defaults to Current Chart Time Frame --- But Can Be Changed to Higher Or Lower Time Frames\n//2nd MA Capability with Show Crosses Feature\n\n//inputs\nsrc = close\nuseCurrentRes = input(true, title="Use Current Chart Resolution?")\nresCustom = input(title="Use Different Timeframe? Uncheck Box Above",defval="D")\nlen = input(20, title="Moving Average Length - LookBack Period")\natype = input(1,minval=1,maxval=7,title="1=SMA, 2=EMA, 3=WMA, 4=HullMA, 5=VWMA, 6=RMA, 7=TEMA")\ncc = input(true,title="Change Color Based On Direction?")\nsmoothe = input(2, minval=1, maxval=10, title="Color Smoothing - 1 = No Smoothing")\ndoma2 = input(false, title="Optional 2nd Moving Average")\nlen2 = input(50, title="Moving Average Length - Optional 2nd MA")\natype2 = input(1,minval=1,maxval=7,title="1=SMA, 2=EMA, 3=WMA, 4=HullMA, 5=VWMA, 6=RMA, 7=TEMA")\ncc2 = input(true,title="Change Color Based On Direction 2nd MA?")\nwarn = input(false, title="***You Can Turn On The Show Dots Parameter Below Without Plotting 2nd MA to See Crosses***")\nwarn2 = input(false, title="***If Using Cross Feature W/O Plotting 2ndMA - Make Sure 2ndMA Parameters are Set Correctly***")\nsd = input(false, title="Show Dots on Cross of Both MA\'s")\n\n\nres = useCurrentRes ? timeframe.period : resCustom\n//hull ma definition\nhullma = wma(2*wma(src, len/2)-wma(src, len), round(sqrt(len)))\n//TEMA definition\nema1 = ema(src, len)\nema2 = ema(ema1, len)\nema3 = ema(ema2, len)\ntema = 3 * (ema1 - ema2) + ema3\n\navg = atype == 1 ? sma(src,len) : atype == 2 ? ema(src,len) : atype == 3 ? wma(src,len) : atype == 4 ? hullma : atype == 5 ? vwma(src, len) : atype == 6 ? rma(src,len) : tema\n//2nd Ma - hull ma definition\nhullma2 = wma(2*wma(src, len2/2)-wma(src, len2), round(sqrt(len2)))\n//2nd MA TEMA definition\nsema1 = ema(src, len2)\nsema2 = ema(sema1, len2)\nsema3 = ema(sema2, len2)\nstema = 3 * (sema1 - sema2) + sema3\n\navg2 = atype2 == 1 ? sma(src,len2) : atype2 == 2 ? ema(src,len2) : atype2 == 3 ? wma(src,len2) : atype2 == 4 ? hullma2 : atype2 == 5 ? vwma(src, len2) : atype2 == 6 ? rma(src,len2) : tema\n\nout = avg \nout_two = avg2\n\nout1 = request.security(syminfo.tickerid, res, out)\nout2 = request.security(syminfo.tickerid, res, out_two)\n\nma_up = out1 >= out1[smoothe]\nma_down = out1 < out1[smoothe]\n\ncol = cc ? ma_up ? lime : ma_down ? red : aqua : aqua\ncol2 = cc2 ? ma_up ? lime : ma_down ? red : aqua : aqua\n\ncircleYPosition = out2\n\nplot(out1, title="Multi-Timeframe Moving Avg", style=line, linewidth=4, color = col)\nplot(doma2 and out2 ? out2 : na, title="2nd Multi-TimeFrame Moving Average", style=circles, linewidth=4, color=col2)\nplot(sd and cross(out1, out2) ? circleYPosition : na,style=cross, linewidth=5, color=yellow)\n\n\nlongCondition = crossover(out1, out1[smoothe])\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = crossunder(out1, out1[smoothe])\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)'

class SM02CC9A5F85D73762(PinePortBase, IStrategy):
    source_id = "SM_02cc9a5f85d73762"
    source_file = '移动平均线交叉信号策略Moving-Average-Cross-Signal-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'useCurrentRes': True, 'resCustom': 'D', 'len': 20, 'atype': 1, 'cc': True, 'smoothe': 2, 'doma2': False, 'len2': 50, 'atype2': 1, 'cc2': True, 'warn': False, 'warn2': False, 'sd': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
