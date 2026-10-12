"""batch_012 port of 高频量价趋势跟踪与成交量分析自适应策略-High-Frequency-Price-Volume-Trend-Following-with-Volume-Analysis-Adaptive-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-10 00:00:00\nend: 2025-01-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Jerryorange\n\n//@version=6\n//@version=6\nstrategy("Autonomous 5-Minute Robot", overlay=true, fill_orders_on_standard_ohlc=true)\n\n// --- Inputs ---\nmaLength = input.int(50, title="Trend MA Length")  // Moving average length for trend detection\nvolumeLength = input.int(10, title="Volume Length") // Length for volume analysis\nstopLossPercent = input.float(3, title="Stop Loss (%)")  // 3% stop loss\ntakeProfitPercent = input.float(29, title="Take Profit (%)")  // 29% take profit\n\n// --- Market Trend Detection ---\nma = ta.sma(close, maLength)  // Simple moving average for trend direction\nisBullish = close > ma  // Market is bullish if the close is above the moving average\nisBearish = close < ma  // Market is bearish if the close is below the moving average\n\n// --- Volume Analysis ---\nbuyVolume = (high != low) ? volume * (close - low) / (high - low) : 0\nsellVolume = (high != low) ? volume * (high - close) / (high - low) : 0\ntotalVolume = volume\n\n// --- Define Market Direction over Last 30 Minutes (6 candles in 5-minute chart) ---\nlookback = 6  // 30 minutes / 5 minutes = 6 bars\n\nprevClose = close[lookback]  // Previous close 30 minutes ago\ncurrentClose = close  // Current close\nuptrend = currentClose > prevClose and isBullish  // Uptrend condition\ndowntrend = currentClose < prevClose and isBearish  // Downtrend condition\n\n// --- Strategy Logic ---\nlongCondition = uptrend and buyVolume > sellVolume  // Buy signal when trend is up and buy volume exceeds sell volume\nshortCondition = downtrend and sellVolume > buyVolume  // Sell signal when trend is down and sell volume exceeds buy volume\n\n// --- Entry and Exit Strategy ---\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// --- Exit Strategy based on Stop Loss and Take Profit ---\nstrategy.exit("Exit Long", "Long", stop=close * (1 - stopLossPercent / 100), limit=close * (1 + takeProfitPercent / 100))\nstrategy.exit("Exit Short", "Short", stop=close * (1 + stopLossPercent / 100), limit=close * (1 - takeProfitPercent / 100))\n\n// --- Plotting for Visualization ---\nplot(ma, color=color.blue, title="50-period MA")  // Trend line\nplotshape(longCondition, style=shape.labelup, location=location.belowbar, color=color.green, text="BUY")\nplotshape(shortCondition, style=shape.labeldown, location=location.abovebar, color=color.red, text="SELL")\n\n\n'

class SMHighFrequencyPriceVolumeTrendFollowingwithVolumeAnalysid4b24e(PinePortBase, IStrategy):
    source_id = "SM_d4b24e55d5ea9e40"
    source_file = '高频量价趋势跟踪与成交量分析自适应策略-High-Frequency-Price-Volume-Trend-Following-with-Volume-Analysis-Adaptive-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
