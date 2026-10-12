"""batch_011 port of 自适应通道突破策略Adaptive-Channel-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-29 00:00:00\nend: 2024-02-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Turtle Trade Channels Strategy", shorttitle="TTCS", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nlength = input(20,"Entry Length", minval=1)\nlen2=input(10, "Exit Length", minval=1)\n\nlower = lowest(length)\nupper = highest(length)\n\nup=highest(high,length)\ndown=lowest(low,length)\nsup=highest(high,len2)\nsdown=lowest(low,len2)\nK1=barssince(high>=up[1])<=barssince(low<=down[1]) ? down : up\nK2=iff(barssince(high>=up[1])<=barssince(low<=down[1]),sdown,sup)\nK3=iff(close>K1,down,na)\nK4=iff(close<K1,up,na)\n\nbuySignal=high==upper[1] or crossover(high,upper[1])\nsellSignal = low==lower[1] or crossover(lower[1],low)\nbuyExit=low==sdown[1] or crossover(sdown[1],low)\nsellExit = high==sup[1] or crossover(high,sup[1])\n\nstrategy.entry("Buy", strategy.long, when = buySignal and barssince(buySignal) < barssince(sellSignal[1]))\nstrategy.entry("Sell", strategy.short, when = sellSignal and barssince(sellSignal) < barssince(buySignal[1]))\nstrategy.exit("Buy Exit", from_entry = "Buy", when = buyExit and barssince(buyExit) < barssince(sellExit[1]))\nstrategy.exit("Sell Exit", from_entry = "Sell", when = sellExit and barssince(sellExit) < barssince(buyExit[1]))\n\nplot(K1, title="Trend Line", color=color.red, linewidth=2)\ne=plot(K2, title="Exit Line", color=color.blue, linewidth=1, style=6)\n\n'

class SMDD270E14D26842A3(PinePortBase, IStrategy):
    source_id = "SM_dd270e14d26842a3"
    source_file = '自适应通道突破策略Adaptive-Channel-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'len2': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
