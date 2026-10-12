"""batch_011 port of 移动平均交叉优化策略Optimized-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-27 00:00:00\nend: 2024-02-03 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ashishchauhan\nstrategy(title="MA CO Strategy Test", overlay=true, pyramiding=0, initial_capital=100000)\n\nfastEMALen = input(title="Fast EMA Length", type=input.integer, defval=50)\nslowEMALen = input(title="Slow EMA Length", type=input.integer, defval=100)\n\nfastEMA = ema(close, fastEMALen)\nslowEMA = ema(close, slowEMALen)\n\nenterLong = crossover(fastEMA, slowEMA)\nenterShort = crossunder(fastEMA, slowEMA)\n\nlongStop = 0.0\nlongStop := enterShort ? close : longStop[1]\n\nshortStop = 0.0\nshortStop := enterLong ? close : shortStop[1]\n\nplot(series=fastEMA, color=color.orange, title="Fast EMA")\nplot(series=slowEMA, color=color.teal, linewidth=3, title="Slow EMA")\n\nif enterLong\n    strategy.entry(id="GoLong", long=true)\n\nif enterShort\n    strategy.entry(id="GoShort", long=false)\n\nif strategy.position_size > 0\n    strategy.exit(id="ExLong", from_entry="GoLong", stop=longStop)\n\nif strategy.position_size < 0\n    strategy.exit(id="ExShort", from_entry="GoShort", stop=shortStop)\n\nstrategy.close_all()\n'

class SM3DECA311D0A856C3(PinePortBase, IStrategy):
    source_id = "SM_3deca311d0a856c3"
    source_file = '移动平均交叉优化策略Optimized-Moving-Average-Crossover-Strategy.md'
    timeframe = '15m'
    can_short = False
    source_defaults = {'fastEMALen': 50, 'slowEMALen': 100}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 100000
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
