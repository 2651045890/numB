"""batch_011 port of 移动平均线交叉趋势跟踪策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-29 00:00:00\nend: 2023-12-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © danielfepardo\n\n//@version=5\n\nstrategy("QUANT", overlay=true)\nlenght1 = input(20)\nlenght2 = input(50)\n\n\nema1 = ta.ema(close, lenght1)\nema2 = ta.ema(close, lenght2)\nplot(ema1, color=color.black)\nplot(ema2, color=color.red)\n\nlong = ta.crossover(ema1, ema2)\n\nSL = 0.004\nTP = 0.007\n\nif long == true\n    strategy.entry("Compra Call", strategy.long)\nlongstop=strategy.position_avg_price*(1-SL)\nlongprofit=strategy.position_avg_price*(1+TP)\nstrategy.exit("Venta Call", stop=longstop, limit=longprofit)\n\nshort = ta.crossover(ema2, ema1)\n\nif short == true\n    strategy.entry("Compra Put", strategy.short)\nshortstop=strategy.position_avg_price*(1+SL)\nshortprofit=strategy.position_avg_price*(1-TP)\nstrategy.exit("Venta Put", stop=shortstop, limit=shortprofit)\n\n\n\n\n'

class SM6A80990F97021C16(PinePortBase, IStrategy):
    source_id = "SM_6a80990f97021c16"
    source_file = '移动平均线交叉趋势跟踪策略Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lenght1': 20, 'lenght2': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
