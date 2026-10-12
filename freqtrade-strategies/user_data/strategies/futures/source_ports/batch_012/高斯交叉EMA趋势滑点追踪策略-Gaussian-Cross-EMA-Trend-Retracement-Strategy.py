"""batch_012 port of 高斯交叉EMA趋势滑点追踪策略-Gaussian-Cross-EMA-Trend-Retracement-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-09-24 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Custom Strategy with EMA and Candle Conditions", overlay=true)\n\n// Define parameters\nema_length = 44\n\n// Calculate EMA\nema_44 = ta.ema(close, ema_length)\n\n// Calculate the slope of the EMA\nema_slope = ta.ema(close, ema_length) - ta.ema(close[9], ema_length)\n\n// Define a threshold for considering the EMA flat\nflat_threshold = 0.5\n\n// Check if the EMA is flat or inclined\nema_is_inclined = math.abs(ema_slope) > flat_threshold\n\n// Define the previous candle details\nprev_candle_high = high[1]\nprev_candle_low = low[1]\nprev_candle_close = close[1]\nprev_candle_open = open[1]\n\n// Candle before the previous candle (for high comparison)\ncandle_before_prev_high = high[2]\n\n// Current candle details\ncurrent_candle_high = high\ncurrent_candle_low = low\ncurrent_candle_close = close\ncurrent_candle_open = open\n\n// Previous to previous candle details\nprev_prev_candle_low = low[2]\n\n// Previous candle body and wick length\nprev_candle_body = math.abs(prev_candle_close - prev_candle_open)\nprev_candle_wick_length = math.max(prev_candle_high - prev_candle_close, prev_candle_close - prev_candle_low)\n\n// Calculate retrace level for the current candle\nretrace_level = prev_candle_close - (prev_candle_close - prev_candle_low) * 0.5\n\n// Check if the previous candle\'s wick is smaller than its body\nprev_candle_condition = prev_candle_wick_length < prev_candle_body\n\n// Check if the previous candle is a green (bullish) candle and if the previous candle\'s close is above EMA\nprev_candle_green = prev_candle_close > prev_candle_open\nprev_candle_red = prev_candle_close < prev_candle_open\nprev_candle_above_ema = prev_candle_close > ema_44\n\n// Entry condition: The current candle has retraced to 50% of the previous candle\'s range, previous candle was green and above EMA, and the high of the current candle is above the retrace level, and EMA is inclined\nentry_condition = prev_candle_close > candle_before_prev_high and\n                   prev_candle_green and\n                   prev_candle_above_ema and\n                   current_candle_low <= retrace_level and\n                   current_candle_high >= retrace_level and ema_is_inclined\n\n// Exit condition\nexit_condition = (strategy.position_size > 0 and prev_candle_red) or (strategy.position_size > 0 and current_candle_low < prev_candle_low)\n\n// Ensure only one trade is open at a time\nsingle_trade_condition = strategy.position_size == 0\n\n// Plot EMA for visualization\nplot(ema_44, color=color.blue, title="44 EMA")\n\n// Plot conditions for debugging\nplotshape(series=entry_condition and single_trade_condition, location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(series=exit_condition, location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n\n// Print entry condition value on chart\nvar label entry_label = na\nif (entry_condition and single_trade_condition)\n    entry_label := label.new(bar_index, low, text="Entry Condition: TRUE", color=color.green, textcolor=color.white, size=size.small, yloc=yloc.belowbar)\nelse\n    entry_label := label.new(bar_index, high, text="Entry Condition: FALSE", color=color.red, textcolor=color.white, size=size.small, yloc=yloc.abovebar)\n\n// Debugging: Plot retrace level and other key values\nplot(retrace_level, color=color.orange, title="Retrace Level")\nplot(prev_candle_high, color=color.purple, title="Previous Candle High")\nplot(candle_before_prev_high, color=color.yellow, title="Candle Before Previous High")\n\n// Trigger buy order if entry condition and single trade condition are met\nif (entry_condition and single_trade_condition)\n    strategy.entry("Buy", strategy.long)\n\n// Trigger sell order if exit condition is met\nif (exit_condition)\n    strategy.close("Buy")\n\n'

class SMEMAGaussianCrossEMATrendRetracementStrategyfb503e(PinePortBase, IStrategy):
    source_id = "SM_fb503eae97bfb743"
    source_file = '高斯交叉EMA趋势滑点追踪策略-Gaussian-Cross-EMA-Trend-Retracement-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
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
