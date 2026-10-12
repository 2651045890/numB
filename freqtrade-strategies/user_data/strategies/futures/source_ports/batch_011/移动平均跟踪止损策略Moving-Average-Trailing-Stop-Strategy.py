"""batch_011 port of 移动平均跟踪止损策略Moving-Average-Trailing-Stop-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2023-09-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n//created by XPloRR 04-03-2018\n\nstrategy("XPloRR MA-Trailing-Stop Strategy",overlay=true, initial_capital=1000,default_qty_type=strategy.percent_of_equity,default_qty_value=100)\n\ntestStartYear = input(2005, "Start Year")\ntestStartMonth = input(1, "Start Month")\ntestStartDay = input(1, "Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2050, "Stop Year")\ntestStopMonth = input(12, "Stop Month")\ntestStopDay = input(31, "Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\ntestPeriodBackground = input(title="Background", type=bool, defval=true)\ntestPeriodBackgroundColor = testPeriodBackground and (time >= testPeriodStart) and (time <= testPeriodStop) ? #00FF00 : na\nbgcolor(testPeriodBackgroundColor, transp=97)\n\nema1Period = input(12, "Fast EMA Buy")\nsma1Period = input(54, "Slow SMA Buy")\nstrength1 = input(52, "Minimum Buy Strength")\n\nema2Period = input(18, "Fast EMA Sell")\nsma2Period = input(55, "Slow SMA Sell")\nstrength2 = input(100, "Minimum Sell Strength")\n\ndelta = input(8, "Trailing Stop (#ATR)")\n\ntestPeriod() => true\n\nema1val=ema(close,ema1Period)\nsma1val=sma(close,sma1Period)\nema1strength=10000*(ema1val-ema1val[1])/ema1val[1]\n\nema2val=ema(close,ema2Period)\nsma2val=sma(close,sma2Period)\nema2strength=10000*(ema2val-ema2val[1])/ema2val[1]\n\nplot(ema1val,color=blue,linewidth=1)\nplot(sma1val,color=orange,linewidth=1)\nplot(ema2val,color=navy,linewidth=1)\nplot(sma2val,color=red,linewidth=1)\n\nlong=crossover(ema1val,sma1val) and (ema1strength > strength1) \nshort=crossunder(ema2val,sma2val) and (ema2strength < -strength2)\n\nstopval=ema(close,6)\natr=sma((high-low),15)\n\ninlong=0\nbuy=0\nstop=0\nif testPeriod()\n    if (inlong[1])\n        inlong:=inlong[1]\n        buy:=close\n        stop:=iff((stopval>(stop[1]+delta*atr)),stopval-delta*atr,stop[1])\n    if (long) and (not inlong[1])\n        strategy.entry("buy",strategy.long)\n        inlong:=close\n        buy:=close\n        stop:=stopval-delta*atr\nplot(buy,color=iff(close<inlong,red,lime),style=columns,transp=90,linewidth=1)\nplot(stop,color=iff((short or (stopval<stop)) and (close<inlong),red,lime),style=columns,transp=60,linewidth=1)\nif testPeriod()\n    if (short or (stopval<stop)) and (inlong[1])\n        strategy.close("buy")\n        inlong:=0\n        stop:=0\n        buy:=0\n\n'

class SM328C61C84E01AC58(PinePortBase, IStrategy):
    source_id = "SM_328c61c84e01ac58"
    source_file = '移动平均跟踪止损策略Moving-Average-Trailing-Stop-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'testStartYear': 2005, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2050, 'testStopMonth': 12, 'testStopDay': 31, 'testPeriodBackground': True, 'ema1Period': 12, 'sma1Period': 54, 'strength1': 52, 'ema2Period': 18, 'sma2Period': 55, 'strength2': 100, 'delta': 8}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
