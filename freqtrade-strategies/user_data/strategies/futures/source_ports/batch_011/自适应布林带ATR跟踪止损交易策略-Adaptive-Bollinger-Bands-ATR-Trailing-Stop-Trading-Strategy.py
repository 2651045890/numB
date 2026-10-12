"""batch_011 port of 自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-19 00:00:00\nend: 2025-02-18 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("ATR Trailing Stop Loss with Bollinger Bands", overlay=true)\n\n// Input parameters for Bollinger Bands\nbb_length = input.int(20, title="Bollinger Bands Length")\nbb_stddev = input.float(2.0, title="Bollinger Bands Std Dev")\n\n// Input parameters for ATR Trailing Stop Loss\natr_length = input.int(14, title="ATR Length")\natr_multiplier = input.float(3.0, title="ATR Multiplier")\n\n// Calculate Bollinger Bands\nbasis = ta.sma(close, bb_length)\nupper_band = ta.sma(close, bb_length) + ta.stdev(close, bb_length) * bb_stddev\nlower_band = ta.sma(close, bb_length) - ta.stdev(close, bb_length) * bb_stddev\n\n// Calculate ATR\natr = ta.atr(atr_length)\n\n// Trailing Stop Loss Calculation\nvar float long_stop = na  // Explicitly define as float type\nvar float short_stop = na // Explicitly define as float type\n\nif (strategy.position_size > 0)\n    long_stop := close - atr * atr_multiplier\n    long_stop := math.max(long_stop, nz(long_stop[1], long_stop))\nelse\n    long_stop := na\n\nif (strategy.position_size < 0)\n    short_stop := close + atr * atr_multiplier\n    short_stop := math.min(short_stop, nz(short_stop[1], short_stop))\nelse\n    short_stop := na\n\n// Entry and Exit Conditions\nlong_condition = ta.crossover(close, lower_band)  // Enter long when price crosses above lower band\nshort_condition = ta.crossunder(close, upper_band)  // Enter short when price crosses below upper band\n\nexit_long_condition = ta.crossunder(close, long_stop)  // Exit long when price crosses below trailing stop\nexit_short_condition = ta.crossover(close, short_stop)  // Exit short when price crosses above trailing stop\n\n// Execute Trades\nif (long_condition)\n    strategy.entry("Long", strategy.long)\n\nif (short_condition)\n    strategy.entry("Short", strategy.short)\n\nif (exit_long_condition)\n    strategy.close("Long")\n\nif (exit_short_condition)\n    strategy.close("Short")\n\n// Plot Bollinger Bands\nplot(basis, color=color.blue, title="Basis")\nplot(upper_band, color=color.red, title="Upper Band")\nplot(lower_band, color=color.green, title="Lower Band")\n\n// Plot Trailing Stop Loss\nplot(strategy.position_size > 0 ? long_stop : na, color=color.orange, title="Long Trailing Stop")\nplot(strategy.position_size < 0 ? short_stop : na, color=color.purple, title="Short Trailing Stop")\n\n// Labels for Entry and Exit\nif (long_condition)\n    label.new(bar_index, low, text="Entry Long", style=label.style_circle, color=color.green, textcolor=color.white, size=size.small)\n\nif (short_condition)\n    label.new(bar_index, high, text="Entry Short", style=label.style_circle, color=color.red, textcolor=color.white, size=size.small)\n\nif (exit_long_condition)\n    label.new(bar_index, low, text="Exit Long", style=label.style_circle, color=color.blue, textcolor=color.white, size=size.small)\n\nif (exit_short_condition)\n    label.new(bar_index, high, text="Exit Short", style=label.style_circle, color=color.orange, textcolor=color.white, size=size.small)'

class SM123D24334EAEEFF5(PinePortBase, IStrategy):
    source_id = "SM_123d24334eaeeff5"
    source_file = '自适应布林带ATR跟踪止损交易策略-Adaptive-Bollinger-Bands-ATR-Trailing-Stop-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'bb_length': 20, 'bb_stddev': 2.0, 'atr_length': 14, 'atr_multiplier': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
