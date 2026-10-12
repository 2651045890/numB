"""batch_012 port of 高点减指数移动平均线策略High-Minus-Exponential-Moving-Average-Stock-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-27 00:00:00\nend: 2023-12-03 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 20/16/2016\n// This indicator plots the difference between the High (of the previous period)\n// and an exponential moving average (13 period) of the Close (of the previous period).\n// You can use in the xPrice any series: Open, High, Low, Close, HL2, HLC3, OHLC4 and ect...\n// It buy if indicator above 0 and sell if below.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy(title="High - EMA Strategy Backtest", shorttitle="High - EMA Strategy")\nLength = input(13, minval=1)\nreverse = input(false, title="Trade reverse")\nxPrice = close  // You can use any series\nhline(0, color=red, linestyle=line)\nxEMA = ema(xPrice, Length)\nnRes = high[1] - nz(xEMA[1])\npos = iff(nRes > 0, 1,\n\t   iff(nRes < 0, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(nRes, color=blue, title="High - EMA") \n'

class SMHighMinusExponentialMovingAverageStockStrategy96df3b(PinePortBase, IStrategy):
    source_id = "SM_96df3bdc1a89671a"
    source_file = '高点减指数移动平均线策略High-Minus-Exponential-Moving-Average-Stock-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 13, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
