"""batch_011 port of 超趋势追踪止盈策略Supertrend-Take-Profit-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy( "Supertrend with TP", overlay=true )\n\n// Supertrend Settings\natrPeriod = input(10, "ATR Length")\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n// TP\'s\ntp1Open = input.bool(true, "TP1")\ntp1 = input.float(2.0, "TP Level (%)", step = 0.1) / 100\ntp1Amount = input.int(25, "Amount (%)", step = 1)\ntp2Open = input.bool(true, "TP2")\ntp2 = input.float(5.0, "TP Level (%)", step = 0.1) / 100\ntp2Amount = input.int(50, "Amount (%)", step = 1)\ntp3Open = input.bool(true, "TP3")\ntp3 = input.float(10.0, "TP Level (%)", step = 0.1) / 100\ntp3Amount = input.int(25, "Amount (%)", step = 1)\n\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\nentryPrice = 0.0\nentryPrice := entryPrice[1]\n\nif ta.change(direction) < 0\n    strategy.entry("Long", strategy.long)\n    entryPrice := close\n\nif ta.change(direction) > 0\n    strategy.entry("Short", strategy.short)\n    entryPrice := close\n\nif (tp1Open)\n    strategy.exit ("TP1", from_entry="Long", limit=entryPrice * (1 + tp1), qty_percent=tp1Amount)\n    strategy.exit ("TP1", from_entry="Short", limit=entryPrice * (1 - tp1), qty_percent=tp1Amount)\n\nif (tp2Open)\n    strategy.exit ("TP2", from_entry="Long", limit=entryPrice * (1 + tp2), qty_percent=tp2Amount)\n    strategy.exit ("TP2", from_entry="Short", limit=entryPrice * (1 - tp2), qty_percent=tp2Amount)\n    \nif (tp3Open)    \n    strategy.exit ("TP3", from_entry="Long", limit=entryPrice * (1 + tp3), qty_percent=tp3Amount)\n    strategy.exit ("TP3", from_entry="Short", limit=entryPrice * (1 - tp3), qty_percent=tp3Amount)'

class SM6C60496C6D20CBFB(PinePortBase, IStrategy):
    source_id = "SM_6c60496c6d20cbfb"
    source_file = '超趋势追踪止盈策略Supertrend-Take-Profit-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrPeriod': 10, 'factor': 3.0, 'tp1Open': True, 'tp1': 2.0, 'tp1Amount': 25, 'tp2Open': True, 'tp2': 5.0, 'tp2Amount': 50, 'tp3Open': True, 'tp3': 10.0, 'tp3Amount': 25}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
