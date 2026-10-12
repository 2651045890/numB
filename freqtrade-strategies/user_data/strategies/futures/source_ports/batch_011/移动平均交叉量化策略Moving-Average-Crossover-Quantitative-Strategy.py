"""batch_011 port of 移动平均交叉量化策略Moving-Average-Crossover-Quantitative-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ZeroHeroTrading\n\n//@version=5\nstrategy("Simple 9/20 Crossover", overlay=true)\n\n// Define moving averages\nma9 = ta.sma(close, 9)\nma20 = ta.sma(close, 20)\n\n// Set persistent variable to keep track of crossover condition\nvar bool crossoverCondition = false\n\n// 9 MA crosses above 20 MA\n// Set crossover condition to true\nif ta.crossover(ma9, ma20)\n    crossoverCondition := true\n\n// 9 MA crosses under 20 MA\n// Reset crossover condition to false\nif ta.crossunder(ma9, ma20)\n    crossoverCondition := false   \n\n// Set buy and sell signals\nbuySignal = crossoverCondition and close > open and close > ma9\nsellSignal = close < ma9\n\n// Execute trades based on signals\nif (buySignal)\n    strategy.entry("Long", strategy.long)\n    // Avoid repeat entries by resetting crossover condition to false\n    crossoverCondition := false\n\nif (sellSignal)\n    strategy.close("Long")\n\n// Plot moving averages on the chart\nplot(ma9, color=color.blue)\nplot(ma20, color=color.red)\n'

class SME50CEF4EFDA8E1AB(PinePortBase, IStrategy):
    source_id = "SM_e50cef4efda8e1ab"
    source_file = '移动平均交叉量化策略Moving-Average-Crossover-Quantitative-Strategy.md'
    timeframe = '1h'
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
