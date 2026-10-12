"""batch_011 port of 移动平均线交叉穿越策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-04 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title="MA Crossover (40)", overlay=true)\n\n// Input for the SMA length (24)\nsma_length = input(40, title="SMA Length")\nsma = ta.sma(close, sma_length)\n\n// Determine if the current candle crosses above the 24-period SMA\nlongCondition = ta.crossover(close, sma)\n\n// Determine if the current candle crosses and closes below the 24-period SMA\ncloseLongCondition = ta.crossunder(close, sma)\n\n// Plot the 24-period SMA\nplot(sma, color=color.blue, title="24-period SMA")\n\n// Long entry signal\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Close long position when the current candle crosses and closes below the 24-period SMA\nif (closeLongCondition)\n    strategy.close("Long")\n\n\n// Create alerts\nalertcondition(longCondition, title="Candle Crosses Above SMA 40", message="Candle has crossed above SMA 40.")\nalertcondition(longCondition, title="Candle Closes Above SMA 40", message="Candle has closed above SMA 40.")\n\n'

class SM9CCC0EF323F91E3C(PinePortBase, IStrategy):
    source_id = "SM_9ccc0ef323f91e3c"
    source_file = '移动平均线交叉穿越策略Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'sma_length': 40}
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
