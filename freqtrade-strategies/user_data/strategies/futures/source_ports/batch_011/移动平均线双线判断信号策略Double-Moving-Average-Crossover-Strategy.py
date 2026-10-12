"""batch_011 port of 移动平均线双线判断信号策略Double-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-26 00:00:00\nend: 2023-12-26 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//Author: HighProfit\n\n//Lead-In\nstrategy("Parabolic SAR & Arnoud Legoux Moving Avarage Strategy", shorttitle="ST-PSAR+ALMA", overlay=true)\n\n//Arnoud Legoux Moving Avarage Inputs\nsource = close\nwindowsize = input(title="Window Size",defval=50)\noffset = input(title="Offset", type=float, defval=0.85)\nsigma = input(title="Sigma", type=float, defval=6)\n\n//Parabolic SAR Inputs\nstart = input(title="Start", type=float, defval=0.02)\nincrease = input(title="Increase", type=float, defval=0.02)\nmax = input(title="Max", type=float, defval=.2)\n\n//Conditions\nlongCondition = close>open and sar(start, increase, max) < low and crossover(close, alma(source, windowsize, offset, sigma))\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = close<open and sar(start, increase, max) > high and crossunder(close, alma(source, windowsize, offset, sigma))\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n//Plots   \nplot(alma(source, windowsize, offset, sigma), linewidth=2, title="ALMA")\nplot(sar(start, increase, max), style=circles, linewidth=2, title="PSAR")'

class SM3344BC7D349AF73C(PinePortBase, IStrategy):
    source_id = "SM_3344bc7d349af73c"
    source_file = '移动平均线双线判断信号策略Double-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'windowsize': 50, 'offset': 0.85, 'sigma': 6, 'start': 0.02, 'increase': 0.02, 'max': 0.2}
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
