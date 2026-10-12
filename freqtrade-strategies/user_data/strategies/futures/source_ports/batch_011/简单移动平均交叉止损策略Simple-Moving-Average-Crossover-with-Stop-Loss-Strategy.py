"""batch_011 port of 简单移动平均交叉止损策略Simple-Moving-Average-Crossover-with-Stop-Loss-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-19 00:00:00\nend: 2023-09-18 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © realisticDove62527\n\n//@version=5\nstrategy("ROoT", overlay=true, margin_long=1, margin_short=1)\n\nlongCondition = ta.crossover(ta.sma(close, 5), ta.vwap(hlc3))\nif (longCondition)\n    strategy.entry("BUY", strategy.long)\n\nshortCondition = ta.crossunder(ta.sma(close, 5), ta.vwap(hlc3))\nif (shortCondition)\n    strategy.entry("SELL", strategy.short)\n    \n\nstoploss = ta.ema(close, 9)\n\n'

class SMF10EB2B05673D478(PinePortBase, IStrategy):
    source_id = "SM_f10eb2b05673d478"
    source_file = '简单移动平均交叉止损策略Simple-Moving-Average-Crossover-with-Stop-Loss-Strategy.md'
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
