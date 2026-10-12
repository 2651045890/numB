"""batch_011 port of 突破结构与成交量确认的多重条件智能交易策略-Break-of-Structure-with-Volume-Confirmation-Multi-Condition-Intelligent-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("BOS and Volume Strategy with Confirmation", overlay=true)\n\n// Parameters\nswingLength = input.int(20, title="Swing Length", minval=1)\nvolumeMultiplier = input.float(1.1, title="Volume Multiplier", step=0.1)\nvolumeSMA_length = input.int(10, title="Volume SMA Length", minval=1)\ntakeProfitPercentage = input.float(0.02, title="Take Profit Percentage", step=0.01)\nstopLossPercentage = input.float(0.15, title="Stop Loss Percentage", step=0.01)  // New parameter for stop loss\natrLength = input.int(14, title="ATR Length")\nconfirmationBars = input.int(2, title="Confirmation Bars", minval=1)\n\n// Calculate Swing Highs and Lows\nswingHigh = ta.highest(high, swingLength)[1]\nswingLow = ta.lowest(low, swingLength)[1]\n\n// Calculate Volume Moving Average\nvolumeSMA = ta.sma(volume, volumeSMA_length)\nhighVolume = volume > (volumeSMA * volumeMultiplier)\n\n// Break of Structure Detection with Confirmation\nvar int bullishCount = 0\nvar int bearishCount = 0\n\nif (close > swingHigh and highVolume)\n    bullishCount := bullishCount + 1\n    bearishCount := 0\nelse if (close < swingLow and highVolume)\n    bearishCount := bearishCount + 1\n    bullishCount := 0\nelse\n    bullishCount := 0\n    bearishCount := 0\n\nbullishBOSConfirmed = (bullishCount >= confirmationBars)\nbearishBOSConfirmed = (bearishCount >= confirmationBars)\n\n// Entry and Exit Conditions\nvar float entryPrice = na  // Declare entryPrice as a variable\n\nif (bullishBOSConfirmed and strategy.position_size <= 0)\n    entryPrice := close  // Use \':=\' for assignment\n    strategy.entry("Long", strategy.long)\n\nif (strategy.position_size > 0)\n    // Calculate stop loss price\n    stopLossPrice = entryPrice * (1 - stopLossPercentage)\n    strategy.exit("Take Profit Long", from_entry="Long", limit=entryPrice * (1 + takeProfitPercentage), stop=stopLossPrice)\n\nif (bearishBOSConfirmed and strategy.position_size >= 0)\n    entryPrice := close  // Use \':=\' for assignment\n    strategy.entry("Short", strategy.short)\n\nif (strategy.position_size < 0)\n    // Calculate stop loss price\n    stopLossPrice = entryPrice * (1 + stopLossPercentage)\n    strategy.exit("Take Profit Short", from_entry="Short", limit=entryPrice * (1 - takeProfitPercentage), stop=stopLossPrice)\n\n// Plot Swing Highs and Lows for Visualization\nplot(swingHigh, title="Swing High", color=color.green, linewidth=1)\nplot(swingLow, title="Swing Low", color=color.red, linewidth=1)'

class SM0B821441D672A9DB(PinePortBase, IStrategy):
    source_id = "SM_0b821441d672a9db"
    source_file = '突破结构与成交量确认的多重条件智能交易策略-Break-of-Structure-with-Volume-Confirmation-Multi-Condition-Intelligent-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'swingLength': 20, 'volumeMultiplier': 1.1, 'volumeSMA_length': 10, 'takeProfitPercentage': 0.02, 'stopLossPercentage': 0.15, 'atrLength': 14, 'confirmationBars': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
