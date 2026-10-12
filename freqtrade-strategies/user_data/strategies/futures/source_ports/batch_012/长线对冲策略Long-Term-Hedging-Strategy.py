"""batch_012 port of 长线对冲策略Long-Term-Hedging-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-14 00:00:00\nend: 2023-09-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © danilogalisteu\n\n//@version=4\nstrategy("Long Term L/S", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nbase = input("BMFBOVESPA:IBOV")\nperiod = input(5, \'SMA Period\', input.integer)\nresolution = input(title="SMA Resolution", type=input.resolution, defval=\'M\')\nstrat = input(title="Strategy", defval="Long/Short", options=["Long Only", "Long/Short", "Short Only"])\nstrat_val = strat == "Long Only" ? 1 : strat == "Long/Short" ? 0 : -1\n\nbase_cl = security((base), resolution, close)\nbase_ma = sma(base_cl, period)\n\nlongCondition = crossover(base_cl, base_ma)\nif (longCondition)\n    if strat_val > -1\n        strategy.entry("LONG", strategy.long)\n    if strat_val < 1\n        strategy.close("SHORT")\n\nshortCondition = crossunder(base_cl, base_ma)\nif (shortCondition)\n    if strat_val > -1\n        strategy.close("LONG")\n    if strat_val < 1\n        strategy.entry("SHORT", strategy.short)\n\n//plot(longCondition?1:0, \'L\', color.blue)\n//plot(shortCondition?-1:0, \'S\', color.red)\n'

class SMLongTermHedgingStrategyf323e9(PinePortBase, IStrategy):
    source_id = "SM_f323e9b4423a739a"
    source_file = '长线对冲策略Long-Term-Hedging-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'base': 'BMFBOVESPA:IBOV', 'period': 5, 'resolution': 'M', 'strat': 'Long/Short'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
