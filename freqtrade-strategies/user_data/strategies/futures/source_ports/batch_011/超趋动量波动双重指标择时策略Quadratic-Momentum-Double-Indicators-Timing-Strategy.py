"""batch_011 port of 超趋动量波动双重指标择时策略Quadratic-Momentum-Double-Indicators-Timing-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-27 00:00:00\nend: 2024-02-03 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Elliott\'s Quadratic Momentum - Strategy [presentTrading]",shorttitle = "EQM Strategy [presentTrading]", overlay=true )\n\n// Inputs for selecting trading direction\ntradingDirection = input.string("Both", "Select Trading Direction", options=["Long", "Short", "Both"])\n\n\n// SuperTrend Function\nsupertrend(src, atrLength, multiplier) =>\n    atr = ta.atr(atrLength)\n    up = hl2 - (multiplier * atr)\n    dn = hl2 + (multiplier * atr)\n    trend = 1\n    trend := nz(trend[1], 1)\n    up := src > nz(up[1], 0) and src[1] > nz(up[1], 0) ?   math.max(up, nz(up[1], 0)) : up\n    dn := src < nz(dn[1], 0) and src[1] < nz(dn[1], 0) ? math.min(dn, nz(dn[1], 0)) : dn\n    trend := src > nz(dn[1], 0) ?  1 : src < nz(up[1], 0)? -1 : nz(trend[1], 1)\n    [up, dn, trend]\n\n// Inputs for SuperTrend settings\natrLength1 = input(7, title="ATR Length for SuperTrend 1")\nmultiplier1 = input(4.0, title="Multiplier for SuperTrend 1")\natrLength2 = input(14, title="ATR Length for SuperTrend 2")\nmultiplier2 = input(3.618, title="Multiplier for SuperTrend 2")\natrLength3 = input(21, title="ATR Length for SuperTrend 3")\nmultiplier3 = input(3.5, title="Multiplier for SuperTrend 3")\natrLength4 = input(28, title="ATR Length for SuperTrend 3")\nmultiplier4 = input(3.382, title="Multiplier for SuperTrend 3")\n\n// Calculate SuperTrend\n[up1, dn1, trend1] = supertrend(close, atrLength1, multiplier1)\n[up2, dn2, trend2] = supertrend(close, atrLength2, multiplier2)\n[up3, dn3, trend3] = supertrend(close, atrLength3, multiplier3)\n[up4, dn4, trend4] = supertrend(close, atrLength4, multiplier4)\n\n\n// Entry Conditions based on SuperTrend and Elliott Wave-like patterns\nlongCondition = trend1 == 1 and trend2 == 1 and trend3 == 1 and trend4 == 1\nshortCondition = trend1 == -1 and trend2 == -1 and trend3 == -1 and trend4 == - 1\n\n// Strategy Entry logic based on selected trading direction\nif tradingDirection == "Long" or tradingDirection == "Both"\n    if longCondition\n        strategy.entry("Long", strategy.long)\n        // [Any additional logic for long entry]\n\nif tradingDirection == "Short" or tradingDirection == "Both"\n    if shortCondition\n        strategy.entry("Short", strategy.short)\n        // [Any additional logic for short entry]\n\n\n// Exit conditions - Define your own exit strategy\n// Example: Exit when any SuperTrend flips\nif trend1 != trend1[1] or trend2 != trend2[1] or trend3 != trend3[1] or trend4 != trend4[1] \n    strategy.close_all()\n\n// Function to apply gradient effect\ngradientColor(baseColor, length, currentBar) =>\n    var color res = color.new(baseColor, 100)\n    if currentBar <= length\n        res := color.new(baseColor, int(100 * currentBar / length))\n    res\n\n// Apply gradient effect\ncolor1 = gradientColor(color.blue, atrLength1, bar_index % atrLength1)\ncolor4 = gradientColor(color.blue, atrLength4, bar_index % atrLength3)\n\n\n// Plot SuperTrend with gradient for upward trend\nplot1Up = plot(trend1 == 1 ? up1 : na, color=color1, linewidth=1, title="SuperTrend 1 Up")\nplot4Up = plot(trend4 == 1 ? up4 : na, color=color4, linewidth=1, title="SuperTrend 3 Up")\n\n// Plot SuperTrend with gradient for downward trend\nplot1Down = plot(trend1 == -1 ? dn1 : na, color=color1, linewidth=1, title="SuperTrend 1 Down")\nplot4Down = plot(trend4 == -1 ? dn4 : na, color=color4, linewidth=1, title="SuperTrend 3 Down")\n\n// Filling the area between the first and third SuperTrend lines for upward trend\nfill(plot1Up, plot4Up, color=color.new(color.green, 80), title="SuperTrend Upward Band")\n\n// Filling the area between the first and third SuperTrend lines for downward trend\nfill(plot1Down, plot4Down, color=color.new(color.red, 80), title="SuperTrend Downward Band")\n\n'

class SM1FA8E9B04738A38B(PinePortBase, IStrategy):
    source_id = "SM_1fa8e9b04738a38b"
    source_file = '超趋动量波动双重指标择时策略Quadratic-Momentum-Double-Indicators-Timing-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'tradingDirection': 'Both', 'atrLength1': 7, 'multiplier1': 4.0, 'atrLength2': 14, 'multiplier2': 3.618, 'atrLength3': 21, 'multiplier3': 3.5, 'atrLength4': 28, 'multiplier4': 3.382}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
