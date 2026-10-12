"""batch_012 port of 高量能突破复利仓位策略High-Volume-Low-Breakout-Compounded-Position-Sizing-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-11 00:00:00\nend: 2024-02-17 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("High Volume Low Breakout (Compounded Position Size)", overlay=true, initial_capital=1000)\n\n// Define input for volume threshold\nvolThreshold = input.int(250, "Volume Threshold")\n\n// Define input for risk per trade as a percentage of total equity\nriskPercentage = input.float(10, "Risk Percentage")\n\n// Calculate volume\nvol = volume\n\n// Check for high volume and low lower than the previous bar\nhighVolume = vol > volThreshold\nlowLowerThanPrevBar = low < low[1]\n\n// Calculate position profit percentage\nposProfitPct = 100 * (close - strategy.position_avg_price) / strategy.position_avg_price\n\n// Calculate the position size based on risk percentage and total account equity\nequity = strategy.equity\nriskAmount = (equity * riskPercentage / 100) / (close - strategy.position_avg_price)\n\n// Calculate leverage (250x in this case)\nleverage = 250\n\n// Calculate the position size in contracts/lots to trade\npositionSize = riskAmount * leverage\n\n// Check if the current bar\'s close is negative when it has high volume\nnegativeCloseWithHighVolume = highVolume and close < close[1]\n\n// Enter long position as soon as volume exceeds the threshold, low is lower than the previous bar, and the current bar\'s close is negative\nif highVolume and lowLowerThanPrevBar and negativeCloseWithHighVolume and strategy.position_size == 0\n    strategy.entry("Long", strategy.long, qty=positionSize, comment="Long Entry")\n\n// Exit long position intrabar if profit goes below -0.14% or above 1%\nif strategy.position_size > 0\n    if posProfitPct < -0.14 or posProfitPct > 4.55\n        strategy.close("Long")\n\n'

class SMHighVolumeLowBreakoutCompoundedPositionSizingStrategy28fe93(PinePortBase, IStrategy):
    source_id = "SM_28fe933a3832ec05"
    source_file = '高量能突破复利仓位策略High-Volume-Low-Breakout-Compounded-Position-Sizing-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'volThreshold': 250, 'riskPercentage': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
