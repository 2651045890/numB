"""batch_012 port of 通过计算价格波动性趋势突破策略Trend-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-26 00:00:00\nend: 2023-12-26 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v2.0 25/10/2017\n//\n//  This histogram displays (high-low)/close\n//  Can be applied to any time frame.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="(H-L)/C Histogram Backtest", precision = 2)\ninput_barwidth = input(4, title="Bar Width")\ninput_barsback = input(1, title="Look Back")\ninput_percentorprice = input(false, title="% change")\ninput_smalength = input(16, title="SMA Length")\nreverse = input(false, title="Trade reverse")\nhline(0, color=blue, linestyle=line)\nxPrice = (high-low)/close\nxPriceHL = (high-low)\nxPrice1 = iff(input_percentorprice, xPrice * 100, xPriceHL)\nxPrice1SMA = sma(abs(xPrice1), input_smalength)\npos = 0.0\npos := iff(xPrice1SMA[input_barsback] > abs(xPrice1), 1,\n\t   iff(xPrice1SMA[input_barsback] < abs(xPrice1), -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) \nplot(abs(xPrice1), color=green, style = histogram, linewidth = input_barwidth, title="Change")\nplot(xPrice1SMA[input_barsback], color=red, title="SMA")\n'

class SMTrendBreakoutStrategy94142a(PinePortBase, IStrategy):
    source_id = "SM_94142a05922ba640"
    source_file = '通过计算价格波动性趋势突破策略Trend-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'input_barwidth': 4, 'input_barsback': 1, 'input_percentorprice': False, 'input_smalength': 16, 'reverse': False}
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
