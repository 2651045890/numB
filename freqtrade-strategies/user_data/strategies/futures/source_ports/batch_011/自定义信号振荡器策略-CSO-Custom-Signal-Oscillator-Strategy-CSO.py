"""batch_011 port of 自定义信号振荡器策略-CSO-Custom-Signal-Oscillator-Strategy-CSO.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-21 00:00:00\nend: 2024-06-20 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © NantzOS\n\n//@version=5\nstrategy("Custom Signal Oscillator Strategy", shorttitle="CSO-TEST", overlay=false)\n\n// Input: Select two plots\nplot1 = input(open, title="Fast Signal")\nplot2 = input(close, title="Slow Signal")\n\n// Input: Enable glow colors\nenableGlow = input.bool(true, title="Enable Glow Colors")\n\n// Input: Long only option\nlongOnly = input.bool(false, title="Long Only")\n\n// Calculate the difference\noscillator = plot1 - plot2\n\n// Plot the oscillator with a glow effect if enabled\nplot(oscillator, title= "Oscillator", color=color.new(color.white, 20), linewidth=1)\nplot(oscillator, title= "Oscillator Glow 1", color=enableGlow ? color.new(color.fuchsia, 50) : na, linewidth=enableGlow ? 4 : na)\nplot(oscillator, title= "Oscillator Glow 2", color=enableGlow ? color.new(color.fuchsia, 70) : na, linewidth=enableGlow ? 8 : na)\n\n// Adding zero line for reference\nhline(0, "Zero Line", color=color.gray)\n\n// Long and Short Entries\nlongEntry = ta.crossover(oscillator, 0)\nshortEntry = ta.crossunder(oscillator, 0)\n\n// Long Exit (for long-only mode)\nlongExit = ta.crossunder(oscillator, 0)\n\n// Plot shapes for entries and exits\nplotshape(series=(longEntry), style=shape.triangleup, location=location.bottom, color=color.rgb(0, 230, 118, 50), size=size.tiny, title = "Cross Over")\nplotshape(series=(shortEntry), style=shape.triangledown, location=location.top, color=color.rgb(136, 14, 79, 50), size=size.tiny, title = "Cross Under")\n\n// Strategy entries and exits\nif longEntry\n    strategy.entry("Long", strategy.long)\n\nif longExit and longOnly\n    strategy.close("Long")\n\nif shortEntry and not longOnly\n    strategy.entry("Short", strategy.short)\n'

class SM1E9A024BF05D1B19(PinePortBase, IStrategy):
    source_id = "SM_1e9a024bf05d1b19"
    source_file = '自定义信号振荡器策略-CSO-Custom-Signal-Oscillator-Strategy-CSO.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'enableGlow': True, 'longOnly': False}
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
