"""batch_011 port of 自适应考夫曼移动平均线趋势跟踪策略Adaptive-Kaufman-Moving-Average-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-03 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 25/08/2017\n// Everyone wants a short-term, fast trading trend that works without large\n// losses. That combination does not exist. But it is possible to have fast\n// trading trends in which one must get in or out of the market quickly, but\n// these have the distinct disadvantage of being whipsawed by market noise\n// when the market is volatile in a sideways trending market. During these\n// periods, the trader is jumping in and out of positions with no profit-making\n// trend in sight. In an attempt to overcome the problem of noise and still be\n// able to get closer to the actual change of the trend, Kaufman developed an\n// indicator that adapts to market movement. This indicator, an adaptive moving\n// average (AMA), moves very slowly when markets are moving sideways but moves\n// swiftly when the markets also move swiftly, change directions or break out of\n// a trading range.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="Kaufman Moving Average Adaptive (KAMA)", shorttitle="Kaufman Moving Average Adaptive (KAMA)", overlay = true)\nLength = input(21, minval=1)\nxPrice = close\nxvnoise = abs(xPrice - xPrice[1])\nnfastend = 0.666\nnslowend = 0.0645\nreverse = input(false, title="Trade reverse")\nnsignal = abs(xPrice - xPrice[Length])\nnnoise = sum(xvnoise, Length)\nnefratio = iff(nnoise != 0, nsignal / nnoise, 0)\nnsmooth = pow(nefratio * (nfastend - nslowend) + nslowend, 2) \nnAMA = nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))\npos = iff(close[1] > nAMA, 1,\n\t   iff(close[1] < nAMA, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )    \nplot(nAMA, color=blue, title="KAMA")\n'

class SMD1479F86DC9F52E8(PinePortBase, IStrategy):
    source_id = "SM_d1479f86dc9f52e8"
    source_file = '自适应考夫曼移动平均线趋势跟踪策略Adaptive-Kaufman-Moving-Average-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 21, 'reverse': False}
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
