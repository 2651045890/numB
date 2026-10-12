"""batch_011 port of 经典双重趋势追踪策略Classic-Dual-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-01 00:00:00\nend: 2023-10-31 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(title="swing trade", shorttitle="vinay_swing", overlay=true)\npf = input(false,title="Show Filtered Pivots")\nsd = input(true, title="Show Daily Pivots?")\n\n//moving average\nlen = input(50, minval=1, title="Length")\nsrc = input(close, title="Source")\nout = ema(src, len)\n\n//RSI INPUT\nlength = input( 7 )\noverSold = input( 20 )\noverBought = input( 80 )\nprice = close\nvrsi = rsi(price, length)\n\n\n// Classic Pivot\npivot = (high + low + close ) / 3.0\n// Filter Cr\nbull= pivot > (pivot + pivot[1]) / 2 + .0025\nbear= pivot < (pivot + pivot[1]) / 2 - .0025\n// Classic Pivots\nr1 = pf and bear ? pivot + (pivot - low) : pf and bull ? pivot + (high - low) : pivot + (pivot - low)\ns1 = pf and bull ? pivot - (high - pivot) : pf and bear ? pivot - (high - low) : pivot - (high - pivot)\nr2 = pf ? na : pivot + (high - low)\ns2 = pf ? na : pivot - (high - low)\nBC = (high + low) / 2.0\nTC = (pivot - BC) + pivot\n\n//Pivot Average Calculation\nsmaP = sma(pivot, 3)\n\n//Daily Pivots \ndtime_pivot = request.security(syminfo.tickerid, \'D\', pivot[1])\ndtime_pivotAvg = request.security(syminfo.tickerid, \'D\', smaP[1])\ndtime_r1 = request.security(syminfo.tickerid, \'D\', r1[1]) \ndtime_s1 = request.security(syminfo.tickerid, \'D\', s1[1]) \ndtime_r2 = request.security(syminfo.tickerid, \'D\', r2[1]) \ndtime_s2 = request.security(syminfo.tickerid, \'D\', s2[1])\ndtime_BC = request.security(syminfo.tickerid, \'D\', BC[1])\ndtime_TC = request.security(syminfo.tickerid, \'D\', TC[1])\n\noffs_daily = 0\nplot(sd and dtime_pivot ? dtime_pivot : na, title="Daily Pivot",style=circles, color=fuchsia,linewidth=1) \nplot(sd and dtime_r1 ? dtime_r1 : na, title="Daily R1",style=circles, color=#DC143C,linewidth=1) \nplot(sd and dtime_s1 ? dtime_s1 : na, title="Daily S1",style=circles, color=lime,linewidth=1) \nplot(sd and dtime_r2 ? dtime_r2 : na, title="Daily R2",style=circles, color=maroon,linewidth=1) \nplot(sd and dtime_s2 ? dtime_s2 : na, title="Daily S2",style=circles, color=#228B22,linewidth=1)\nplot(sd and dtime_BC ? dtime_BC : na, title="Daily BC",style=circles, color=black,linewidth=1)\nplot(sd and dtime_TC ? dtime_TC : na, title="Daily TC",style=circles, color=black,linewidth=1)\n\nbull1=  (close > dtime_r2)\nbull2= (low < dtime_pivot) or (low < dtime_s1) \nbull3= dtime_pivot > dtime_pivot[1]\nbullishenglufing=bull2 and bull3\nbullishenglufing1=bull1 and (close > out) and (crossover(vrsi, overBought))\nlongCondition = bull1[1] and ((low < dtime_TC) or (low < dtime_BC) or (low < dtime_s1))\n\nbear1=  (close < dtime_s2)\nbear2= (high > dtime_pivot) or (high < dtime_r1) \nbear3= dtime_pivot < dtime_pivot[1]\nbearishenglufing=bear2 and bear3\nbearishenglufing1=bear1 and (close < out) and (crossunder(vrsi, overSold))\nshortCondition = bear1[1] and ((high > dtime_BC) or (high > dtime_TC) or (high > dtime_r1))\n\nplotshape(bullishenglufing, style = shape.triangleup, location = location.belowbar, color = green, size = size.tiny)\nplotshape(bearishenglufing, style = shape.triangledown, location = location.abovebar, color = red, size = size.tiny)\n\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)\n'

class SM63886B5D448BB768(PinePortBase, IStrategy):
    source_id = "SM_63886b5d448bb768"
    source_file = '经典双重趋势追踪策略Classic-Dual-Trend-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'pf': False, 'sd': True, 'len': 50, 'length': 7, 'overSold': 20, 'overBought': 80}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
