"""batch_011 port of 趋势跟踪移动平均指标策略Moving-Average-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ceyhun\n\n//@version=4\nstrategy("Chaloke System Strategy",overlay=true)\n\nP1=input(9,title="ShortTerm Period")\nP2=input(15,title="MidTerm Period")\nP3=input(24,title="LongTerm Period")\nP4=input(5,title="Invesment Term")\nP5=input(5,title="ATR Period")\nBarcolor=input(true,title="Barcolor")\n\nSm=2*P5/10\nATRX=Sm*atr(P4)\nS=ema(close,P1)-ATRX\nM=ema(close,P2)-ATRX\nLg=ema(close,P3)-ATRX\n\nSht=iff(close==highest(close,3),S,ema(close[1],P1)-ATRX)\nMid=iff(close==highest(close,3),M,ema(close[1],P2)-ATRX)\nLng=iff(close==highest(close,3),Lg,ema(close[1],P3)-ATRX)\n\ncolors=iff(Sht>Mid and close > Sht ,color.green,iff(close < Lng or Sht<Lng,color.red,color.black))\n\nplot(Sht,"Short",color=color.green,linewidth=2)\nplot(Mid,"Middle",color=color.black,linewidth=2)\nplot(Lng,"Long",color=color.red,linewidth=2)\n\nbarcolor(Barcolor ? colors :na)\n   \nlong =  crossover(Sht,Mid) and close > Sht\nshort = crossunder(Sht,Lng) or close < Lng\n\nif long\n    strategy.entry("Long", strategy.long, comment="Long")\n    \nif short\n    strategy.entry("Short", strategy.short, comment="Short")\n\nalertcondition(long, title=\'Long\', message=\'Chaloke System Alert Long\')\nalertcondition(short, title=\'Short\', message=\'Chaloke System Alert Short\')'

class SM69B95CD27721E6E8(PinePortBase, IStrategy):
    source_id = "SM_69b95cd27721e6e8"
    source_file = '趋势跟踪移动平均指标策略Moving-Average-Trend-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'P1': 9, 'P2': 15, 'P3': 24, 'P4': 5, 'P5': 5, 'Barcolor': True}
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
