"""batch_011 port of 自适应三重超级趋势策略Adaptive-Triple-Supertrend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-25 00:00:00\nend: 2024-01-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Custom Supertrend Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=15, shorttitle="Supertrend Strategy")\n\n// Define the parameters for Supertrend 1\nfactor1 = input.float(3.0, "Factor 1", step = 0.01)\natrPeriod1 = input(12, "ATR Length 1")\n\n// Define the parameters for Supertrend 2\nfactor2 = input.float(1.0, "Factor 2", step = 0.01)\natrPeriod2 = input(10, "ATR Length 2")\n\n// Define the parameters for Supertrend 3\nfactor3 = input.float(2.0, "Factor 3", step = 0.01)\natrPeriod3 = input(11, "ATR Length 3")\n\n[_, direction1] = ta.supertrend(factor1, atrPeriod1)\n[_, direction2] = ta.supertrend(factor2, atrPeriod2)\n[_, direction3] = ta.supertrend(factor3, atrPeriod3)\n\n// Define the start and end dates as Unix timestamps (in seconds)\nstart_date = timestamp("2023-01-01T00:00:00")\nend_date = timestamp("2023-10-01T00:00:00")\n\n// Determine Buy and Sell conditions within the specified date range\nin_date_range = true\nbuy_condition = direction1 > 0 and direction2 > 0 and direction3 > 0 and in_date_range\nsell_condition = direction1 < 0 or direction2 < 0 or direction3 < 0\n\n// Track the position with a variable\nvar isLong = false\n\nif buy_condition and not isLong\n    strategy.entry("Long Entry", strategy.long)\n    isLong := true\n\nif sell_condition and isLong\n    // Define take profit and stop loss percentages\n    take_profit_percentage = 10 // Increased to 10%\n    stop_loss_percentage = 1\n\n    // Calculate take profit and stop loss levels\n    take_profit_level = close * (1 + take_profit_percentage / 100)\n    stop_loss_level = close * (1 - stop_loss_percentage / 100)\n\n    // Exit the long position with take profit and stop loss\n    strategy.exit("Take Profit/Stop Loss", from_entry="Long Entry", limit=take_profit_level, stop=stop_loss_level)\n    isLong := false'

class SM484BAEA6246B5563(PinePortBase, IStrategy):
    source_id = "SM_484baea6246b5563"
    source_file = '自适应三重超级趋势策略Adaptive-Triple-Supertrend-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'factor1': 3.0, 'atrPeriod1': 12, 'factor2': 1.0, 'atrPeriod2': 10, 'factor3': 2.0, 'atrPeriod3': 11}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 15
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
