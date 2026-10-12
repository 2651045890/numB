"""batch_011 port of 自适应布林网格交易策略-Adaptive-Bollinger-Bands-Grid-Trading-Strategy-with-Dynamic-Level-Adjustment.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-19 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Grid Bot based on Bollinger Bands with Adjustable Levels", overlay=true)\n\n// Settings\nsource = close\nlength = input.int(20, minval=1, title="Bollinger Bands Length")\nmult = input.float(2.0, minval=0.001, maxval=50, title="Bollinger Bands Multiplier")\ngridDistancePercent = input.float(1.0, title="Distance Between Levels (%)") / 100 // Distance between grid levels in percentage\ngridSize = input.int(4, title="Number of Grid Levels") // Number of grid levels\n\n// Bollinger Bands Calculation\nbasis = ta.sma(source, length)\ndev = mult * ta.stdev(source, length)\nupper = basis + dev\nlower = basis - dev\n\n// Middle line between the upper and lower Bollinger Bands\nmiddle = (upper + lower) / 2\n\n// Levels for long and short positions\nvar float[] longLevels = array.new_float(gridSize)\nvar float[] shortLevels = array.new_float(gridSize)\n\n// Filling levels for long and short positions\nfor i = 0 to gridSize - 1\n    array.set(longLevels, i, lower * (1 + gridDistancePercent * (i + 1))) // For longs, increase the lower band\n    array.set(shortLevels, i, upper * (1 - gridDistancePercent * (i + 1))) // For shorts, decrease the upper band\n\n// Logic for entering a long position (buy) at the first level crossover\nlongCondition = ta.crossover(source, array.get(longLevels, 0)) // Condition for buying — crossover with the first long level\nif longCondition\n    strategy.entry("GridLong", strategy.long, comment="GridLong")\n\n// Logic for entering a short position (sell) at the first level crossunder\nshortCondition = ta.crossunder(source, array.get(shortLevels, 0)) // Condition for selling — crossunder with the first short level\nif shortCondition\n    strategy.entry("GridShort", strategy.short, comment="GridShort")\n\n// Logic for additional buys/sells when reaching subsequent levels\n// For longs:\nfor i = 1 to gridSize - 1\n    if ta.crossover(source, array.get(longLevels, i))\n        strategy.entry("GridLong" + str.tostring(i), strategy.long, comment="GridLong")\n\n// For shorts:\nfor i = 1 to gridSize - 1\n    if ta.crossunder(source, array.get(shortLevels, i))\n        strategy.entry("GridShort" + str.tostring(i), strategy.short, comment="GridShort")\n\n// Visualization of the levels\nplot(upper, color=color.red, linewidth=2, title="Upper Bollinger Band")\nplot(lower, color=color.green, linewidth=2, title="Lower Bollinger Band")\nplot(middle, color=color.blue, linewidth=2, title="Middle Line")\n\n// Display additional grid levels (fixed titles)\nplot(array.get(longLevels, 0), color=color.green, linewidth=1, title="Long Level 1") // For the 1st long level\nplot(array.get(longLevels, 1), color=color.green, linewidth=1, title="Long Level 2") // For the 2nd long level\nplot(array.get(longLevels, 2), color=color.green, linewidth=1, title="Long Level 3") // For the 3rd long level\nplot(array.get(longLevels, 3), color=color.green, linewidth=1, title="Long Level 4") // For the 4th long level\n\nplot(array.get(shortLevels, 0), color=color.red, linewidth=1, title="Short Level 1") // For the 1st short level\nplot(array.get(shortLevels, 1), color=color.red, linewidth=1, title="Short Level 2") // For the 2nd short level\nplot(array.get(shortLevels, 2), color=color.red, linewidth=1, title="Short Level 3") // For the 3rd short level\nplot(array.get(shortLevels, 3), color=color.red, linewidth=1, title="Short Level 4") // For the 4th short level\n'

class SMA0A025355E3F1E4F(PinePortBase, IStrategy):
    source_id = "SM_a0a025355e3f1e4f"
    source_file = '自适应布林网格交易策略-Adaptive-Bollinger-Bands-Grid-Trading-Strategy-with-Dynamic-Level-Adjustment.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0, 'gridDistancePercent': 1.0, 'gridSize': 4}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['array', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
