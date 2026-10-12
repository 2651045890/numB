"""batch_011 port of 自适应价格交叉均线交易策略-Adaptive-Price-Crossing-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-03-23 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SHIESTD", overlay=true)\n\n// Function to calculate Hull Moving Average (HMA)\nhma(src, length) =>\n    wma1 = ta.wma(src, length)\n    wma2 = ta.wma(src, length / 2)\n    hma = ta.wma(2 * wma2 - wma1, math.round(math.sqrt(length)))\n    hma\n\n// Parameters\nhma_length = 104\n\n// Calculate Hull Moving Average\nhma_value = hma(close, hma_length)\n\n// Plot HMA\nplot(hma_value, title="104-period Hull Moving Average", color=color.blue, linewidth=2)\n\n// Define SL and TP values in dollars\nlong_sl_amount = 1.25\nlong_tp_amount = 37.5\nshort_sl_amount = 1.25\nshort_tp_amount = 37.5\n\n// Number of contracts\ncontracts = 2\n\n// Function to calculate SL and TP prices based on entry price and dollar amounts\nlong_sl_price(entry_price) =>\n    entry_price - long_sl_amount\n\nlong_tp_price(entry_price) =>\n    entry_price + long_tp_amount\n\nshort_sl_price(entry_price) =>\n    entry_price + short_sl_amount\n\nshort_tp_price(entry_price) =>\n    entry_price - short_tp_amount\n\n// Trading conditions\nprice_intersects_hma = ta.crossover(close, hma_value) or ta.crossunder(close, hma_value)\n\n// Long and Short Conditions based on price intersecting HMA\nlong_condition = ta.crossover(close, hma_value)\nshort_condition = ta.crossunder(close, hma_value)\n\n// Track open positions\nvar bool long_open = false\nvar bool short_open = false\n\n// Handle Long Positions\nif (long_condition and not long_open)\n    entry_price = close\n    strategy.entry("Long", strategy.long, qty=contracts)\n    strategy.exit("Exit Long", from_entry="Long", stop=long_sl_price(entry_price), limit=long_tp_price(entry_price))\n    long_open := true\n\n// Handle Short Positions\nif (short_condition and not short_open)\n    entry_price = close\n    strategy.entry("Short", strategy.short, qty=contracts)\n    strategy.exit("Exit Short", from_entry="Short", stop=short_sl_price(entry_price), limit=short_tp_price(entry_price))\n    short_open := true\n\n// Reset flags when the position is closed\nif (strategy.opentrades == 0)\n    long_open := false\n    short_open := false\n'

class SM8249B569C2D0F3BC(PinePortBase, IStrategy):
    source_id = "SM_8249b569c2d0f3bc"
    source_file = '自适应价格交叉均线交易策略-Adaptive-Price-Crossing-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
