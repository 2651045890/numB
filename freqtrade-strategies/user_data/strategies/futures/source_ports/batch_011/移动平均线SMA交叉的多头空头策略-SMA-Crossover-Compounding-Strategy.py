"""batch_011 port of 移动平均线SMA交叉的多头空头策略-SMA-Crossover-Compounding-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Umesh SMA Crossover Strategy", overlay=true)\n\n// Input parameters\nfast_length = input.int(9, title="Fast SMA Length")\nslow_length = input.int(21, title="Slow SMA Length")\n\n// Calculate SMAs\nfast_sma = ta.sma(close, fast_length)\nslow_sma = ta.sma(close, slow_length)\n\n// Plot SMAs\nplot(fast_sma, color=color.blue, title="Fast SMA")\nplot(slow_sma, color=color.red, title="Slow SMA")\n\n// Strategy logic\nlongCondition = ta.crossover(fast_sma, slow_sma)\nshortCondition = ta.crossunder(fast_sma, slow_sma)\n\n// Initialize cumulative profit with netprofit\nvar float cumulative_profit = na\nif (na(cumulative_profit))\n    cumulative_profit := strategy.netprofit\n\n// // Initialize starting balance\n// var float starting_balance = na\n// if (na(starting_balance))\n//     starting_balance := strategy.equity\n\n// Initialize starting balance\nvar float starting_balance = na\nif (na(starting_balance))\n    starting_balance := 100000.0 // Initial balance\n\n// Calculate profit or gains\nif (strategy.opentrades != 0)\n    cumulative_profit := strategy.netprofit + (strategy.equity - starting_balance)\n\n// Calculate position size based on current balance and cumulative profit\n//position_size = 100000 \nposition_size = starting_balance + cumulative_profit\n\n// Entry conditions\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty = position_size / close)\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty = position_size / close)\n\n// // Entry conditions\n// if (longCondition)\n//     strategy.entry("Long", strategy.long, qty = 100000 / close)\n// if (shortCondition)\n//     strategy.entry("Short", strategy.short, qty = 100000 / close)\n\n\n// Plot strategy.equity \nplot(strategy.equity, color=color.green, title="Cumulative Profit")\n\n// Print cumulative profit value on chart\nlabel.new(x = bar_index, y = strategy.equity, text = str.tostring(strategy.equity), style=label.style_label_down, color=color.new(color.green, 0), size=size.small)\n// Plot cumulative profit\nplot(cumulative_profit, color=color.green, title="Cumulative Profit")\n\n// Print cumulative profit value on chart\nlabel.new(x = bar_index, y = cumulative_profit, text = str.tostring(cumulative_profit), style=label.style_label_down, color=color.new(color.green, 0), size=size.small)\n\n// Plot cumulative profit\nplot(position_size, color=color.green, title="Cumulative Profit")\n\n// Print cumulative profit value on chart\nlabel.new(x = bar_index, y = position_size, text = str.tostring(position_size), style=label.style_label_down, color=color.new(color.green, 0), size=size.small)\n'

class SM0086CD91F11FE810(PinePortBase, IStrategy):
    source_id = "SM_0086cd91f11fe810"
    source_file = '移动平均线SMA交叉的多头空头策略-SMA-Crossover-Compounding-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fast_length': 9, 'slow_length': 21}
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
