"""batch_011 port of 移动平均线金叉死叉策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("My Strategy", overlay=true)\n\nlongCondition = crossover(sma(close, 5), sma(close, 21))\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = crossunder(sma(close, 14), sma(close, 28))\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)'

class SMA09F50A409F6885F(PinePortBase, IStrategy):
    source_id = "SM_a09f50a409f6885f"
    source_file = '移动平均线金叉死叉策略Moving-Average-Crossover-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
