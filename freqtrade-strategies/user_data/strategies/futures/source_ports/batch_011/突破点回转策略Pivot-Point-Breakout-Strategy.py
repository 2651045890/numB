"""batch_011 port of 突破点回转策略Pivot-Point-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-27 00:00:00\nend: 2023-09-26 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EduardoMattje\n\n//@version=5\nstrategy("Pivot Point Breakout", "PPB", true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, process_orders_on_close=true)\n\n// Constants\n\nvar L_PIVOT_HIGH = "Pivot high"\nvar L_PIVOT_LOW = "Pivot low"\n\nvar LEFT = "Left"\nvar RIGHT = "Right"\n\nvar BOTH = "Both"\nvar LONG = "Long"\nvar SHORT = "Short"\n\nvar DATES = "Date selection"\nvar DATES_TOOLTIP = "Change it to limit the trades for the given time interval.\\n\\nLeave it to disable this behaviour."\n\n// Inputs\n\nvar orderDirection = input.string(LONG, "Order direction", options=[BOTH, LONG, SHORT])\n\nvar leftHigh = input.int(3, LEFT, minval=0, inline=L_PIVOT_HIGH, group=L_PIVOT_HIGH)\nvar rightHigh = input.int(3, RIGHT, minval=0, inline=L_PIVOT_HIGH, group=L_PIVOT_HIGH)\n\nvar leftLow = input.int(3, LEFT, minval=0, inline=L_PIVOT_LOW, group=L_PIVOT_LOW)\nvar rightLow = input.int(3, RIGHT, minval=0, inline=L_PIVOT_LOW, group=L_PIVOT_LOW)\n\nvar startDate = input(0, "Starting date", group=DATES)\nvar endDate = input(0, "Final date", group=DATES)\n\n//\n\nvar float lastHigh = na\nvar float lastLow = na\n\nlowPivot = ta.pivotlow(leftLow, rightLow)\nhighPivot = ta.pivothigh(leftHigh, rightHigh)\n\nf_updateLevels(pivot_) => \n    var float pastLevel = na\n    \n    if not na(pivot_)\n        pastLevel := pivot_\n    \n    pastLevel\n    \nlastLow := f_updateLevels(lowPivot)\nlastHigh := f_updateLevels(highPivot)\n\n// Validates the time interval\n\nvalidTrade =  true\n\n// Orders\n\nif high > lastHigh\n    strategy.entry("Long", strategy.long, when=orderDirection != SHORT and validTrade)\n    strategy.close("Short", when=orderDirection == SHORT)\nif low < lastLow\n    strategy.entry("Short", strategy.short, when=orderDirection != LONG and validTrade)\n    strategy.close("Long", when=orderDirection == LONG)\n    \n// Plots\n\nplot(lastLow, "Last pivot low", color.red, offset=1)\nplot(lastHigh, "Last pivot high", color.teal, offset=1)\n\nplotshape(lowPivot, "Pivot low", location=location.belowbar, color=color.red, offset=-rightLow)\nplotshape(highPivot, "Pivot high", color=color.teal, offset=-rightHigh)\n'

class SM64ADA79C1833F30D(PinePortBase, IStrategy):
    source_id = "SM_64ada79c1833f30d"
    source_file = '突破点回转策略Pivot-Point-Breakout-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'leftHigh': 3, 'rightHigh': 3, 'leftLow': 3, 'rightLow': 3, 'startDate': 0, 'endDate': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
