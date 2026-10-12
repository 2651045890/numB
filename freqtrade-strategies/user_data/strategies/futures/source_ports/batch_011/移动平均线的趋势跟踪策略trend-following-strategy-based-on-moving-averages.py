"""batch_011 port of 移动平均线的趋势跟踪策略trend-following-strategy-based-on-moving-averages.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-30 00:00:00\nend: 2023-10-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Simple Moving Average Crossover", overlay=true)\n\n// Input parameters\nfast_length = input(10, title="Fast MA Length")\nslow_length = input(50, title="Slow MA Length")\nstop_loss_pct = input(1, title="Stop Loss Percentage", minval=0, maxval=5) / 100\n\n// Calculate moving averages\nfast_ma = sma(close, fast_length)\nslow_ma = sma(close, slow_length)\n\n// Plot moving averages\nplot(fast_ma, color=color.blue, title="Fast MA")\nplot(slow_ma, color=color.red, title="Slow MA")\n\n// Strategy logic\nlong_condition = crossover(fast_ma, slow_ma)\nshort_condition = crossunder(fast_ma, slow_ma)\n\n// Execute trades\nif (long_condition)\n    strategy.entry("Long", strategy.long)\n\nif (short_condition)\n    strategy.entry("Short", strategy.short)\n\n// Set stop loss\nlong_stop_price = close * (1 - stop_loss_pct)\nshort_stop_price = close * (1 + stop_loss_pct)\n\nstrategy.exit("Stop Loss/Profit", from_entry="Long", stop=long_stop_price)\nstrategy.exit("Stop Loss/Profit", from_entry="Short", stop=short_stop_price)\n'

class SM57374D39FBB10B79(PinePortBase, IStrategy):
    source_id = "SM_57374d39fbb10b79"
    source_file = '移动平均线的趋势跟踪策略trend-following-strategy-based-on-moving-averages.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fast_length': 10, 'slow_length': 50, 'stop_loss_pct': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
