"""batch_011 port of 趋势量能突破策略整合EMA与成交量异常监测系统-Trend-Volume-Breakthrough-Strategy-Integrating-EMA-with-Volume-Anomaly-Detection-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-16 00:00:00\nend: 2025-04-15 00:00:00\nperiod: 4d\nbasePeriod: 4d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("AI Volume Strategy", overlay=true)\n\n// === Parameters ===\nvolumeEmaLength = input.int(20, title="Volume EMA Length")\nvolumeMultiplier = input.float(2.0, title="Multiplier (for spike detection)")\nexitBars = input.int(5, title="Exit After How Many Bars?", minval=1)  // Default exit after 5 bars\nshowVolumeEMA = input.bool(false, title="Show Volume EMA", tooltip="Check to show the Volume EMA on the chart")  // Default is false\n\n// === Calculations ===\nvolumeEMA = ta.ema(volume, volumeEmaLength)\nvolumeSpike = volume > volumeEMA * volumeMultiplier\n\n// Trend conditions – simple MA to filter direction\npriceMA = ta.ema(close, 50)\ntrendUp = close > priceMA\ntrendDown = close < priceMA\n\n// Candle conditions (candle color)\nisBullishCandle = close > open  // Bullish candle\nisBearishCandle = close < open  // Bearish candle\n\n// === Signals ===\nbuySignal = volumeSpike and trendUp and isBullishCandle\nsellSignal = volumeSpike and trendDown and isBearishCandle\n\n// Tracking bars since entry\nvar int barsSinceEntry = 0\n\n// Entry logic\nif buySignal\n    strategy.entry("BUY", strategy.long)\n    barsSinceEntry := 0  // Reset bars since entry after buying\n\nif sellSignal\n    strategy.entry("SELL", strategy.short)\n    barsSinceEntry := 0  // Reset bars since entry after selling\n\n// Count bars since entry\nbarsSinceEntry := barsSinceEntry + 1\n\n// Exit condition after the specified number of bars\nexitCondition = barsSinceEntry >= exitBars\n\n// Close positions after the specified number of bars\nif exitCondition\n    strategy.close("BUY", comment="Exit after " + str.tostring(exitBars) + " bars")\n    strategy.close("SELL", comment="Exit after " + str.tostring(exitBars) + " bars")\n\n// === Visualization ===\nplotshape(buySignal, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(sellSignal, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Conditionally plot the Volume EMA line based on user input\nplot(showVolumeEMA ? volumeEMA : na, title="Volume EMA", color=color.orange)\n\n// === Alerts ===\nalertcondition(buySignal, title="Buy Alert", message="AI Volume Signal: BUY")\nalertcondition(sellSignal, title="Sell Alert", message="AI Volume Signal: SELL")\n'

class SMFAE4DD0C3D846E9E(PinePortBase, IStrategy):
    source_id = "SM_fae4dd0c3d846e9e"
    source_file = '趋势量能突破策略整合EMA与成交量异常监测系统-Trend-Volume-Breakthrough-Strategy-Integrating-EMA-with-Volume-Anomaly-Detection-System.md'
    timeframe = '4d'
    can_short = True
    source_defaults = {'volumeEmaLength': 20, 'volumeMultiplier': 2.0, 'exitBars': 5, 'showVolumeEMA': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
