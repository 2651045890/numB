"""batch_011 port of 行情反转关键点策略WMX-Williams-Fractals-Reversal-Pivot-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-14 00:00:00\nend: 2023-12-14 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © WMX_Q_System_Trading\n\n//@version=4\nSystemName="WMX Williams Fractals strategy V4"\nInitCapital = 1000000\nInitPosition = 100\nInitCommission = 0.075\nInitPyramidMax = 10\nstrategy(title=SystemName, shorttitle=SystemName, overlay=true, initial_capital=InitCapital, default_qty_type=strategy.percent_of_equity, default_qty_value=InitPosition, commission_type=strategy.commission.percent, commission_value=InitCommission)\n\n\n//study("WMX Williams Fractals", shorttitle="WMX Fractals", format=format.price, precision=0, overlay=true)\n// Define "n" as the number of periods and keep a minimum value of 2 for error handling.\nn = input(title="Periods", defval=2, minval=2, type=input.integer)\nh=close\nl=close\n\nfactorh(High)=>\n    upFractal = (                                                                                                          (High[n+2]  < High[n]) and (High[n+1]  < High[n]) and (High[n-1] < High[n]) and (High[n-2] < High[n]))\n             or (                                                                               (High[n+3]  < High[n]) and (High[n+2]  < High[n]) and (High[n+1] == High[n]) and (High[n-1] < High[n]) and (High[n-2] < High[n]))\n             or (                                                    (High[n+4]  < High[n]) and (High[n+3]  < High[n]) and (High[n+2] == High[n]) and (High[n+1] <= High[n]) and (High[n-1] < High[n]) and (High[n-2] < High[n]))\n             or (                          (High[n+5] < High[n]) and (High[n+4]  < High[n]) and (High[n+3] == High[n]) and (High[n+2] == High[n]) and (High[n+1] <= High[n]) and (High[n-1] < High[n]) and (High[n-2] < High[n]))\n             or ((High[n+6] < High[n]) and (High[n+5] < High[n]) and (High[n+4] == High[n]) and (High[n+3] <= High[n]) and (High[n+2] == High[n]) and (High[n+1] <= High[n]) and (High[n-1] < High[n]) and (High[n-2] < High[n]))\n    upFractal\nupFractal=factorh(h)\nfactorl(Low)=>\n    dnFractal = (                                                                                                  (Low[n+2]  > Low[n]) and (Low[n+1]  > Low[n]) and (Low[n-1] > Low[n]) and (Low[n-2] > Low[n]))\n             or (                                                                         (Low[n+3]  > Low[n]) and (Low[n+2]  > Low[n]) and (Low[n+1] == Low[n]) and (Low[n-1] > Low[n]) and (Low[n-2] > Low[n]))\n             or (                                                (Low[n+4]  > Low[n]) and (Low[n+3]  > Low[n]) and (Low[n+2] == Low[n]) and (Low[n+1] >= Low[n]) and (Low[n-1] > Low[n]) and (Low[n-2] > Low[n]))\n             or (                        (Low[n+5] > Low[n]) and (Low[n+4]  > Low[n]) and (Low[n+3] == Low[n]) and (Low[n+2] == Low[n]) and (Low[n+1] >= Low[n]) and (Low[n-1] > Low[n]) and (Low[n-2] > Low[n]))\n             or ((Low[n+6] > Low[n]) and (Low[n+5] > Low[n]) and (Low[n+4] == Low[n]) and (Low[n+3] >= Low[n]) and (Low[n+2] == Low[n]) and (Low[n+1] >= Low[n]) and (Low[n-1] > Low[n]) and (Low[n-2] > Low[n]))\n    \ndnFractal=factorl(l)\n\nU=valuewhen(upFractal[0]!= upFractal[1],l[0],3)\nL=valuewhen(dnFractal[0]!=dnFractal[1],h[0],3)\n\nlongcon=crossover(close ,L) and close>open\nshortcon=crossunder(close ,U) and close<open\n\nif longcon\n    \n    strategy.entry("Long", strategy.long,   when = strategy.position_size <= 0 )\n    \nif  shortcon\n    strategy.entry("Short", strategy.short,  when = strategy.position_size >= 0 )\n        \n\n\n\n\n'

class SM888D3301A7EBBB01(PinePortBase, IStrategy):
    source_id = "SM_888d3301a7ebbb01"
    source_file = '行情反转关键点策略WMX-Williams-Fractals-Reversal-Pivot-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'n': 2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
