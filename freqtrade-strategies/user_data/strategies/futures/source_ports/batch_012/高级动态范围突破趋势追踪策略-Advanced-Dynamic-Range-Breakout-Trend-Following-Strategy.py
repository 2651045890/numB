"""batch_012 port of 高级动态范围突破趋势追踪策略-Advanced-Dynamic-Range-Breakout-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-31 00:00:00\nend: 2025-03-29 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Enhanced Keltner Channel Strategy", overlay = true)\n\n// Inputs for Keltner Channel\nlength = input.int(20, "EMA Length")\nmult = input.float(2.0, "Multiplier")\n\n// Trend Filter - 200 EMA\ntrendEMA = input.int(200, "Trend EMA Length")\nema200 = ta.ema(close, trendEMA)\n\n// Keltner Channel Calculation\nema = ta.ema(close, length)\natr = ta.atr(length)\nupper_band = ema + mult * atr\nlower_band = ema - mult * atr\n\n// Additional Confirmation - RSI\nrsiLength = input.int(14, "RSI Length")\nrsi = ta.rsi(close, rsiLength)\n\n// Entry Conditions\nlongCondition = ta.crossover(close, upper_band) and close > ema200 and rsi > 50\nshortCondition = ta.crossunder(close, lower_band) and close < ema200 and rsi < 50\n\n// Exit Conditions\nexitLongCondition = ta.crossunder(close, ema)\nexitShortCondition = ta.crossover(close, ema)\n\n// ATR-Based Stop Loss and Take Profit\natrValue = ta.atr(14)\nstopLossLong = close - 1.5 * atrValue\ntakeProfitLong = close + 2 * atrValue\nstopLossShort = close + 1.5 * atrValue\ntakeProfitShort = close - 2 * atrValue\n\n// Strategy Execution\nif longCondition\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Long", stop=stopLossLong, limit=takeProfitLong)\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Short", stop=stopLossShort, limit=takeProfitShort)\n\nif exitLongCondition\n    strategy.close("Long")\n\nif exitShortCondition\n    strategy.close("Short")\n\n// Plotting\nplot(upper_band, color=color.red, linewidth=2, title="Upper Band")\nplot(ema, color=color.blue, linewidth=2, title="EMA")\nplot(lower_band, color=color.green, linewidth=2, title="Lower Band")\nplot(ema200, color=color.purple, linewidth=2, title="Trend Filter EMA 200")\n\n'

class SMAdvancedDynamicRangeBreakoutTrendFollowingStrategy38439e(PinePortBase, IStrategy):
    source_id = "SM_38439e2906221767"
    source_file = '高级动态范围突破趋势追踪策略-Advanced-Dynamic-Range-Breakout-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0, 'trendEMA': 200, 'rsiLength': 14}
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
