"""batch_011 port of 趋势追踪型RafaelZioni动量策略RafaelZioni-Momentum-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2023-08-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n\nstrategy(shorttitle=\'SuperB\', title=\'SuperB By RafaelZioni\', overlay=true)\nlong_only = input(title="Only Long?", defval=true)\n\nhilow = ((high - low)*100)\nopenclose = ((close - open)*100)\nvol = (volume / hilow)\nspreadvol = (openclose * vol)\nVPT = spreadvol + cum(spreadvol)\nwindow_len = 28\n\nv_len = 14\nprice_spread = stdev(high-low, window_len)\n\nvp =  spreadvol + cum(spreadvol)\nsmooth = sma(vp, v_len)\nv_spread = stdev(vp - smooth, window_len)\nshadow = (vp - smooth) / v_spread * price_spread\n\nout = shadow > 0 ? high + shadow : low + shadow\n//\n\nlen = input(10)\n\n\n\nvpt=ema(out,len)\n\n// INPUTS //\nst_mult   = input(1,   title = \' Multiplier\', minval = 0, maxval = 100, step = 0.01)\nst_period = input(10, title = \' Period\',     minval = 1)\n\n// CALCULATIONS //\nup= vpt - (st_mult * atr(st_period))\ndn = vpt + (st_mult * atr(st_period))\nc5=close\n//\n\nfactor = input(title="Factor", defval=0.05, minval=0.01, maxval=5, step=0.01, type=input.float)\n\nhb = 0.00 ,hb := nz(hb[1])\nhl = 0.000, hl := nz(hl[1])\n\nlb = 0.00 ,lb := nz(lb[1])\nl1 = 0.000,l1 := nz(l1[1])\n\nc = 0\nc := nz(c[1]) + 1\n\ntrend = 0,trend := nz(trend[1]),n = dn,x =up\n\n\nif barstate.isfirst\n    c := 0\n    lb := n\n    hb := x                      \n    l1 := c5  \n    hl := c5\n    hl\nif c == 1\n    if x >= hb[1]\n        hb := x\n        hl := c5\n        trend := 1  \n        trend\n    else\n        lb := n\n        l1 := c5 \n        trend := -1 \n        trend\n\nif c > 1\n\n    if trend[1] > 0  \n        hl := max(hl[1], c5)\n        if x >= hb[1] \n            hb := x\n            hb\n        else\n\n            \n            if n < hb[1] - hb[1] * factor \n                lb := n\n                l1 := c5\n\n                trend := -1  \n                trend\n    else\n\n       \n        l1 := min(l1[1], c5 )\n\n        if n <= lb[1] \n            lb := n \n            lb\n        else\n\n           \n            if x > lb[1] + lb[1] * factor\n                hb := x \n                hl := c5\n\n                trend := 1  \n                trend\n\n\n\nv = trend == 1 ? hb : trend == -1 ? lb : na\nplot(v, color=trend == 1 ? color.blue : color.yellow, style=plot.style_circles, linewidth=1, title="trend", transp=0, join=true)\n\n//\n\nlong = trend == 1 and trend[1] == -1 \nshort = trend == -1 and trend[1] == 1 \n//\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nbuy = crossover(last_long, last_short)\nsell = crossover(last_short, last_long)\n\n/////////////// Positions ////////////// \nif long\n    strategy.entry("Buy", long=true)\n    if long_only == false\n        strategy.close("Sell")\n\nif short\n    if long_only == false\n        strategy.entry("Sell", long=false)\n    strategy.close("Buy")\n\n/////////////// Plotting /////////////// \nplotshape(buy, title="buy", text="Buy", color=color.green, style=shape.labelup, location=location.belowbar, size=size.small, textcolor=color.white, transp=0)  //plot for buy icon\nplotshape(sell, title="sell", text="Sell", color=color.red, style=shape.labeldown, location=location.abovebar, size=size.small, textcolor=color.white, transp=0)\n\n\n/////////////// Alerts /////////////// \nalertcondition(buy, title=\'buy\', message=\'Buy\')\nalertcondition(sell, title=\'sell\', message=\'Sell\')'

class SM53F1345112F26E24(PinePortBase, IStrategy):
    source_id = "SM_53f1345112f26e24"
    source_file = '趋势追踪型RafaelZioni动量策略RafaelZioni-Momentum-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'long_only': True, 'len': 10, 'st_mult': 1, 'st_period': 10, 'factor': 0.05}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
