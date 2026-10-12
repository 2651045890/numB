"""batch_012 port of 高级多指标趋势确认交易策略-Advanced-Multi-Indicator-Trend-Confirmation-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-16 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Enhanced Volume + Trend Strategy", overlay=true)\n\n// Inputs\nemaLength = input.int(50, title="EMA Length")\natrLength = input.int(14, title="ATR Length")\natrMultiplierSL = input.float(2.0, title="ATR Multiplier for Stop Loss")\natrMultiplierTP = input.float(3.0, title="ATR Multiplier for Take Profit")\nvolLength = input.int(20, title="Volume Moving Average Length")\nvolMultiplier = input.float(1.5, title="Volume Multiplier (Relative to Previous Volume)")\n\n// Trend Detection using EMA\nema = ta.ema(close, emaLength)\n\n// ATR Calculation for Stop Loss/Take Profit\natr = ta.atr(atrLength)\n\n// Volume Moving Average\nvolMA = ta.sma(volume, volLength)\n\n// Additional Volume Condition (Current Volume > Previous Volume + Multiplier)\nvolCondition = volume > volMA * volMultiplier and volume > volume[1]\n\n// Entry Conditions based on Trend (EMA) and Volume (Volume Moving Average)\nlongCondition = close > ema and volCondition\nshortCondition = close < ema and volCondition\n\n// Stop Loss and Take Profit Levels\nlongStopLoss = close - (atr * atrMultiplierSL)\nlongTakeProfit = close + (atr * atrMultiplierTP)\nshortStopLoss = close + (atr * atrMultiplierSL)\nshortTakeProfit = close - (atr * atrMultiplierTP)\n\n// Strategy Execution\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Long", stop=longStopLoss, limit=longTakeProfit)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Short", stop=shortStopLoss, limit=shortTakeProfit)\n\n// Plotting EMA\nplot(ema, color=color.yellow, title="EMA")\n\n// Plot Volume Moving Average\nplot(volMA, color=color.blue, title="Volume Moving Average")\n\n// Signal Visualizations\nplotshape(series=longCondition, color=color.green, style=shape.labelup, location=location.belowbar, title="Buy Signal")\nplotshape(series=shortCondition, color=color.red, style=shape.labeldown, location=location.abovebar, title="Sell Signal")\n\n'

class SMAdvancedMultiIndicatorTrendConfirmationTradingStrategya3fab3(PinePortBase, IStrategy):
    source_id = "SM_a3fab3bc78af27e0"
    source_file = '高级多指标趋势确认交易策略-Advanced-Multi-Indicator-Trend-Confirmation-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaLength': 50, 'atrLength': 14, 'atrMultiplierSL': 2.0, 'atrMultiplierTP': 3.0, 'volLength': 20, 'volMultiplier': 1.5}
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
