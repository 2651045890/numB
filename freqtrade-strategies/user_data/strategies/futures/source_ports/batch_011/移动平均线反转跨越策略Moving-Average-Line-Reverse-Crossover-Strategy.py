"""batch_011 port of 移动平均线反转跨越策略Moving-Average-Line-Reverse-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-23 00:00:00\nend: 2023-11-28 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Moving Average Reverse Crossover Strategy", overlay=true)\n\n// Calculate the 45-day moving average\nma_length = 45\nma = ta.sma(close, ma_length)\n\n// Track position entry and entry bar\nvar bool in_short_position = na\nvar int entry_bar = na\nvar int exit_bar = na\n\n// Entry condition: Close price crosses below the 45-day moving average to enter the short position\nif (not in_short_position and ta.crossunder(close, ma) and not na(ma[1]) and close < ma and close[1] > ma[1])\n    in_short_position := true\n    entry_bar := bar_index\n\n// Exit condition: Close the short position after holding for 8 trading days\nif (in_short_position and bar_index - entry_bar >= 8)\n    in_short_position := false\n    exit_bar := bar_index\n\n// Re-entry condition: Wait for price to cross below the 45-day moving average again\nif (not in_short_position and ta.crossunder(close, ma) and not na(ma[1]) and close < ma and close[1] < ma[1] and (na(exit_bar) or bar_index - exit_bar >= 8))\n    in_short_position := true\n    entry_bar := bar_index\n\n// Execute short entry and exit\nif (in_short_position)\n    strategy.entry("Short", strategy.short)\n\nif (not in_short_position)\n    strategy.close("Short")'

class SM6B6CC31DCB9597E1(PinePortBase, IStrategy):
    source_id = "SM_6b6cc31dcb9597e1"
    source_file = '移动平均线反转跨越策略Moving-Average-Line-Reverse-Crossover-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
