"""batch_011 port of 移动平均线动态止盈策略Moving-Average-Strategy-with-Dynamic-Profit-Target.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-10 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © dongyun\n\n//@version=4\nstrategy("利润目标止损的移动平均线", overlay=true)\n\nperiod = input(80,\'\')\nptper = input(252,\'\')\nptfactor = input(12,\'\')\nsizeper = input(20, \'\')\n\ntrend = 0.0\nsignal = 0\nsize = 1.0\ninvestment = 100000\natrange = 0.0\nptrange = 0.0\nstoph = 0.0\nstopl = 0.0\n\n\nif sizeper != 0\n\tatrange := atr(sizeper)\n\nif atrange == 0 or sizeper == 0 \n\tsize := 1\nelse\n\tsize := investment/atrange * 0.1\n\ntrend := sma(close,period)\n\n\nif signal != 1 and nz(trend[1]) < nz(trend[2]) and trend > nz(trend[1])\n\tstrategy.entry(\'long\',strategy.long, comment=\'open_long\')\n\tsignal := 1\nelse\n    signal := nz(signal[1])\n    \nif signal != -1 and nz(trend[1]) > nz(trend[2]) and trend < nz(trend[1])\n\tstrategy.entry(\'short\',strategy.short, comment=\'open_short\')\n\tsignal := -1\nelse\n    if signal == 0\n        signal := nz(signal[1])\n\nptrange := atr(ptper)\n\nif strategy.position_size > 0\n\tstrategy.exit("exit_long", "long", qty = strategy.position_size, limit = close + ptfactor*ptrange , comment=\'trail_long\') \nelse\n\tif strategy.position_size < 0\n\t\tstrategy.exit("exit_short", "short", qty = abs(strategy.position_size), limit = close - ptfactor*ptrange, comment=\'trail_short\')\n'

class SM05425FDB3B9AC6F6(PinePortBase, IStrategy):
    source_id = "SM_05425fdb3b9ac6f6"
    source_file = '移动平均线动态止盈策略Moving-Average-Strategy-with-Dynamic-Profit-Target.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'period': 80, 'ptper': 252, 'ptfactor': 12, 'sizeper': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
