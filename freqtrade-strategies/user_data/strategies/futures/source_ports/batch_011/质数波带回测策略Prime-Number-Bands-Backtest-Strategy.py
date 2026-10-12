"""batch_011 port of 质数波带回测策略Prime-Number-Bands-Backtest-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-08 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 27/03/2018\n// Determining market trends has become a science even though a high number \n// or people still believe it’s a gambling game. Mathematicians, technicians, \n// brokers and investors have worked together in developing quite several \n// indicators to help them better understand and forecast market movements.\n// The Prime Number Bands indicator was developed by Modulus Financial Engineering \n// Inc. This indicator is charted by indentifying the highest and lowest prime number \n// in the neighborhood and plotting the two series as a band.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n//  - For purpose educate only\n//  - This script to change bars colors.\n////////////////////////////////////////////////////////////\nPrimeNumberUpBand(price, percent) =>\n    res = 0\n    res1 = 0\n    for j = price to price + (price * percent / 100)\n        res1 := j\n\t    for i = 2 to sqrt(price)\n        \tres1 := iff(j % i == 0 , 0, j)\n            if res1 == 0 \n                break\n\t\tif res1 > 0 \n\t\t    break\n    res := iff(res1 == 0, res[1], res1)\n    res\n\nPrimeNumberDnBand(price, percent) =>\n    res = 0\n    res2 = 0\n    for j = price to price - (price * percent / 100)\n        res2 := j\n\t    for i = 2 to sqrt(price)\n        \tres2 := iff(j % i == 0 , 0, j)\n            if res2 == 0 \n                break\n\t\tif res2 > 0 \n\t\t    break\n    res := iff(res2 == 0, res[1], res2)\n    res\n\nstrategy(title="Prime Number Bands Backtest", overlay = true)\npercent = input(5, minval=0.01, step = 0.01, title="Tolerance Percentage")\nLength = input(5, minval=1)\nsrcUp = input(title="Source Up Band",  defval=high)\nsrcDn = input(title="Source Down Band",  defval=low)\nreverse = input(false, title="Trade reverse")\nxPNUB = PrimeNumberUpBand(srcUp, percent)\nxPNDB = PrimeNumberDnBand(srcDn, percent)\nxHighestPNUB = highest(xPNUB, Length)\nxLowestPNUB = lowest(xPNDB, Length)\npos = iff(close > xHighestPNUB[1], 1,\n       iff(close < xLowestPNUB[1], -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(xHighestPNUB, color=red, title="PNUp")\nplot(xLowestPNUB, color=green, title="PNDn")'

class SM6A0945A778EDC8C7(PinePortBase, IStrategy):
    source_id = "SM_6a0945a778edc8c7"
    source_file = '质数波带回测策略Prime-Number-Bands-Backtest-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'percent': 5, 'Length': 5, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
