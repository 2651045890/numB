"""batch_011 port of 移动平均线穿越策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-21 00:00:00\nend: 2023-09-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © brandlabng\n\n//@version=5\n//study(title="Holly Grail FX", overlay = true)\nstrategy(\'HG|E30m\', overlay=true)\nsrc = input(close, title=\'Source\')\n\nprice = request.security(syminfo.tickerid, timeframe.period, src)\nma1 = input(20, title=\'1st MA Length\')\ntype1 = input.string(\'EMA\', \'1st MA Type\', options=[\'EMA\'])\n\nma2 = input(120, title=\'2nd MA Length\')\ntype2 = input.string(\'EMA\', \'2nd MA Type\', options=[\'EMA\'])\n\nprice1 = if type1 == \'EMA\'\n    ta.ema(price, ma1)\n\nprice2 = if type2 == \'EMA\'\n    ta.ema(price, ma2)\n\n\n//plot(series=price, style=line,  title="Price", color=black, linewidth=1, transp=0)\nplot(series=price1, style=plot.style_line, title=\'1st MA\', color=color.new(#219ff3, 0), linewidth=2)\nplot(series=price2, style=plot.style_line, title=\'2nd MA\', color=color.new(color.purple, 0), linewidth=2)\n\n\nlongCondition = ta.crossover(price1, price2)\nif longCondition\n    strategy.entry(\'Long\', strategy.long)\n\nshortCondition = ta.crossunder(price1, price2)\nif shortCondition\n    strategy.entry(\'Short\', strategy.short)'

class SMD438FF66241C850C(PinePortBase, IStrategy):
    source_id = "SM_d438ff66241c850c"
    source_file = '移动平均线穿越策略Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'ma1': 20, 'type1': 'EMA', 'ma2': 120, 'type2': 'EMA'}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
