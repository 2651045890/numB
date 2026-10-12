"""batch_011 port of 趋势结构突破与订单块公平价值缺口策略-Trend-Structure-Break-with-Order-Block-and-Fair-Value-Gap-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-30 00:00:00\nend: 2024-07-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Trend and Structure Break Strategy", overlay=true)\n\n// Inputs for the moving averages to determine trend\nfastLength = input.int(9, title="Fast MA Length")\nslowLength = input.int(21, title="Slow MA Length")\n\n// Inputs for the order block and fair value gap\norderBlockThreshold = input.float(0.1, title="Order Block Threshold (%)")\nfvgThreshold = input.float(0.5, title="Fair Value Gap Threshold (%)")\n\n// Calculate moving averages\nfastMA = ta.sma(close, fastLength)\nslowMA = ta.sma(close, slowLength)\n\n// Determine trend\nisBullishTrend = fastMA > slowMA\nisBearishTrend = fastMA < slowMA\n\n// Break of structure\nvar float highestHigh = na\nvar float lowestLow = na\n\nif isBullishTrend\n    highestHigh := ta.highest(high, 10)\n    if close > highestHigh\n        label.new(bar_index, high, "BOS Up", style=label.style_label_down, color=color.green)\nif isBearishTrend\n    lowestLow := ta.lowest(low, 10)\n    if close < lowestLow\n        label.new(bar_index, low, "BOS Down", style=label.style_label_up, color=color.red)\n\n// Identify order block\nvar float orderBlockHigh = na\nvar float orderBlockLow = na\n\nif isBullishTrend and close > highestHigh\n    orderBlockHigh := highestHigh\n    orderBlockLow := close * (1 - orderBlockThreshold / 100)\n    box.new(left=bar_index - 1, right=bar_index, top=orderBlockHigh, bottom=orderBlockLow, bgcolor=color.new(color.green, 80))\n\nif isBearishTrend and close < lowestLow\n    orderBlockLow := lowestLow\n    orderBlockHigh := close * (1 + orderBlockThreshold / 100)\n    box.new(left=bar_index - 1, right=bar_index, top=orderBlockHigh, bottom=orderBlockLow, bgcolor=color.new(color.red, 80))\n\n// Identify fair value gap\nvar line fvgLine1 = na\nvar line fvgLine2 = na\nvar line fvgLine3 = na\n\nif isBullishTrend and ta.crossover(close, highestHigh)\n    fvgLine1 := line.new(x1=bar_index, y1=high, x2=bar_index + 1, y2=high, color=color.blue)\n    fvgLine2 := line.new(x1=bar_index, y1=high * (1 - fvgThreshold / 100), x2=bar_index + 1, y2=high * (1 - fvgThreshold / 100), color=color.blue)\n    fvgLine3 := line.new(x1=bar_index, y1=high * (1 - fvgThreshold / 100 * 2), x2=bar_index + 1, y2=high * (1 - fvgThreshold / 100 * 2), color=color.blue)\n\nif isBearishTrend and ta.crossunder(close, lowestLow)\n    fvgLine1 := line.new(x1=bar_index, y1=low, x2=bar_index + 1, y2=low, color=color.blue)\n    fvgLine2 := line.new(x1=bar_index, y1=low * (1 + fvgThreshold / 100), x2=bar_index + 1, y2=low * (1 + fvgThreshold / 100), color=color.blue)\n    fvgLine3 := line.new(x1=bar_index, y1=low * (1 + fvgThreshold / 100 * 2), x2=bar_index + 1, y2=low * (1 + fvgThreshold / 100 * 2), color=color.blue)\n\n// Entry and exit signals\nif (ta.crossover(fastMA, slowMA))\n    strategy.entry("Long", strategy.long)\n\nif (ta.crossunder(fastMA, slowMA))\n    strategy.entry("Short", strategy.short)\n\n// Plot moving averages\nplot(fastMA, color=color.blue, title="Fast MA")\nplot(slowMA, color=color.red, title="Slow MA")'

class SM08A1EE08316E5C53(PinePortBase, IStrategy):
    source_id = "SM_08a1ee08316e5c53"
    source_file = '趋势结构突破与订单块公平价值缺口策略-Trend-Structure-Break-with-Order-Block-and-Fair-Value-Gap-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowLength': 21, 'orderBlockThreshold': 0.1, 'fvgThreshold': 0.5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
