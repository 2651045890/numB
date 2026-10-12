"""batch_012 port of 高频量化交易中的趋势匹配与退出优化策略-High-Frequency-Quantitative-Trading-Strategy-with-Trend-Matching-and-Exit-Optimization.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-19 00:00:00\nend: 2025-02-16 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Intraday + 1-Hour Trend Match", overlay=true)\n\n// Inputs\nemaLength3Min = input.int(50, title="EMA Length (3-Min)")\nemaLength1Hr = input.int(50, title="EMA Length (1-Hour)")\nvolumeMultiplier = input.float(1.5, title="Volume Spike Multiplier")\n\n// Intraday (3-Minute) EMA and Volume Spike\nema3Min = ta.ema(close, emaLength3Min)\nvolumeSMA = ta.sma(volume, 20)\nisVolumeSpike = volume > (volumeSMA * volumeMultiplier)\n\n// 1-Hour Trend (EMA)\nema1Hr = request.security(syminfo.tickerid, "60", ta.ema(close, emaLength1Hr))\nis1HrUptrend = close > ema1Hr\n\n// Intraday Signal\nbuyCondition3Min = close > ema3Min and isVolumeSpike\n\n// Combined Signal: Match 3-Min Signal with 1-Hour Trend\nfinalBuyCondition = buyCondition3Min and is1HrUptrend\n\n// All-Day High Tracking\nvar float allDayHigh = na\nif (hour == 9 and minute == 0)\n    allDayHigh := high // Reset the all-day high at market open\nelse\n    allDayHigh := math.max(allDayHigh, high) // Update all-day high\n\n// Debugging Plots\nplot(ema3Min, color=color.blue, title="EMA 3-Min")\nplot(ema1Hr, color=color.orange, title="EMA 1-Hour")\nplotshape(isVolumeSpike, style=shape.circle, color=color.blue, title="Volume Spike (3-Min)")\nplotshape(finalBuyCondition, style=shape.triangleup, color=color.green, title="Buy Signal")\nplot(allDayHigh, color=color.red, title="All-Day High", linewidth=2)\n\n// Strategy Execution\nif (finalBuyCondition)\n    strategy.entry("Buy Signal", strategy.long)\n\n// Exit Conditions\nexitCondition = (close == allDayHigh) or (hour == 15 and minute >= 0)\nif (exitCondition)\n    strategy.close("Buy Signal")\n\n'

class SMHighFrequencyQuantitativeTradingStrategywithTrendMatchi517682(PinePortBase, IStrategy):
    source_id = "SM_517682bf1d0d3256"
    source_file = '高频量化交易中的趋势匹配与退出优化策略-High-Frequency-Quantitative-Trading-Strategy-with-Trend-Matching-and-Exit-Optimization.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'emaLength3Min': 50, 'emaLength1Hr': 50, 'volumeMultiplier': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
