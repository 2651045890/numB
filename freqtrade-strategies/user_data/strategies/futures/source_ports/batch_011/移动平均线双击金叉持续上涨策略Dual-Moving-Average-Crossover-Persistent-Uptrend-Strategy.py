"""batch_011 port of 移动平均线双击金叉持续上涨策略Dual-Moving-Average-Crossover-Persistent-Uptrend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-05 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//written by markjames12210@gmail.com\n//@version=5\nstrategy(title="MJ-Dual Moving Average",initial_capital=10000,overlay=false)\n\n// import TradingView/ZigZag/6 as ZigZagLib \n\n// // Create Zig Zag instance from user settings.\n// var zigZag = ZigZagLib.newInstance(\n//   ZigZagLib.Settings.new(\n//       input.float(5.0, "Price deviation for reversals (%)", 0.00001, 100.0, 0.5, "0.00001 - 100"),\n//       input.int(10, "Pivot legs", 2),\n//       input(#2962FF, "Line color"),\n//       input(true, "Extend to last bar"),\n//       input(true, "Display reversal price"),\n//       input(true, "Display cumulative volume"),\n//       input(true, "Display reversal price change", inline = "priceRev"),\n//       input.string("Absolute", "", ["Absolute", "Percent"], inline = "priceRev"),\n//       true)\n//  )\n\n// // Update \'zigZag\' object on each bar with new \u200bpivots, \u200bvolume, lines, labels.\n// zigZag.update()\n// // plot(zigZag.pivots, "zigZag")\n\nma1= ta.sma(close,8)\nma2= ta.sma(close,21)\n\nangleCriteria = input.int(title="Angle", defval=7, minval=1, maxval=13)\n\ni_lookback   = input.int(2,     "Angle Period", minval = 1)\ni_atrPeriod  = input.int(10,    "ATR Period",   minval = 1)\ni_angleLevel = input.int(6,     "Angle Level",  minval = 1)\ni_maSource   = input.source(close, "MA Source")\nTP = input.float(1, "TP", minval = 0.1)\nSL = input.float(1, "SL", minval = 0.1)\n\nf_angle(_src, _lookback, _atrPeriod) =>\n    rad2degree = 180 / 3.141592653589793238462643  //pi \n    ang = rad2degree * math.atan((_src[0] - _src[_lookback]) / ta.atr(_atrPeriod)/_lookback)\n    ang\n_angle = f_angle(ma2, i_lookback, i_atrPeriod)\nplot(ta.atr(i_atrPeriod), "atr")\n// plot(ma1,color=#FF0000)\n// plot(ma2,color=#00FF00)\n\ncrosso=ta.crossover(ma1,ma2) \ncrossu=ta.crossunder(ma1,ma2)\n\n_lookback = 15\n\nf_somethingHappened(_cond, _lookback) =>\n    bool _crossed = false\n    for i = 1 to _lookback\n        if _cond[i]\n            _crossed := true\n    _crossed\n    \nlongcrossed = f_somethingHappened(crosso,_lookback)\nshortcrossed = f_somethingHappened(crossu,_lookback)\n\natr_factor = 1\natr = ta.atr(i_atrPeriod)\ne = atr * atr_factor \n\nafr = close \nafr := nz(afr[1], afr)\n\natr_factoryHigh = close + e\natr_factoryLow = close - e \n\nif atr_factoryLow > afr \n    afr := atr_factoryLow\nif atr_factoryHigh < afr \n    afr := atr_factoryHigh\n\n// plot(afr, "afr", display = display.data_window)\n// plot(atr_factoryHigh, "afr", color = color.yellow, display = display.all)\n// plot(atr_factoryLow, "afr", color = color.green, display = display.all)\n\n\ninLong() => strategy.position_size > 0\ninShort() => strategy.position_size < 0\ninZero() => not inLong() and not inShort()\n\nlong = longcrossed and _angle > angleCriteria\nshort= shortcrossed and _angle < -(angleCriteria)\n\nplotshape(long, "Buy", shape.arrowup, location.belowbar, color = #FF0000)\nplotshape(short, "Sell", shape.arrowdown, location.abovebar, color = #00FF00)\n\nvar longTp = 0.0\nvar longSl = 0.0\nvar shortTp = 0.0\nvar shortSl = 0.0\n[b_middle, b_high, b_low] = ta.bb(close, 20, 2)\nentry_price = strategy.opentrades.entry_price(0)\n\nif inZero()\n    if short\n        longTp := close * (1 + TP/100)\n        longSl := close * (1 - SL/100)\n        strategy.entry("LONG",strategy.long, comment = "tp:" + str.tostring(longTp) + " sl:" + str.tostring(longSl))\n    if long\n        shortTp := close * (1 - TP/100)\n        shortSl := close * (1 + SL/100)\n        strategy.entry("SHORT",strategy.short, comment = "tp:" + str.tostring(shortTp) + " sl:" + str.tostring(shortSl))\n\nif inLong()\n    // if close - entry_price > close * 0.005\n    //     longSl := entry_price + close * 0.001\n    if high > longTp\n        strategy.close("LONG")\n        if (close - open) > close * 0.014\n            shortTp := close * (1 - TP/100)\n            shortSl := close * (1 + SL/100)\n            strategy.entry("SHORT",strategy.short, comment = "tp:" + str.tostring(shortTp) + " sl:" + str.tostring(shortSl))\n\n    if close < longSl\n        strategy.close("LONG")\n    if open >= b_high and close >= b_high\n        strategy.close("LONG")\n    // if high > b_high and entry_price < high\n    //     strategy.close("LONG")\n\n\nif inShort()\n    // if entry_price - close > close * 0.005\n    //     shortSl := entry_price - close * 0.001\n    if low < shortTp\n        strategy.close("SHORT")\n        if (open - close) > close * 0.014\n            longTp := close * (1 + TP/100)\n            longSl := close * (1 - SL/100)\n            strategy.entry("LONG",strategy.long, comment = "tp:" + str.tostring(longTp) + " sl:" + str.tostring(longSl))\n\n\n    if close > shortSl\n        strategy.close("SHORT")\n    if open < b_low and close < b_low\n        strategy.close("SHORT")\n    // if low < b_low and entry_price > low\n    //     strategy.close("SHORT")'

class SM18F2A1AB05B2EB06(PinePortBase, IStrategy):
    source_id = "SM_18f2a1ab05b2eb06"
    source_file = '移动平均线双击金叉持续上涨策略Dual-Moving-Average-Crossover-Persistent-Uptrend-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'angleCriteria': 7, 'i_lookback': 2, 'i_atrPeriod': 10, 'i_angleLevel': 6, 'TP': 1, 'SL': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'broker_state', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
