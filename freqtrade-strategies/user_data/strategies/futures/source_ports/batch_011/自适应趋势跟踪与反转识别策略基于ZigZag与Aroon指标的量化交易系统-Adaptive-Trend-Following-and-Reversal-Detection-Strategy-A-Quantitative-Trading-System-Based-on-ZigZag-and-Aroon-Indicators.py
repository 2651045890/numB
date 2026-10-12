"""batch_011 port of 自适应趋势跟踪与反转识别策略基于ZigZag与Aroon指标的量化交易系统-Adaptive-Trend-Following-and-Reversal-Detection-Strategy-A-Quantitative-Trading-System-Based-on-ZigZag-and-Aroon-Indicators.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-10 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Zig Zag + Aroon Strategy", overlay=true)\n\n// Zig Zag parameters\nzigzagDepth = input(5, title="Zig Zag Depth")\n\n// Aroon parameters\naroonLength = input(14, title="Aroon Length")\n\n// Zig Zag logic\nvar float lastZigZag = na\nvar float lastZigZagHigh = na\nvar float lastZigZagLow = na\nvar int direction = 0  // 1 for up, -1 for down\n\n// Calculate Zig Zag\nif (not na(high) and high >= ta.highest(high, zigzagDepth) and direction != 1)\n    lastZigZag := high\n    lastZigZagHigh := high\n    direction := 1\nif (not na(low) and low <= ta.lowest(low, zigzagDepth) and direction != -1)\n    lastZigZag := low\n    lastZigZagLow := low\n    direction := -1\n\n// Aroon calculation\nhighestHigh = ta.highest(high, aroonLength)\nlowestLow = ta.lowest(low, aroonLength)\naroonUp = (aroonLength - (bar_index - ta.highestbars(high, aroonLength))) / aroonLength * 100\naroonDown = (aroonLength - (bar_index - ta.lowestbars(low, aroonLength))) / aroonLength * 100\n\n// Long entry condition\nlongCondition = (ta.crossover(aroonUp, aroonDown)) and (lastZigZag == lastZigZagHigh)\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short entry condition\nshortCondition = (ta.crossover(aroonDown, aroonUp)) and (lastZigZag == lastZigZagLow)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Exit conditions\nif (ta.crossover(aroonDown, aroonUp) and strategy.position_size > 0)\n    strategy.close("Long")\n\nif (ta.crossover(aroonUp, aroonDown) and strategy.position_size < 0)\n    strategy.close("Short")\n\n// Plot Zig Zag\nplot(lastZigZag, color=color.blue, title="Zig Zag", linewidth=2, style=plot.style_stepline)\n\n// Plot Aroon\nhline(70, "Aroon Up Overbought", color=color.red)\nhline(30, "Aroon Down Oversold", color=color.green)\nplot(aroonUp, color=color.green, title="Aroon Up")\nplot(aroonDown, color=color.red, title="Aroon Down")'

class SMB6CE265A2AF803A2(PinePortBase, IStrategy):
    source_id = "SM_b6ce265a2af803a2"
    source_file = '自适应趋势跟踪与反转识别策略基于ZigZag与Aroon指标的量化交易系统-Adaptive-Trend-Following-and-Reversal-Detection-Strategy-A-Quantitative-Trading-System-Based-on-ZigZag-and-Aroon-Indicators.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'zigzagDepth': 5, 'aroonLength': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
