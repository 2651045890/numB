"""batch_012 port of 高级自动交易策略多指标动量和支撑阻力趋势分析系统-Advanced-Automated-Trading-System-Multi-indicator-Momentum-and-Support-Resistance-Trend-Analysis.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-25 00:00:00\nend: 2025-02-25 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Auto Trading Strategy", overlay=true)\n\n// Inputs for Customization\nmaPeriod = input.int(20, "Moving Average Period", minval=1)\nsupportLevel = input.float(21662.5, "Support Level")\nresistanceLevel = input.float(22450, "Resistance Level")\nvolumeLookback = input.int(10, "Volume Lookback Period", minval=1)\nrangeLookback = input.int(10, "Range Lookback Period", minval=1)\nproximity = input.float(100, "Proximity to Support (points)", minval=0)\nstopLossPoints = input.float(100, "Stop Loss (points)", minval=0)\ntakeProfitPoints = input.float(200, "Take Profit (points)", minval=0)\n\n// Calculate Indicators\n// 20-period Simple Moving Average\nma = ta.sma(close, maPeriod)\n\n// Volume Spike Detection (50% above average)\navgVolume = ta.sma(volume, volumeLookback)\nvolumeSpike = volume > avgVolume * 1.5\n\n// Large Candle Range Detection (50% larger than average)\ncandleRange = high - low\navgRange = ta.sma(candleRange, rangeLookback)\nlargeRange = candleRange > avgRange * 1.5\n\n// Candlestick Definitions\nbearishCandle = close < open\nbullishCandle = close > open\n\n// Trading Conditions\n// Short Entry: Price below MA, large bearish candle, volume spike\nshortCondition = close < ma and largeRange and volumeSpike and bearishCandle\n\n// Long Entry: Price near support, bullish candle, volume spike\nnearSupport = close <= supportLevel + proximity\nlongCondition = nearSupport and bullishCandle and volumeSpike\n\n// Execute Trades\nif longCondition\n    strategy.entry("Long", strategy.long)\nif shortCondition\n    strategy.entry("Short", strategy.short)\n\n// Exit Trades with Stop-Loss and Take-Profit\nstrategy.exit("Long Exit", "Long", stop=strategy.position_avg_price - stopLossPoints, limit=strategy.position_avg_price + takeProfitPoints)\nstrategy.exit("Short Exit", "Short", stop=strategy.position_avg_price + stopLossPoints, limit=strategy.position_avg_price - takeProfitPoints)\n\n// Visualizations\nhline(supportLevel, "Support", color=color.green)\nhline(resistanceLevel, "Resistance", color=color.red)\nplot(ma, "Moving Average", color=color.blue)\n\n// Debug Entry Signals\nplotshape(longCondition, title="Long Entry", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(shortCondition, title="Short Entry", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n'

class SMAdvancedAutomatedTradingSystemMultiindicatorMomentumandbe9e37(PinePortBase, IStrategy):
    source_id = "SM_be9e37032f59b898"
    source_file = '高级自动交易策略多指标动量和支撑阻力趋势分析系统-Advanced-Automated-Trading-System-Multi-indicator-Momentum-and-Support-Resistance-Trend-Analysis.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maPeriod': 20, 'supportLevel': 21662.5, 'resistanceLevel': 22450, 'volumeLookback': 10, 'rangeLookback': 10, 'proximity': 100, 'stopLossPoints': 100, 'takeProfitPoints': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
