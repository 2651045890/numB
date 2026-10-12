"""batch_012 port of 震荡波动优异指标交易策略Bill-Williams-Awesome-Oscillator-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-12 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 29/12/2016\n//    This indicator is based on Bill Williams` recommendations from his book \n//    "New Trading Dimensions". We recommend this book to you as most useful reading.\n//    The wisdom, technical expertise, and skillful teaching style of Williams make \n//    it a truly revolutionary-level source. A must-have new book for stock and \n//    commodity traders.\n//    The 1st 2 chapters are somewhat of ramble where the author describes the \n//    "metaphysics" of trading. Still some good ideas are offered. The book references \n//    chaos theory, and leaves it up to the reader to believe whether "supercomputers" \n//    were used in formulating the various trading methods (the author wants to come across \n//    as an applied mathemetician, but he sure looks like a stock trader). There isn\'t any \n//    obvious connection with Chaos Theory - despite of the weak link between the title and \n//    content, the trading methodologies do work. Most readers think the author\'s systems to \n//    be a perfect filter and trigger for a short term trading system. He states a goal of \n//    10%/month, but when these filters & axioms are correctly combined with a good momentum \n//    system, much more is a probable result.\n//    There\'s better written & more informative books out there for less money, but this author \n//    does have the "Holy Grail" of stock trading. A set of filters, axioms, and methods which are \n//    the "missing link" for any trading system which is based upon conventional indicators.\n//    This indicator plots the oscillator as a histogram where periods fit for buying are marked \n//    as blue, and periods fit for selling as red. If the current value of AC (Awesome Oscillator) \n//    is over the previous, the period is deemed fit for buying and the indicator is marked blue. \n//    If the AC values is not over the previous, the period is deemed fir for selling and the indicator \n//    is marked red.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n////////////////////////////////////////////////////////////\nstrategy("Bill Williams. Awesome Oscillator (AO)")\nnLengthSlow = input(34, minval=1, title="Length Slow")\nnLengthFast = input(5, minval=1, title="Length Fast")\nreverse = input(false, title="Trade reverse")\nxSMA1_hl2 = sma(hl2, nLengthFast)\nxSMA2_hl2 = sma(hl2, nLengthSlow)\nxSMA1_SMA2 = xSMA1_hl2 - xSMA2_hl2\ncClr = xSMA1_SMA2 > xSMA1_SMA2[1] ? blue : red\npos = iff(xSMA1_SMA2 > xSMA1_SMA2[1], 1,\n\t   iff(xSMA1_SMA2 < xSMA1_SMA2[1], -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )\nplot(xSMA1_SMA2, style=histogram, linewidth=1, color=cClr)\n'

class SMBillWilliamsAwesomeOscillatorTradingStrategye4c780(PinePortBase, IStrategy):
    source_id = "SM_e4c780a60908ceb2"
    source_file = '震荡波动优异指标交易策略Bill-Williams-Awesome-Oscillator-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'nLengthSlow': 34, 'nLengthFast': 5, 'reverse': False}
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
