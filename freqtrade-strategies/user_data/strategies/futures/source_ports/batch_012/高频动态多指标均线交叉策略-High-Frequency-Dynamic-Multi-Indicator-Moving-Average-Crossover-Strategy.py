"""batch_012 port of 高频动态多指标均线交叉策略-High-Frequency-Dynamic-Multi-Indicator-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized Nifty MidCap Select Options 5-min Intraday Strategy", overlay=true)\n\n// Parameters\nemaShortPeriod = input.int(9, title="Short EMA")\nemaLongPeriod = input.int(21, title="Long EMA")\nrsiPeriod = input.int(14, title="RSI Period")\nrsiOverbought = input.int(65, title="RSI Overbought Level") // More conservative than 70\nrsiOversold = input.int(35, title="RSI Oversold Level") // More conservative than 30\natrLength = input.int(14, title="ATR Length")\natrMultiplier = input.float(1.5, title="ATR Multiplier")\nvolumeMultiplier = input.float(1.2, title="Volume Multiplier") // For confirming high-volume trades\n\n// EMA Calculation\nemaShort = ta.ema(close, emaShortPeriod)\nemaLong = ta.ema(close, emaLongPeriod)\n\n// RSI Calculation\nrsiValue = ta.rsi(close, rsiPeriod)\n\n// ATR Calculation\natrValue = ta.atr(atrLength)\n\n// VWAP Calculation\nvwapValue = ta.vwap(close)\n\n// Volume Check\nvolumeCondition = volume > ta.sma(volume, 20) * volumeMultiplier\n\n// Define long and short conditions\n\n// Long Condition: \n// Price above both EMAs, RSI not overbought, price above VWAP, and high volume\nlongCondition = (close > emaShort) and (close > emaLong) and (rsiValue > 40 and rsiValue < rsiOverbought) and (close > vwapValue) and volumeCondition\n\n// Short Condition: \n// Price below both EMAs, RSI not oversold, price below VWAP, and high volume\nshortCondition = (close < emaShort) and (close < emaLong) and (rsiValue < 60 and rsiValue > rsiOversold) and (close < vwapValue) and volumeCondition\n\n// Entry logic\nif (longCondition)\n    strategy.entry("Buy Call", strategy.long)\nif (shortCondition)\n    strategy.entry("Buy Put", strategy.short)\n\n// Dynamic Take Profit and Stop Loss based on ATR\ntakeProfitLevel = strategy.position_avg_price * (1 + atrValue * atrMultiplier / 100)\nstopLossLevel = strategy.position_avg_price * (1 - atrValue * atrMultiplier / 100)\n\n// Exit strategy based on ATR levels\nstrategy.exit("Take Profit/Stop Loss", from_entry="Buy Call", limit=takeProfitLevel, stop=stopLossLevel)\nstrategy.exit("Take Profit/Stop Loss", from_entry="Buy Put", limit=takeProfitLevel, stop=stopLossLevel)\n\n// Plotting indicators\nplot(emaShort, title="9 EMA", color=color.blue)\nplot(emaLong, title="21 EMA", color=color.red)\nhline(rsiOverbought, "RSI Overbought", color=color.red)\nhline(rsiOversold, "RSI Oversold", color=color.green)\nplot(vwapValue, title="VWAP", color=color.purple)\n'

class SMHighFrequencyDynamicMultiIndicatorMovingAverageCrossovedb3b2d(PinePortBase, IStrategy):
    source_id = "SM_db3b2d12812c679c"
    source_file = '高频动态多指标均线交叉策略-High-Frequency-Dynamic-Multi-Indicator-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaShortPeriod': 9, 'emaLongPeriod': 21, 'rsiPeriod': 14, 'atrLength': 14, 'atrMultiplier': 1.5}
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
