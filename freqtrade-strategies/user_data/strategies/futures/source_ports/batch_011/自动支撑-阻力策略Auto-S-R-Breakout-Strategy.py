"""batch_011 port of 自动支撑-阻力策略Auto-S-R-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2023-12-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © lukaRT\n\n//@version=5\nstrategy("Auto S/R Strategy", shorttitle="Auto S/R", overlay=true)\n\n// Ваши входные параметры\nleftBars = input.int(50, title="Left Bars")\nrightBars = input.int(25, title="Right Bars")\nquickRightBars = input.int(5, title="Quick Right Bars")\nsrc = input(close, title="Source")\n\npivotHigh = ta.pivothigh(src, leftBars, rightBars)\npivotLow = ta.pivotlow(src, leftBars, rightBars)\n\nquickPivotHigh = ta.pivothigh(src, leftBars, quickRightBars)\nquickPivotLow = ta.pivotlow(src, leftBars, quickRightBars)\n\n// Ваши уровни сопротивления и поддержки\nresistanceLevel1 = ta.valuewhen(quickPivotHigh, high[quickRightBars], 0)\nsupportLevel1 = ta.valuewhen(quickPivotLow, low[quickRightBars], 0)\n\n// Пересечение ценой уровней\nlongCondition = ta.crossover(close, supportLevel1)\nshortCondition = ta.crossunder(close, resistanceLevel1)\n\nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.entry("Short", strategy.short, when=shortCondition)\n\n// Отображение линий сопротивления и поддержки на графике\nplot(resistanceLevel1, color=color.red, title="Resistance Level 1")\nplot(supportLevel1, color=color.green, title="Support Level 1")\n'

class SMDDCAD27AE6F943E6(PinePortBase, IStrategy):
    source_id = "SM_ddcad27ae6f943e6"
    source_file = '自动支撑-阻力策略Auto-S-R-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'leftBars': 50, 'rightBars': 25, 'quickRightBars': 5}
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
