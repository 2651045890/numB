"""batch_012 port of 量化价格行为突破动态风险收益比交易策略-Dynamic-Risk-Reward-Price-Action-Breakout-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 5d\nbasePeriod: 5d\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Filtered Price Action Breakout", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// === INPUTS ===\nlookback = input.int(20, title="Breakout Lookback Period", minval=5)\nstopLookback = input.int(10, title="Stop Loss Lookback Period", minval=3)\nrrMultiplier = input.float(5.0, title="Risk-to-Reward Multiplier", step=0.1)\nmaxTradesPerDay = input.int(5, title="Max Trades Per Day", minval=1)\n\n// Ensure there are enough bars for calculations\ninRange = bar_index >= lookback\n\n// === CALCULATIONS ===\n// Highest high and lowest low over the \'lookback\' period\nhighestHigh = ta.highest(high, lookback)\nlowestLow = ta.lowest(low, lookback)\n\n// Define breakout conditions (using previous bar\'s level)\nbullBreakout = ta.crossover(close, highestHigh[1])\nbearBreakout = ta.crossunder(close, lowestLow[1])\n\n// Store breakout signals in variables to prevent inconsistencies\nbullBreakoutSignal = bullBreakout\nbearBreakoutSignal = bearBreakout\n\n// Determine stop levels based on recent swing lows/highs\nlongStop = ta.lowest(low, stopLookback)\nshortStop = ta.highest(high, stopLookback)\n\n// Track number of trades per day (fixing boolean condition issue)\nnewDay = ta.change(time("D")) != 0\ntodayTrades = ta.barssince(newDay)\ntradeCount = 0\nif newDay\n    tradeCount := 0\nelse\n    tradeCount := tradeCount + 1\n\n// === STRATEGY LOGIC: ENTRY & EXIT ===\nif bullBreakoutSignal and tradeCount < maxTradesPerDay\n    entryPrice = close\n    stopLevel = longStop\n    risk = entryPrice - stopLevel\n    if risk > 0\n        target = entryPrice + rrMultiplier * risk\n        strategy.entry("Long", strategy.long)\n        strategy.exit("Long Exit", from_entry="Long", stop=stopLevel, limit=target)\n        tradeCount := tradeCount + 1\n\nif bearBreakoutSignal and tradeCount < maxTradesPerDay\n    entryPrice = close\n    stopLevel = shortStop\n    risk = stopLevel - entryPrice\n    if risk > 0\n        target = entryPrice - rrMultiplier * risk\n        strategy.entry("Short", strategy.short)\n        strategy.exit("Short Exit", from_entry="Short", stop=stopLevel, limit=target)\n        tradeCount := tradeCount + 1\n\n// === PLOTTING ===\nplot(highestHigh, color=color.green, title="Highest High (Breakout Level)")\nplot(lowestLow, color=color.red, title="Lowest Low (Breakout Level)")\n\n'

class SMDynamicRiskRewardPriceActionBreakoutTradingStrategy07c16a(PinePortBase, IStrategy):
    source_id = "SM_07c16af71a98026f"
    source_file = '量化价格行为突破动态风险收益比交易策略-Dynamic-Risk-Reward-Price-Action-Breakout-Trading-Strategy.md'
    timeframe = '5d'
    can_short = True
    source_defaults = {'lookback': 20, 'stopLookback': 10, 'rrMultiplier': 5.0, 'maxTradesPerDay': 5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
