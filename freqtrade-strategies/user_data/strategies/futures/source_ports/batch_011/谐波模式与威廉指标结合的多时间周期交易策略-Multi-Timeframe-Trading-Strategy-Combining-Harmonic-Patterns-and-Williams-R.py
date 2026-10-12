"""batch_011 port of 谐波模式与威廉指标结合的多时间周期交易策略-Multi-Timeframe-Trading-Strategy-Combining-Harmonic-Patterns-and-Williams-R.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-09 00:00:00\nend: 2025-01-16 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Harmonic Pattern with WPR Backtest", overlay=true)\n\n// === Inputs ===\npatternLength = input.int(5, title="Pattern Length")\nwprLength = input.int(14, title="WPR Length")\nwprOverbought = input.float(-20, title="WPR Overbought Level")\nwprOversold = input.float(-80, title="WPR Oversold Level")\nriskRewardMultiplier = input.float(0.618, title="Take-Profit Risk/Reward Multiplier")\nstopLossBuffer = input.float(0.005, title="Stop-Loss Buffer (%)")\n\n// === Manual Calculation of William Percent Range (WPR) ===\nhighestHigh = ta.highest(high, wprLength)\nlowestLow = ta.lowest(low, wprLength)\nwpr = ((highestHigh - close) / (highestHigh - lowestLow)) * -100\n\n// === Harmonic Pattern Detection (Simplified Approximation) ===\n// Calculate price pivots\npivotHigh = ta.pivothigh(high, patternLength, patternLength)\npivotLow = ta.pivotlow(low, patternLength, patternLength)\n\n// Detect Bullish and Bearish Harmonic Patterns\nbullishPattern = pivotLow and close > ta.lowest(close, patternLength)  // Simplified detection for bullish patterns\nbearishPattern = pivotHigh and close < ta.highest(close, patternLength)  // Simplified detection for bearish patterns\n\n// === Entry Conditions ===\nlongCondition = bullishPattern and wpr < wprOversold\nshortCondition = bearishPattern and wpr > wprOverbought\n\n// === Stop-Loss and Take-Profit Levels ===\nlongEntryPrice = close\nlongSL = ta.valuewhen(longCondition, low, 0) * (1 - stopLossBuffer)  // Stop-loss for long trades\nlongTP = longEntryPrice * (1 + riskRewardMultiplier)  // Take-profit for long trades\n\nshortEntryPrice = close\nshortSL = ta.valuewhen(shortCondition, high, 0) * (1 + stopLossBuffer)  // Stop-loss for short trades\nshortTP = shortEntryPrice * (1 - riskRewardMultiplier)  // Take-profit for short trades\n\n// === Backtesting Logic ===\n// Long Trade\nif longCondition\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long Exit", "Long", stop=longSL, limit=longTP)\n\n// Short Trade\nif shortCondition\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short Exit", "Short", stop=shortSL, limit=shortTP)\n\n// === Visualization ===\nbgcolor(longCondition ? color.new(color.green, 90) : na, title="Long Entry Signal")\nbgcolor(shortCondition ? color.new(color.red, 90) : na, title="Short Entry Signal")\n'

class SM90E6536A151F15D4(PinePortBase, IStrategy):
    source_id = "SM_90e6536a151f15d4"
    source_file = '谐波模式与威廉指标结合的多时间周期交易策略-Multi-Timeframe-Trading-Strategy-Combining-Harmonic-Patterns-and-Williams-R.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'patternLength': 5, 'wprLength': 14, 'wprOverbought': -20, 'wprOversold': -80, 'riskRewardMultiplier': 0.618, 'stopLossBuffer': 0.005}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
