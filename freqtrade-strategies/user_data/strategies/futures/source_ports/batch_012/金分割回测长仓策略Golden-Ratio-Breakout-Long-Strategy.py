"""batch_012 port of 金分割回测长仓策略Golden-Ratio-Breakout-Long-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-21 00:00:00\nend: 2023-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © omkarkondhekar\n\n//@version=4\nstrategy("GRBLong", overlay=true)\n\nhighInput = input(title = "High Days", type = input.integer, defval = 21, minval = 11)\nlowInput = input(title = "Low Days", type = input.integer, defval = 21, minval = 5)\n\n// Configure backtest start date with inputs\nstartDate = input(title="Start Date", type=input.integer,\n     defval=1, minval=1, maxval=31)\nstartMonth = input(title="Start Month", type=input.integer,\n     defval=1, minval=1, maxval=12)\nstartYear = input(title="Start Year", type=input.integer,\n     defval=2019, minval=1800, maxval=2100)\n\n// See if this bar\'s time happened on/after start date\nafterStartDate = (time >= timestamp(syminfo.timezone,\n     startYear, startMonth, startDate, 0, 0))\n\nhigh21 = highest(high, highInput)\nlow21 = lowest(low, lowInput)\n\ndiff = high21 - low21\n\nlongEntrySignal = low > low21 + (diff * 0.382) and close[1] > open[1] \n\nstrategy.entry("Long", strategy.long, limit = low, when = longEntrySignal and afterStartDate)\nstrategy.exit("Long Exit", "Long", stop = low21 + (diff * 0.236))\n\nplot(low21 + (diff * 0.382), color= color.green)\nplot(low21 + (diff * 0.236), color = color.red)\n\n'

class SMGoldenRatioBreakoutLongStrategya99d0f(PinePortBase, IStrategy):
    source_id = "SM_a99d0f1fcdd6769e"
    source_file = '金分割回测长仓策略Golden-Ratio-Breakout-Long-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'highInput': 21, 'lowInput': 21}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
