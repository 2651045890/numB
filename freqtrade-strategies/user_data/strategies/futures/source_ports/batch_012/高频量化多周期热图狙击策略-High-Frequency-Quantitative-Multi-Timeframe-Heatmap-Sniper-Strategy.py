"""batch_012 port of 高频量化多周期热图狙击策略-High-Frequency-Quantitative-Multi-Timeframe-Heatmap-Sniper-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=6\nstrategy("Ultimate Heatmap Sniper Bot", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=1)\n\n// Input Parameters\nsensitivity = input(50, title="Heatmap Sensitivity")\nweekMA = input(50, title="1-Week Moving Average Length")\nmonthMA = input(200, title="1-Month Moving Average Length")\nlookback = input(50, title="Heatmap Lookback")\ntradeFrequency = input(6, title="Max Trades Per Day")\n\n// Calculate Heatmap Highs & Lows\nhighs = ta.highest(high, lookback)\nlows = ta.lowest(low, lookback)\nheatmapLow = ta.sma(lows, sensitivity)\nheatmapHigh = ta.sma(highs, sensitivity)\n\n// Trend Confirmation using Higher Timeframes\nweekTrend = ta.sma(close, weekMA)\nmonthTrend = ta.sma(close, monthMA)\ntrendDirection = weekTrend > monthTrend ? 1 : -1\n\n// Reversal Signals\nbullishReversal = ta.crossover(close, weekTrend)\nbearishReversal = ta.crossunder(close, weekTrend)\n\n// Entry Conditions\nlongEntry = ta.crossover(close, heatmapLow) and trendDirection == 1\nshortEntry = ta.crossunder(close, heatmapHigh) and trendDirection == -1\n\n// Execute Trades\nif (longEntry)\n    strategy.entry("Sniper Long", strategy.long)\nif (shortEntry)\n    strategy.entry("Sniper Short", strategy.short)\n\n// Visualization\nplot(heatmapLow, color=color.green, linewidth=2, title="Heatmap Low")\nplot(heatmapHigh, color=color.red, linewidth=2, title="Heatmap High")\nplot(weekTrend, color=color.blue, linewidth=1, title="1-Week Trend")\nplot(monthTrend, color=color.orange, linewidth=1, title="1-Month Trend")\n\n// Mark Trades on Chart\nplotshape(series=longEntry, location=location.belowbar, color=color.green, style=shape.labelup, title="BUY Signal", text="BUY")\nplotshape(series=shortEntry, location=location.abovebar, color=color.red, style=shape.labeldown, title="SELL Signal", text="SELL")\n\n// Warning Bubble Before Execution\npreLongWarning = ta.crossover(close, heatmapLow * 1.02) and trendDirection == 1\npreShortWarning = ta.crossunder(close, heatmapHigh * 0.98) and trendDirection == -1\nplotshape(series=preLongWarning, location=location.belowbar, color=color.new(color.blue, 90), style=shape.labelup, title="BUY WARNING", text="BUY WARNING")\nplotshape(series=preShortWarning, location=location.abovebar, color=color.orange, style=shape.labeldown, title="SELL WARNING", text="SELL WARNING")\n\n// Reversal Indicators with Diamonds\nplotshape(series=bullishReversal, location=location.belowbar, color=color.green, style=shape.diamond, title="Bullish Reversal", text="Bull Reversal")\nplotshape(series=bearishReversal, location=location.abovebar, color=color.red, style=shape.diamond, title="Bearish Reversal", text="Bear Reversal")\n\n// Sparkle Trail Projection\nprojectedMove = (heatmapHigh + heatmapLow) / 2\nplotshape(series=projectedMove, location=location.belowbar, color=color.purple, style=shape.cross, title="Projected Move Cross")\n\n'

class SMHighFrequencyQuantitativeMultiTimeframeHeatmapSniperStr71c638(PinePortBase, IStrategy):
    source_id = "SM_71c638c18c25e9b2"
    source_file = '高频量化多周期热图狙击策略-High-Frequency-Quantitative-Multi-Timeframe-Heatmap-Sniper-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'sensitivity': 50, 'weekMA': 50, 'monthMA': 200, 'lookback': 50, 'tradeFrequency': 6}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
