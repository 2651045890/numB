"""batch_012 port of 高级动量EMA趋势跟踪结合RSI超买超卖的交易策略-Advanced-Momentum-EMA-Trend-Following-with-RSI-Overbought-Oversold-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-08-01 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © bommytarton\n\n//@version=6\nstrategy("Improved Momentum and Pivot Reversal Strategy", overlay=true)\n\n// Define user inputs\nlengthEMA = input.int(34, title="EMA Length", minval=1)\nlengthRSI = input.int(14, title="RSI Length", minval=1)\nrsiOverbought = input.int(70, title="RSI Overbought Level", minval=50, maxval=100)\nrsiOversold = input.int(30, title="RSI Oversold Level", minval=0, maxval=50)\nlengthATR = input.int(14, title="ATR Length", minval=1)\nmultATR = input.float(1.5, title="ATR Multiplier for Take-Profit", minval=1.0)\nstopLossMultiplier = input.float(1.0, title="Stop Loss Multiplier for ATR", minval=0.5, maxval=3.0) // Adjust the stop-loss to be tighter or wider\n\n// Calculate the indicators\nema34 = ta.ema(close, lengthEMA)\nrsiValue = ta.rsi(close, lengthRSI)\natrValue = ta.atr(lengthATR)\n\n// Define entry conditions\nlongCondition = close > ema34 and close[1] < open[1] and close > open and close[2] > open[2] and close[1] < open[1] and rsiValue > 50\n\n// Define stop-loss and take-profit based on ATR\nstopLoss = close - (atrValue * stopLossMultiplier) // Tighter stop-loss using the ATR multiplier\ntakeProfit = close + (atrValue * multATR) // Take profit with adjustable multiplier\n\n// Volume condition filter (make sure that the volume is higher than average over the past 20 bars)\navgVolume = ta.sma(volume, 20)\nvolumeCondition = volume > avgVolume\n\n// Only trigger long if all conditions are met (trend above 34 EMA, red-green-green candle pattern, volume confirmation)\nif (longCondition and volumeCondition)\n    strategy.entry("Long", strategy.long, stop=stopLoss, limit=takeProfit)\n\n// Exit conditions based on RSI overbought/oversold and trailing stop\nexitCondition = rsiValue > rsiOverbought or close < stopLoss\n\n// Execute the exit strategy when RSI is overbought or price hits the stop-loss level\nif (exitCondition)\n    strategy.close("Long")  // Close the position when exit condition is met\n\n// Plotting for visualization\nplot(ema34, title="34 EMA", color=color.blue)\nplot(stopLoss, title="Stop Loss", color=color.red, linewidth=2)\nplot(takeProfit, title="Take Profit", color=color.green, linewidth=2)\n\n'

class SMEMARSIAdvancedMomentumEMATrendFollowingwithRSIOverbough20bb20(PinePortBase, IStrategy):
    source_id = "SM_20bb20c5ea4589c6"
    source_file = '高级动量EMA趋势跟踪结合RSI超买超卖的交易策略-Advanced-Momentum-EMA-Trend-Following-with-RSI-Overbought-Oversold-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'lengthEMA': 34, 'lengthRSI': 14, 'rsiOverbought': 70, 'rsiOversold': 30, 'lengthATR': 14, 'multATR': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
