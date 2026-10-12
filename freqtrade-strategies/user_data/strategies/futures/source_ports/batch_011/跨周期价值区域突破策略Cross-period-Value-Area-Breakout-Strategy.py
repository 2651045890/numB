"""batch_011 port of 跨周期价值区域突破策略Cross-period-Value-Area-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-05 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\nstrategy("Swing MTF", shorttitle="Swing MTF", overlay=false, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, initial_capital = 10000, slippage = 5)\n//\notf_period = input(defval=2, title="Look Back Period (2nd Timeframe)")\notf = input(defval="180", title="Second Momentum Timeframe")\n\n// Function to dectect a new bar\nis_newbar(res) =>\n    t = time(res)\n    change(t) != 0 ? true : false\n\n// Check how many bars are in our upper timeframe\nsince_new_bar = barssince(is_newbar(otf))\notf_total_bars = na\notf_total_bars := since_new_bar == 0 ? since_new_bar[1] : otf_total_bars[1]\n\n//Calculate RSI Values\nctf_rsi = rsi(open, otf_period)\n\nbreakline=input(title="Breaks in lines", defval = true, type=bool)\n\nso = request.security(syminfo.tickerid, otf, rsi(open, otf_period))\nsc = request.security(syminfo.tickerid, otf, rsi(close, otf_period))\n\n\nfinal_otf_so = na\nfinal_otf_so := barstate.isrealtime ? since_new_bar == otf_total_bars ? so : final_otf_so[1] : so\n\nfinal_otf_sc = na\nfinal_otf_sc := barstate.isrealtime ? since_new_bar == otf_total_bars ? sc : final_otf_sc[1] : sc\n\nbarsback = input(11, title=\'Bars back to check for a swing\')\n// showsig = input(false, title=\'Show Signal Markers\')\n \nswing_detection(index)=>\n    swing_high = false\n    swing_low = false\n    start = (index*2) - 1 // -1 so we have an even number of\n    swing_point_high = final_otf_so[index]\n    swing_point_low = final_otf_sc[index]\n    \n    //Swing Highs\n    for i = 0 to start\n        swing_high := true\n        if i < index \n            if final_otf_so[i] > swing_point_high \n                swing_high := false\n                break\n        // Have to do checks before pivot and after seperately because we can get\n        // two highs of the same value in a row. Notice the > and >= difference\n        if i > index\n            if final_otf_so[i] >= swing_point_high \n                swing_high := false\n                break\n        \n    //Swing lows\n    for i = 0 to start\n        swing_low := true\n        if i < index\n            if final_otf_sc[i] < swing_point_low \n                swing_low := false\n                break  \n        // Have to do checks before pivot and after seperately because we can get\n        // two lows of the same value in a row. Notice the > and >= difference\n        if i > index\n            if final_otf_sc[i] <= swing_point_low \n                swing_low := false\n                break \n        \n    [swing_high, swing_low]\n \n// Check for a swing\n[swing_high, swing_low] = swing_detection(barsback)\n \n\nlong =  final_otf_so > final_otf_sc\nshort = final_otf_so < final_otf_sc\n\nif swing_low and long\n    strategy.entry("My Long Entry Id", strategy.long)\n\n\nif swing_high and short\n    strategy.entry("My Short Entry Id", strategy.short)'

class SM83081E1C2C0128CF(PinePortBase, IStrategy):
    source_id = "SM_83081e1c2c0128cf"
    source_file = '跨周期价值区域突破策略Cross-period-Value-Area-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'otf_period': 2, 'otf': '180', 'breakline': True, 'barsback': 11}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'loop', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
