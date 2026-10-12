"""batch_012 port of 量化交易VSA体积分析与MACD动量指标结合公平价值缺口策略-Quantitative-Trading-Strategy-Combining-VSA-Volume-Analysis-MACD-Momentum-Indicator-and-Fair-Value-Gap-Detection.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-07-22 00:00:00\nend: 2025-03-01 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("VSA+MACD+FVG Strategy", overlay=true)\n\n// === Inputs ===\n// MACD Inputs\nfastLength = input.int(12, "MACD Fast Length", minval=1, group="MACD Settings")\nslowLength = input.int(26, "MACD Slow Length", minval=1, group="MACD Settings")\nsignalLength = input.int(9, "MACD Signal Length", minval=1, group="MACD Settings")\n\n// VSA Inputs\nvolumeLookback = input.int(20, "Volume SMA Period", minval=1, group="VSA Settings")\npriceLookback = input.int(5, "Price Lookback Period", minval=1, group="VSA Settings")\n\n// FVG Inputs\nfvgLookback = input.int(3, "FVG Lookback", minval=1, group="FVG Settings")\nfvgColor = input.color(color.blue, "FVG Color", group="FVG Settings")\nfvgTransparency = input.int(90, "FVG Transparency", minval=0, maxval=100, group="FVG Settings")\n\n// Signal Colors\nbuyColor = input.color(color.green, "Buy Signal Color", group="Display Settings")\nsellColor = input.color(color.red, "Sell Signal Color", group="Display Settings")\n\n// === MACD Calculation ===\n[macdLine, signalLine, hist] = ta.macd(close, fastLength, slowLength, signalLength)\nmacdBullish = macdLine > signalLine and macdLine > 0\nmacdBearish = macdLine < signalLine and macdLine < 0\n\n// === VSA Implementation ===\nvsaBullish = close > open and volume > ta.sma(volume, volumeLookback) and close > ta.highest(high, priceLookback)[2]\nvsaBearish = close < open and volume > ta.sma(volume, volumeLookback) and close < ta.lowest(low, priceLookback)[2]\n\n// === FVG (Fair Value Gap) Detection ===\nfvgUpCondition = low > high[fvgLookback] and close[1] > open[1]\nfvgDownCondition = high < low[fvgLookback] and close[1] < open[1]\n\nvar float fvgTop = 0.0\nvar float fvgBottom = 0.0\nvar bool inFVG = false\n\n// Detect and Store FVG\nif fvgUpCondition\n    fvgTop := low\n    fvgBottom := high[fvgLookback]\n    inFVG := true\nelse if fvgDownCondition\n    fvgTop := low[fvgLookback]\n    fvgBottom := high\n    inFVG := true\n\n// Check if price is in FVG\npriceInFVG = (high >= fvgBottom and low <= fvgTop)\n\n// === Position Tracking ===\nisLongOpen = strategy.position_size > 0\nisShortOpen = strategy.position_size < 0\n\n// === Trading Conditions ===\nbuySignal = vsaBullish and macdBullish and priceInFVG and not isLongOpen\nsellSignal = vsaBearish and macdBearish and priceInFVG and not isShortOpen\n\n// === Execute Trades ===\nif buySignal\n    strategy.entry("Buy", strategy.long)\n\nif sellSignal\n    strategy.entry("Sell", strategy.short)\n\n// === Visual Markers ===\nif buySignal\n    label.new(bar_index, low, "BUY", \n              color=buyColor, \n              textcolor=color.white, \n              style=label.style_label_up)\n\nif sellSignal\n    label.new(bar_index, high, "SELL", \n              color=sellColor, \n              textcolor=color.white, \n              style=label.style_label_down)\n\n// === Plot MACD for reference ===\nplot(macdLine, "MACD", color=color.blue, title="MACD Line")\nplot(signalLine, "Signal", color=color.orange, title="Signal Line")\nplot(hist, "Histogram", style=plot.style_histogram, color=color.gray, title="Histogram")\n'

class SMVSAMACDQuantitativeTradingStrategyCombiningVSAVolumeAna618a49(PinePortBase, IStrategy):
    source_id = "SM_618a4982f71c58d8"
    source_file = '量化交易VSA体积分析与MACD动量指标结合公平价值缺口策略-Quantitative-Trading-Strategy-Combining-VSA-Volume-Analysis-MACD-Momentum-Indicator-and-Fair-Value-Gap-Detection.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9, 'volumeLookback': 20, 'priceLookback': 5, 'fvgLookback': 3, 'fvgColor': 'color.blue', 'fvgTransparency': 90, 'buyColor': 'color.green', 'sellColor': 'color.red'}
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
