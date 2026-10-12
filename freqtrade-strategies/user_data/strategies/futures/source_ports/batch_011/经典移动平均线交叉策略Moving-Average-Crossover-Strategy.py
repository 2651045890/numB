"""batch_011 port of 经典移动平均线交叉策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-31 00:00:00\nend: 2023-11-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//TMA strategy I came across, uses sma to display entry/exit points for both margin and non margin trading. The buy/sell signals as well as syntax are hidden behind comments if you scroll down.\n//Change the commented fields for margin or spot trading!\n//@version=3\nstrategy("MP Rollercoaster Strat", overlay=true)\n\nbgcolor ( color=black, transp=0, title=\'Blackground\', editable=true)\n\nx = input(close, "Red")\nn = input(10, "periods")\ntrima = sma(sma(x,n), n)\n\nkisa=input(5, "Green")\nsma = sma(close, kisa)\n\nbull = (sma>trima)\nfill(plot(sma, color = green), plot(trima, color=red), bull ? green : red)\n\n//Conditions\nbuy_signal = crossover(sma,trima)\nsell_signal = crossunder(sma,trima)\n\nplotshape(sell_signal, style=shape.triangleup, color = red, text="Short")\nplotshape(buy_signal, style=shape.triangledown, color = green, text="Long")\n//plotshape(sell_signal, style=shape.triangleup, color = red, text="Sell")\n//plotshape(buy_signal, style=shape.triangledown, color = green, text="Buy")\n\nalertcondition(sell_signal, title = \'Short\', message = \'e= s= c=position b=long t=market l= | delay=30 | e= s= b=short l= t=market q=0.01\')\nalertcondition(buy_signal, title = \'Long\', message =  \'e= s= c=position b=short t=market l= | delay=30 | e= s= b=long l= t=market q=0.01\')\n\n//alertcondition(sell_signal, title = \'Sell\', message = \'e= s= c=order b=buy | delay=3 | e= b=sell q=99% p=0.70% u=currency\')\n//alertcondition(buy_signal, title = \'Buy\', message =  \'e= s= c=order b=sell | delay=30 | e= b=buy q=80 p=0.1% u=currency\')\n\ntestStartYear = input(2018, "From Year") \ntestStartMonth = input(4, "From Month")\ntestStartDay = input(1, "From Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2019, "To Year")\ntestStopMonth = input(1, "To Month")\ntestStopDay = input(1, "To Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\ntestPeriod() => true\n\nif testPeriod()\n    if buy_signal\n        strategy.entry("Long", true)\n    \n\n    if sell_signal\n        strategy.close("Long")'

class SM128DD2B16D82C5D9(PinePortBase, IStrategy):
    source_id = "SM_128dd2b16d82c5d9"
    source_file = '经典移动平均线交叉策略Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'n': 10, 'kisa': 5, 'testStartYear': 2018, 'testStartMonth': 4, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 1, 'testStopDay': 1}
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
