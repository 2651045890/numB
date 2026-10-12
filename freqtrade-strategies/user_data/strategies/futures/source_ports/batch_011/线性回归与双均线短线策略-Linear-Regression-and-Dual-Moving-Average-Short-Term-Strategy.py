"""batch_011 port of 线性回归与双均线短线策略-Linear-Regression-and-Dual-Moving-Average-Short-Term-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-26 00:00:00\nend: 2024-01-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(\'LR&SSL_Short\', overlay=true)\nstartP = timestamp(input(2017, "Start Year"), input(12, "Month"), input(17, "Day"), 0, 0)\nend   = timestamp(9999,1,1,0,0)\n_testPeriod() => true\n\nlen = input(title="Period", defval=89)\nsmaHigh = linreg(high, len, 0)\nsmaLow = linreg(low, len, -1)\nHlv = 0.0\nHlv := close > smaHigh ? 1 : close < smaLow ? -1 : Hlv[1]\nsslDown = Hlv < 0 ? smaHigh : smaLow\nsslUp = Hlv < 0 ? smaLow : smaHigh\n\nplot(sslDown, linewidth=2, color=color.red)\nplot(sslUp, linewidth=2, color=color.lime)\n\n\n\nlength = input(200, title="DEMA") \nd1 = ema(close, length)                                               \nd2 = 2 * d1 - ema(d1, length)                                         \ntrendColour = d2 > d1 ? #AAFFAA : #FFAAAA \ndema=sma(d2,length) \n\nturnGreen = d2 > d1 and d2[1] <= d1[1]  \nturnRed   = d2 <= d1 and d2[1] > d1[1]  \n\nup =turnGreen \ndown=turnRed \n  \nplotshape(down, title="down", style=shape.triangledown,location=location.abovebar, color=color.red, transp=0, size=size.small) \nplotshape(up,  title="up", style=shape.triangleup,location=location.belowbar, color=color.green, transp=0, size=size.small) \nplot(dema, color = trendColour,linewidth=3 ,transp = 0)\nbgcolor(close > dema ? color.green : color.red)\n\nstrategy.entry("short", strategy.short, when= crossunder(sslUp, sslDown) and dema > close and _testPeriod())\nstrategy.close("short", when = crossover(sslUp, sslDown) or crossover(close, dema))\n'

class SM7E4086EC18BFA8C1(PinePortBase, IStrategy):
    source_id = "SM_7e4086ec18bfa8c1"
    source_file = '线性回归与双均线短线策略-Linear-Regression-and-Dual-Moving-Average-Short-Term-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'len': 89, 'length': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
