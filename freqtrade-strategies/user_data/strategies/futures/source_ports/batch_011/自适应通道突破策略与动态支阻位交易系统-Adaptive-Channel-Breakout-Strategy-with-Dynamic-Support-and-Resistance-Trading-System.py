"""batch_011 port of 自适应通道突破策略与动态支阻位交易系统-Adaptive-Channel-Breakout-Strategy-with-Dynamic-Support-and-Resistance-Trading-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-04 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Support and Resistance with Trend Lines and Channels", overlay=true)\n\n// Inputs\nlookback = input.int(20, title="Lookback Period for Support/Resistance", minval=1)\nchannelWidth = input.float(0.01, title="Channel Width (%)", minval=0.001) / 100\nstartDate = input(timestamp("2023-01-01 00:00"), title="Backtesting Start Date")\nendDate = input(timestamp("2023-12-31 23:59"), title="Backtesting End Date")\n\n// Check if the current bar is within the testing range\ninTestingRange = true\n\n// Support and Resistance Levels\nsupportLevel = ta.lowest(low, lookback)  // Swing low (support)\nresistanceLevel = ta.highest(high, lookback)  // Swing high (resistance)\n\n// Trend Lines and Channels\nvar line supportLine = na\nvar line resistanceLine = na\nvar line upperChannelLine = na\nvar line lowerChannelLine = na\n\n// Calculate channel levels\nupperChannel = resistanceLevel * (1 + channelWidth)  // Upper edge of channel\nlowerChannel = supportLevel * (1 - channelWidth)  // Lower edge of channel\n\n// Create or update the support trend line\n// if na(supportLine)\n//     supportLine := line.new(bar_index, supportLevel, bar_index + 1, supportLevel, color=color.green, width=2, extend=extend.right)\n// else\n//     line.set_y1(supportLine, supportLevel)\n//     line.set_y2(supportLine, supportLevel)\n\n// // Create or update the resistance trend line\n// if na(resistanceLine)\n//     resistanceLine := line.new(bar_index, resistanceLevel, bar_index + 1, resistanceLevel, color=color.red, width=2, extend=extend.right)\n// else\n//     line.set_y1(resistanceLine, resistanceLevel)\n//     line.set_y2(resistanceLine, resistanceLevel)\n\n// // Create or update the upper channel line\n// if na(upperChannelLine)\n//     upperChannelLine := line.new(bar_index, upperChannel, bar_index + 1, upperChannel, color=color.blue, width=1, style=line.style_dashed, extend=extend.right)\n// else\n//     line.set_y1(upperChannelLine, upperChannel)\n//     line.set_y2(upperChannelLine, upperChannel)\n\n// // Create or update the lower channel line\n// if na(lowerChannelLine)\n//     lowerChannelLine := line.new(bar_index, lowerChannel, bar_index + 1, lowerChannel, color=color.purple, width=1, style=line.style_dashed, extend=extend.right)\n// else\n//     line.set_y1(lowerChannelLine, lowerChannel)\n//     line.set_y2(lowerChannelLine, lowerChannel)\n\n// Buy Condition: When price is near support level\nbuyCondition = close <= supportLevel * 1.01 and inTestingRange\nif buyCondition\n    strategy.entry("Buy", strategy.long)\n\n// Stop Loss and Take Profit\nstopLossPercentage = input.float(1.5, title="Stop Loss Percentage", minval=0.0) / 100\ntakeProfitPercentage = input.float(3.0, title="Take Profit Percentage", minval=0.0) / 100\n\nvar float longStopLoss = na\nvar float longTakeProfit = na\nif strategy.position_size > 0\n    longStopLoss := strategy.position_avg_price * (1 - stopLossPercentage)\n    longTakeProfit := strategy.position_avg_price * (1 + takeProfitPercentage)\n    strategy.exit("Exit Buy", "Buy", stop=longStopLoss, limit=longTakeProfit)\n\n// Visualize Entry, Stop Loss, and Take Profit Levels\nvar float entryPrice = na\nif buyCondition\n    entryPrice := close\nif not na(entryPrice)\n    label.new(bar_index, entryPrice, text="Entry: " + str.tostring(entryPrice, "#.##"), style=label.style_label_up, color=color.green, textcolor=color.white)\n\nif strategy.position_size > 0\n    line.new(bar_index, longStopLoss, bar_index + 1, longStopLoss, color=color.red, width=1, extend=extend.right)\n    line.new(bar_index, longTakeProfit, bar_index + 1, longTakeProfit, color=color.blue, width=1, extend=extend.right)\n\n// Risk-to-Reward Ratio (Optional)\nif not na(entryPrice) and not na(longStopLoss) and not na(longTakeProfit)\n    riskToReward = (longTakeProfit - entryPrice) / (entryPrice - longStopLoss)\n    label.new(bar_index, entryPrice, text="R:R " + str.tostring(riskToReward, "#.##"), style=label.style_label_up, color=color.yellow, textcolor=color.black, size=size.small)'

class SM873B2055527CEC26(PinePortBase, IStrategy):
    source_id = "SM_873b2055527cec26"
    source_file = '自适应通道突破策略与动态支阻位交易系统-Adaptive-Channel-Breakout-Strategy-with-Dynamic-Support-and-Resistance-Trading-System.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'lookback': 20, 'channelWidth': 0.01, 'stopLossPercentage': 1.5, 'takeProfitPercentage': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
