"""batch_011 port of 超趋势和CCI策略的短线交易Supertrend-and-CCI-Scalping-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-19 00:00:00\nend: 2024-02-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend & CCI Strategy Scalp", overlay=true)\n\n// SuperTrend Settings\natrLength1 = input(14, "ATR Length 1")\nfactor1 = input(3.0, "Factor 1" )\natrLength2 = input(14, "ATR Length 2")\nfactor2 = input(6.0, "Factor 2")\n // Calculate SuperTrend 1\n[superTrend1, direction1] = ta.supertrend(factor1, atrLength1)\n\n// // Calculate SuperTrend 2\n[superTrend2, direction2] = ta.supertrend(factor2, atrLength2)\n\n// superTrend1 := barstate.isfirst ? na : superTrend1\n// upTrend1 =    plot(direction1 < 0 ? superTrend1 : na, "Up Trend",   color = color.green, style = plot.style_linebr)\n// downTrend1 =  plot(direction1 < 0 ? na : superTrend1, "Down Trend", color = color.red,   style = plot.style_linebr)\n// bodyMiddle1 = plot(barstate.isfirst ? na : (open + close) / 2, "Body Middle",display = display.none)\n\n// fill(bodyMiddle1, upTrend1,   color.new(color.green, 90), fillgaps = false)\n// fill(bodyMiddle1, downTrend1, color.new(color.red,   90), fillgaps = false)\n\n// superTrend2 := barstate.isfirst ? na : superTrend2\n// upTrend2 =    plot(direction1 < 0 ? superTrend2 : na, "Up Trend",   color = color.green, style = plot.style_linebr)\n// downTrend2 =  plot(direction1 < 0 ? na : superTrend2, "Down Trend", color = color.red,   style = plot.style_linebr)\n// bodyMiddle2 = plot(barstate.isfirst ? na : (open + close) / 2, "Body Middle",display = display.none)\n\n// fill(bodyMiddle2, upTrend2,   color.new(color.green, 90), fillgaps = false)\n// fill(bodyMiddle2, downTrend2, color.new(color.red,   90), fillgaps = false)\n// CCI Settings\n//cciLength = input.int(14, title="CCI Length")\ncciLevel = input.int(100, title="CCI Level")\n\n// Calculate CCI\nlength = input.int(20, minval=1)\nsrc = input(hlc3, title="Source")\nma = ta.sma(src, length)\ncci = (src - ma) / (0.015 * ta.dev(src, length))\n//plot(cci, "CCI", color=#2962FF)\n//band1 = hline(100, "Upper Band", color=#787B86, linestyle=hline.style_dashed)\n//hline(0, "Middle Band", color=color.new(#787B86, 50))\n//band0 = hline(-100, "Lower Band", color=#787B86, linestyle=hline.style_dashed)\n//fill(band1, band0, color=color.rgb(33, 150, 243, 90), title="Background")\n\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\ntypeMA = input.string(title = "Method", defval = "SMA", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="Smoothing")\nsmoothingLength = input.int(title = "Length", defval = 5, minval = 1, maxval = 100, group="Smoothing")\n\nsmoothingLine = ma(cci, smoothingLength, typeMA)\n//plot(smoothingLine, title="Smoothing Line", color=#f37f20, display=display.none)\n\n\n// Entry conditions\nlongCondition = superTrend1 > close and superTrend2 < close and smoothingLine < -100\nshortCondition = superTrend1 < close and superTrend2 > close and smoothingLine > 100\n\n/// Initialize variables to track trade direction\nvar bool isLong = na\nvar bool isShort = na\n\n// Strategy entry and exit\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    isLong := true\n    isShort := false\n    \nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    isShort := true\n    isLong := false\n\n// Close Long positions\nif (isLong)\n    strategy.close("Long", when = superTrend1 < close or superTrend2 > close or cci > 100)\n\n// Close Short positions\nif (isShort)\n    strategy.close("Short", when = superTrend1 > close or superTrend2 < close or cci < -100)\n\n\n\n// Plotting\nplot(superTrend1, color=color.blue, title="SuperTrend 1")\nplot(superTrend2, color=color.red, title="SuperTrend 2")\n//plot(cci, color=color.orange, title="CCI")\n\n'

class SM2D2956DE122B5DE7(PinePortBase, IStrategy):
    source_id = "SM_2d2956de122b5de7"
    source_file = '超趋势和CCI策略的短线交易Supertrend-and-CCI-Scalping-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrLength1': 14, 'factor1': 3.0, 'atrLength2': 14, 'factor2': 6.0, 'cciLevel': 100, 'length': 20, 'typeMA': 'SMA', 'smoothingLength': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'switch', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
