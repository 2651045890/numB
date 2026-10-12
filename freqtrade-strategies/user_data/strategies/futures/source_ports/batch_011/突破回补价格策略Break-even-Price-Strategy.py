"""batch_011 port of 突破回补价格策略Break-even-Price-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-15 00:00:00\nend: 2023-11-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © NikitaDoronin\n//@version=4\n\nstrategy("Plot Break-even Price", overlay=true)\n\n/// Break-even calculation\nep = 0.0\nep := na(ep[1]) ? na : ep[1]\n\np = 0.0\np := na(p[1]) ? na : p[1]\n\n/// Fees Input\nfee_inp = input(0.25, title=\'Price Change in %\', step=0.1)/100\n\n/// Your Strategy calculation\nlongCondition = crossover(sma(close, 14), sma(close, 28))\nshortCondition = crossunder(sma(close, 14), sma(close, 28))\n\n/// Stategy Entry\nif (longCondition)\n    ep := close\n    p := close * (1 + fee_inp)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nif (shortCondition)\n    ep := close\n    p := close * (1 - fee_inp)\n    strategy.entry("My Short Entry Id", strategy.short)\n\n/// Plot Break-even Price \np1 = plot(ep, color = color.red, transp = 85)\np2 = plot(p, color = color.green)\nfill(p1, p2, color = color.red, transp = 85)'

class SM8EF905D3284D822D(PinePortBase, IStrategy):
    source_id = "SM_8ef905d3284d822d"
    source_file = '突破回补价格策略Break-even-Price-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fee_inp': 0.25}
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
