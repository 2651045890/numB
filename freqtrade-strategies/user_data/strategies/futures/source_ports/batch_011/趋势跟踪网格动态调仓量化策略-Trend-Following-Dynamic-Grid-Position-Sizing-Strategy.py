"""batch_011 port of 趋势跟踪网格动态调仓量化策略-Trend-Following-Dynamic-Grid-Position-Sizing-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-04 00:00:00\nend: 2024-12-11 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("TTM Grid Strategy", overlay=true)\n\n// Input parameters\nint ttmPeriod = input.int(6, minval=1, title="TTM Period")\nint gridLevels = input.int(5, minval=2, title="Grid Levels")\nfloat gridSpacing = input.float(0.01, minval=0.0001, title="Grid Spacing (%)")\n\n// Calculate TTM State\nttmState() =>\n    lowMA = ta.ema(low, ttmPeriod)\n    highMA = ta.ema(high, ttmPeriod)\n    lowThird = (highMA - lowMA) / 3 + lowMA\n    highThird = 2 * (highMA - lowMA) / 3 + lowMA\n\n    if close > highThird\n        1\n    else if close < lowThird\n        0\n    else\n        -1\n\n// State tracking variables\nvar float gridBasePrice = 0.0\nvar int gridDirection = -1\n\n// Determine grid state\nupdateGridState(float currentClose, int currentState) =>\n    float newBasePrice = gridBasePrice\n    int newDirection = gridDirection\n\n    if currentState != -1 and currentState != gridDirection\n        newBasePrice := currentClose\n        newDirection := currentState\n    \n    [newBasePrice, newDirection]\n\n// Calculate grid levels\ncalcGridLevels(float basePrice, int direction, int levels) =>\n    float[] buyLevels = array.new_float(levels)\n    float[] sellLevels = array.new_float(levels)\n\n    for i = 1 to levels\n        multiplier = i * gridSpacing\n        if direction == 1  // Buy grid\n            array.set(buyLevels, i-1, basePrice * (1 - multiplier))\n            array.set(sellLevels, i-1, basePrice * (1 + multiplier))\n        else  // Sell grid\n            array.set(buyLevels, i-1, basePrice * (1 + multiplier))\n            array.set(sellLevels, i-1, basePrice * (1 - multiplier))\n    \n    [buyLevels, sellLevels]\n\n// Execute grid trades\nexecuteGridTrades(float basePrice, int direction, int levels) =>\n    [buyLevels, sellLevels] = calcGridLevels(basePrice, direction, levels)\n\n    for i = 0 to levels - 1\n        float buyLevel = array.get(buyLevels, i)\n        float sellLevel = array.get(sellLevels, i)\n\n        if direction == 1  // Buy grid\n            if low <= buyLevel\n                strategy.entry("GridBuy" + str.tostring(i), strategy.long, comment="Buy Level " + str.tostring(i))\n            if high >= sellLevel\n                strategy.entry("GridSell" + str.tostring(i), strategy.short, comment="Sell Level " + str.tostring(i))\n        else  // Sell grid\n            if high >= buyLevel\n                strategy.entry("GridBuy" + str.tostring(i), strategy.long, comment="Buy Level " + str.tostring(i))\n            if low <= sellLevel\n                strategy.entry("GridSell" + str.tostring(i), strategy.short, comment="Sell Level " + str.tostring(i))\n\n// Main strategy logic\ncurrentState = ttmState()\n[newGridBasePrice, newGridDirection] = updateGridState(close, currentState)\n\n// Update global variables\nif newGridBasePrice != gridBasePrice\n    gridBasePrice := newGridBasePrice\nif newGridDirection != gridDirection\n    gridDirection := newGridDirection\n\n// Execute grid trades\nexecuteGridTrades(newGridBasePrice, newGridDirection, gridLevels)\n\n// Visualization\nplotColor = newGridDirection == 1 ? color.green : color.red\nplot(newGridBasePrice, color=plotColor, style=plot.style_cross)'

class SMFA278D073058A051(PinePortBase, IStrategy):
    source_id = "SM_fa278d073058a051"
    source_file = '趋势跟踪网格动态调仓量化策略-Trend-Following-Dynamic-Grid-Position-Sizing-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'ttmPeriod': 6, 'gridLevels': 5, 'gridSpacing': 0.01}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'array', 'loop', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
