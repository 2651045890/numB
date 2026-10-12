"""batch_011 port of 移动平均线叠带策略EMA-Ribbon-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-14 00:00:00\nend: 2024-01-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="EMA Ribbon [Krypt] with Buy/Sell Signals", shorttitle="EMA Ribbon", overlay=true)\n\ndropn(src, n) =>\n    na(src[n]) ? na : src\n\nlength1 = input(20, title="MA-1 period", minval=1)\nlength2 = input(25, title="MA-2 period", minval=1)\nlength3 = input(30, title="MA-3 period", minval=1)\nlength4 = input(35, title="MA-4 period", minval=1)\nlength5 = input(40, title="MA-5 period", minval=1)\nlength6 = input(45, title="MA-6 period", minval=1)\nlength7 = input(50, title="MA-7 period", minval=1)\nlength8 = input(55, title="MA-8 period", minval=1)\nsource_input = input(close, title="Source")\n\nprice = dropn(source_input, 1)\n\nema1 = ema(price, length1)\nema2 = ema(price, length2)\nema3 = ema(price, length3)\nema4 = ema(price, length4)\nema5 = ema(price, length5)\nema6 = ema(price, length6)\nema7 = ema(price, length7)\nema8 = ema(price, length8)\n\nplot(ema1, title="MA-1", color=#f5eb5d, transp=0, linewidth=2)\nplot(ema2, title="MA-2", color=#f5b771, transp=0, linewidth=2)\nplot(ema3, title="MA-3", color=#f5b056, transp=0, linewidth=2)\nplot(ema4, title="MA-4", color=#f57b4e, transp=0, linewidth=2)\nplot(ema5, title="MA-5", color=#f56d58, transp=0, linewidth=2)\nplot(ema6, title="MA-6", color=#f57d51, transp=0, linewidth=2)\nplot(ema7, title="MA-7", color=#f55151, transp=0, linewidth=2)\nplot(ema8, title="MA-8", color=#aa2707, transp=0, linewidth=2)\n\n// Buy and sell signals based on crossover and crossunder\nbuySignal = crossover(ema1, ema8)\nsellSignal = crossunder(ema1, ema8)\n\nplotshape(series=buySignal, title="Buy Signal", color=color.green, style=shape.triangleup, size=size.small)\nplotshape(series=sellSignal, title="Sell Signal", color=color.red, style=shape.triangledown, size=size.small)\n\nif buySignal\n    strategy.entry("Enter Long", strategy.long)\nelse if sellSignal\n    strategy.entry("Enter Short", strategy.short)'

class SM5C7F743D35DDF4F1(PinePortBase, IStrategy):
    source_id = "SM_5c7f743d35ddf4f1"
    source_file = '移动平均线叠带策略EMA-Ribbon-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length1': 20, 'length2': 25, 'length3': 30, 'length4': 35, 'length5': 40, 'length6': 45, 'length7': 50, 'length8': 55}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
