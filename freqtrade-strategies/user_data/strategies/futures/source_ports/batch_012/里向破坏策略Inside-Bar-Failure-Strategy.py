"""batch_012 port of 里向破坏策略Inside-Bar-Failure-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-07 00:00:00\nend: 2022-10-31 00:00:00\nperiod: 4d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Inside Bar Failure", overlay=true)\n\nforward = input(defval=3, title="Look Forward")\n\nlongCondition = if (high[2] > high[1] and low[2] < low[1] and low < low[1] and high < high[1] and close > low[1])\n    x = true\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = if (high[2] > high[1] and low[2] < low[1] and high > high[1] and low > low[1] and close < high[1])\n    y = true\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    \nif (longCondition[forward])\n    strategy.close("Long")\nif (shortCondition[forward])\n    strategy.close("Short")\n'

class SMInsideBarFailureStrategya651a4(PinePortBase, IStrategy):
    source_id = "SM_a651a4a67a14f818"
    source_file = '里向破坏策略Inside-Bar-Failure-Strategy.md'
    timeframe = '4d'
    can_short = True
    source_defaults = {'forward': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
