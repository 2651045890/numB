"""batch_011 port of 突破型公平价差策略Breakthrough-Fair-Value-Gap-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Greg_007\n\n//@version=5\nstrategy("Fair Value Gap Strategy", "FVG Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding = 1)\n\nvar longOnly = input.bool(false, "Take only long trades?")\nvar pyramid = input.bool(false, "Since this can generate a lot of trades, make sure to fill in the commission (if applicable) for a realistic ROI.", group = "REMINDERS")\nvar pyramid2 = input.bool(false, "Modify pyramiding orders to increase the amount of trades.", group = "REMINDERS")\nvar bearFVG = false\nvar bullFVG = false\nvar plotBull = false\nvar plotBear = false\nvar bearTrend = false\nvar bullTrend = false\n\n//BEARISH FVG\nif high < low[2] and close[1] < low[2]\n    bullFVG := false\n    bearFVG := true\n    plotBear := true\n    if not longOnly\n        strategy.entry("Short", strategy.short)\n    else\n        strategy.close_all()\nelse\n    //BULLISH FVG \n    if low > high[2] and close[1] > high[2]\n        bullFVG := true\n        bearFVG := false\n        plotBull := true\n        strategy.entry("Long", strategy.long)\n        \n// plotshape(plotBull, style=shape.labeldown, location=location.abovebar, color=color.green, text="FVG",textcolor=color.white, size=size.tiny, title="Bull FVG", display=display.all - display.status_line)\n// plotshape(plotBear, style=shape.labelup, location=location.belowbar, color=color.red, text="FVG",textcolor=color.white, size=size.tiny, title="Bear FVG", display=display.all - display.status_line)\n\n// //reset the status\n// plotBull := false\n// plotBear := false\n\n'

class SM9CED15E09152BA86(PinePortBase, IStrategy):
    source_id = "SM_9ced15e09152ba86"
    source_file = '突破型公平价差策略Breakthrough-Fair-Value-Gap-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'longOnly': False, 'pyramid': False, 'pyramid2': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
