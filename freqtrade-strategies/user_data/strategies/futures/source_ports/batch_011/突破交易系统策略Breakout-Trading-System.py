"""batch_011 port of 突破交易系统策略Breakout-Trading-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-14 00:00:00\nend: 2024-02-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0\n\n//Break out trading system works best in a weekly chart and daily chart of Nifty and BankNifty\n//@version=4\n\nstrategy("Eswar New",shorttitle = "ESW")\nlength = input(20, minval=1)\nexit = input(1, minval=1, maxval=2,title = "Exit Option") // Use Option 1 to exit using lower band; Use Option 2 to exit using basis line\n\nlower = lowest(length)\nupper = highest(length)\nbasis = avg(upper, lower)\n\nl = plot(lower, color=color.blue)\nu = plot(upper, color=color.blue)\nplot(basis, color=color.orange)\nfill(u, l, color=color.blue)\n\nlongCondition = crossover(close,upper[1])\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif(exit==1)\n    if (crossunder(close,lower[1]))\n        strategy.close("Long")\n\nif(exit==2) \n    if (crossunder(close,basis[1]))\n        strategy.close("Long")\n'

class SMBAC3B9142689E10D(PinePortBase, IStrategy):
    source_id = "SM_bac3b9142689e10d"
    source_file = '突破交易系统策略Breakout-Trading-System.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 20, 'exit': 1}
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
