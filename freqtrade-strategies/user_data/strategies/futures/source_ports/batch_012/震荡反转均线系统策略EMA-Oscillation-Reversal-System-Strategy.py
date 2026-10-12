"""batch_012 port of 震荡反转均线系统策略EMA-Oscillation-Reversal-System-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-11 00:00:00\nend: 2023-10-17 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © juanchez\n\n//@version=4\nstrategy("CHI", overlay = true, close_entries_rule = "ANY")\n\nn = input(title= "highest high o lowest low period", defval= 22)\nf= input(title= "multiplicador", defval= 4)\nlong = highest(high, n) - atr(n)*f\nshort= lowest(low, n) + atr(n)*f\nplot(long, color= color.red)\nplot(short, color= color.green)\n\n//moving averages\nperiod= input(title= "moving averages period", defval= 50)\nperiod2= input(title= "moving averages period2", defval= 20)\ntype= input(title= "moving averages type", options= ["sma", "ema"], defval= "ema")\n\n//moving average function\nmo(p, t) =>\n    if t == "sma"\n        sma(close[barstate.islast ? 1: 0], p)\n    else  if t== "ema"\n        ema(close[barstate.islast ? 1: 0], p)\n\nm= mo(period, type)\nm2= mo(period2, type)\n\ntrend= m2 > m \n\nplot(m, color = color.maroon, linewidth = 3)\nplot(m2, linewidth= 3)\n\n\n//BOLLINGER BANDS ENTRIES\nbb1_period= input(title= "Bollinger bands 1 period", defval=40, minval=1)\nbb1_source=input(title="Bollinger band 1 source", defval=close)\nbb1_multi=input(title="Bollinger Bands 1 factor", defval=2, minval=1, step=0.1)\nshow_bb1= input(title="Show Bollinger bands 1", defval=false)\n//BOLLINGER BANDS\n_bb(src, lenght, multi)=>\n    float moving_avg= sma(src[barstate.islast? 1: 0], lenght)\n    float deviation= stdev(src[barstate.islast? 1: 0], lenght)\n    float lowerband = moving_avg - deviation*multi\n    float upperband = moving_avg + deviation*multi\n    \n    [moving_avg, lowerband, upperband]\n    \n[bb1, lowerband1, upperband1]= _bb(bb1_source,  bb1_period, bb1_multi)\n\n//FIRST BAND    \nplot(show_bb1? bb1 : na, title="BB1 Moving average", linewidth= 3, color= color.fuchsia)\nplot(show_bb1? upperband1 : na, title="BB1 Upper Band", linewidth= 3, color= color.green)\nplot(show_bb1? lowerband1 : na, title="BB1 Lower Band", linewidth= 3, color= color.red)\n\n//BB\'s Width threshold \nthresh= input(title= "widen %", defval= 9, minval = 0, step = 1, maxval= 100)\n\nwidht= (upperband1 - lowerband1)/bb1\nroc= change(widht)/widht[1]*100\ncross=crossover(roc, thresh)\n\n// entry\n//long\nelong= input(true, title= "enable long")\nlongcondition= m2 > m and cross and elong\n\n//short\neshort= input(true, title= "enable short")\nshortcondition= m2 < m and cross and eshort\n\n\nplotshape(longcondition? true: false , location= location.belowbar, style= shape.labelup, size= size.small, color= color.green, text= "Buy", textcolor= color.white)\nplotshape(shortcondition? true: false , location= location.abovebar, style= shape.labeldown, size= size.small, color= color.red, text= "Sell", textcolor= color.white)\n\nout= crossunder(close, long)\noutt= crossover(close, short)\n\nstrategy.entry("long", strategy.long, when = longcondition)\nstrategy.close("long", when = out)\n\nstrategy.entry("short", strategy.short, when = shortcondition)\nstrategy.close("short", when = outt)\n'

class SMEMAOscillationReversalSystemStrategye616ec(PinePortBase, IStrategy):
    source_id = "SM_e616ecaf7cd20781"
    source_file = '震荡反转均线系统策略EMA-Oscillation-Reversal-System-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'n': 22, 'f': 4, 'period': 50, 'period2': 20, 'type': 'ema', 'bb1_period': 40, 'bb1_source': 'close', 'bb1_multi': 2, 'show_bb1': False, 'thresh': 9, 'elong': True, 'eshort': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
