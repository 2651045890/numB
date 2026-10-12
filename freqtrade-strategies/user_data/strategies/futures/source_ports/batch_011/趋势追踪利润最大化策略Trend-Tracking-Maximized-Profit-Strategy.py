"""batch_011 port of 趋势追踪利润最大化策略Trend-Tracking-Maximized-Profit-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-10 00:00:00\nend: 2023-10-10 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ErdemDemir\n\n//@version=4\nstrategy("Lawyers Trend Pro Strategy", shorttitle="Lawyers Trend Pro Strategy", overlay=true)\n\nsrc = close\nmult = 2.0\nbasis = sma(src, 20)\ndev = mult * stdev(src, 20)\nupper = basis + dev\nlower = basis - dev\noffset = 0\n\n\nlower2 = lowest(20)\nupper2 = highest(20)\nbasis2 = avg(upper2, lower2)\n\n\nMB= (basis+basis2)/2\n\n\n\n\n\ncol1=close>MB\ncol3=MB>close\ncolorE = col1 ? color.blue : col3 ? color.red : color.yellow\np3=plot(MB, color=colorE, linewidth=3)\n\n// Deternine if we are currently LONG\nisLong = false\nisLong := nz(isLong[1], false)\n\n// Determine if we are currently SHORT\nisShort = false\nisShort := nz(isShort[1], false)\n\n// Buy only if the buy signal is triggered and we are not already long\nbuySignal = not isLong and crossover(close,MB)\n\n// Sell only if the sell signal is triggered and we are not already short\nsellSignal= not isShort and crossover(MB,close)\nif (buySignal)\n    isLong := true\n    isShort := false\n\nif (sellSignal)\n    isLong := false\n    isShort := true\n\n\n\n\n\n\n\n/// LONG\nstrategy.entry("long", true , when = buySignal, comment="Open Long")\n\nstrategy.close("long", when=sellSignal, comment = "Close Long")\n\n/// SHORT\nstrategy.entry("short", false,  when = sellSignal, comment="Open Short")\n\nstrategy.close("short", when=buySignal, comment = "Close Short")\n\n'

class SM25DFE964C6615FE1(PinePortBase, IStrategy):
    source_id = "SM_25dfe964c6615fe1"
    source_file = '趋势追踪利润最大化策略Trend-Tracking-Maximized-Profit-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
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
