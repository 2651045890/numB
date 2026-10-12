"""batch_012 port of 高级量化交易多均线交叉体系配合成交量过滤策略-Advanced-Quantitative-Trading-Multi-Moving-Average-Crossover-System-with-Volume-Filter-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2024-12-17 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized Moving Average Crossover Strategy with Volume Filter", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Inputs for Moving Averages\nfastLength = input.int(9, title="Fast MA Length")\nslowLength = input.int(21, title="Slow MA Length")\ntrendFilterLength = input.int(50, title="Trend Filter Length")\n\n// Risk Management Inputs\nstopLossPercent = input.float(1, title="Stop Loss (%)", step=0.1)\ntakeProfitPercent = input.float(400, title="Take Profit (%)", step=0.1)\n\n// Volume Filter Input\nvolumeMultiplier = input.float(1.5, title="Volume Multiplier", step=0.1)  // Multiplier for average volume\n\n// Moving Averages\nfastMA = ta.ema(close, fastLength)\nslowMA = ta.ema(close, slowLength)\ntrendMA = ta.sma(close, trendFilterLength)  // Long-term trend filter\n\n// Volume Calculation\navgVolume = ta.sma(volume, 20)  // 20-period average volume\nvolumeCondition = volume > avgVolume * volumeMultiplier  // Volume must exceed threshold\n\n// Plotting Moving Averages\nplot(fastMA, color=color.blue, title="Fast MA")\nplot(slowMA, color=color.red, title="Slow MA")\nplot(trendMA, color=color.green, title="Trend Filter MA")\n\n// Entry Conditions (Filtered by Trend and Volume)\nlongCondition = ta.crossover(fastMA, slowMA) and close > trendMA and volumeCondition\nshortCondition = ta.crossunder(fastMA, slowMA) and close < trendMA and volumeCondition\n\n// Execute Trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Exit Conditions: Stop Loss and Take Profit\nif (strategy.position_size > 0)\n    strategy.exit("Exit Long", "Long", stop=strategy.position_avg_price * (1 - stopLossPercent / 100), limit=strategy.position_avg_price * (1 + takeProfitPercent / 100))\n\nif (strategy.position_size < 0)\n    strategy.exit("Exit Short", "Short", stop=strategy.position_avg_price * (1 + stopLossPercent / 100), limit=strategy.position_avg_price * (1 - takeProfitPercent / 100))\n\n// Additional Alerts\nalertcondition(longCondition, title="Long Signal", message="Go Long!")\nalertcondition(shortCondition, title="Short Signal", message="Go Short!")\n\n// Debugging Labels\nif (longCondition)\n    label.new(bar_index, close, "Long", style=label.style_label_up, color=color.green, textcolor=color.white)\n\nif (shortCondition)\n    label.new(bar_index, close, "Short", style=label.style_label_down, color=color.red, textcolor=color.white)\n'

class SMAdvancedQuantitativeTradingMultiMovingAverageCrossoverS69eee0(PinePortBase, IStrategy):
    source_id = "SM_69eee054bdb3ea4d"
    source_file = '高级量化交易多均线交叉体系配合成交量过滤策略-Advanced-Quantitative-Trading-Multi-Moving-Average-Crossover-System-with-Volume-Filter-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowLength': 21, 'trendFilterLength': 50, 'stopLossPercent': 1, 'takeProfitPercent': 400}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
