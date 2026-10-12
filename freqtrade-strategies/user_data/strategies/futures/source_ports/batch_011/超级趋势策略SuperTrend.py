"""batch_011 port of 超级趋势策略SuperTrend.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-08-17 08:00:00\nend: 2024-08-29 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\nstrategy("supertrend", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 50)\n\n[supertrend, direction] = ta.supertrend(input(5, "factor"), input.int(10, "atrPeriod"))\n\nplot(direction < 0 ? supertrend : na, "Up direction", color = color.green, style=plot.style_linebr)\nplot(direction > 0 ? supertrend : na, "Down direction", color = color.red, style=plot.style_linebr)\n\nif direction < 0\n    if supertrend > supertrend[2]\n        strategy.entry("entry long", strategy.long)\n    else if strategy.position_size < 0\n        strategy.close_all()\nelse if direction > 0\n    if supertrend < supertrend[3]\n        strategy.entry("entry short", strategy.short)\n    else if strategy.position_size > 0\n        strategy.close_all()\n'

class SMA724C4CCB6D658F6(PinePortBase, IStrategy):
    source_id = "SM_a724c4ccb6d658f6"
    source_file = '超级趋势策略SuperTrend.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 50
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
