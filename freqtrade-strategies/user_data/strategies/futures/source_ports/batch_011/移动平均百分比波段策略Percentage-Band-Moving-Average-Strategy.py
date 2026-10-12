"""batch_011 port of 移动平均百分比波段策略Percentage-Band-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-05 00:00:00\nend: 2023-12-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\nstrategy(title = "Percentage Band", overlay = true)\n\n\n//////////////// BAND  ////////////////////////////\nprice=close\nbandlength = input(50)\nbbupmult =input(2,step=0.1,title="Multiplier for Percent upper Band")\nbblowmult = input(2,step=0.1,title="Multiplier for Percent Lower  Band")\n\nbasis =  sma(close,bandlength)\n\ndevup =  (bbupmult*price)/100\ndevlow = (bblowmult*price)/100\n\nupper = basis + devup\nlower = basis - devlow\nplot(basis, color=red)\np1 = plot(upper, color=blue)\np2 = plot(lower, color=blue)\nfill(p1, p2)\n\n\n\n/////////////////////////BAND  //////////////////////////\n\n\n// Conditions\n\n\n\nlongCond = na\nsellCond = na\nlongCond :=  crossover(price,lower)\nsellCond :=  crossunder(price,upper)\n\n\n\n\nmonthfrom =input(6)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\n\n\n\nif (  longCond  ) \n    strategy.entry("BUY", strategy.long, stop=close, oca_name="TREND",comment="BUY")\n    \nelse\n    strategy.cancel(id="BUY")\n\n\nif ( sellCond   ) \n\n    strategy.close("BUY")\n\n\n\n\n\n'

class SM9699B648043D57F4(PinePortBase, IStrategy):
    source_id = "SM_9699b648043d57f4"
    source_file = '移动平均百分比波段策略Percentage-Band-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'bandlength': 50, 'bbupmult': 2, 'bblowmult': 2, 'monthfrom': 6, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
