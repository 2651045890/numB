"""batch_011 port of 趋势消除MACD策略Trendless-MACD-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-23 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n\nstrategy(title = "Trendless MACD  Strategy",shorttitle="MACD-T Strategy",default_qty_type = strategy.percent_of_equity, default_qty_value = 100,commission_type=strategy.commission.percent,commission_value=0.01,initial_capital=100000)\n\n\n\nmaperiod=input(9)\nema=ema(close,maperiod)\n\n\nfastmacd = input(12,title=\'MACD Fast  Line Length\')\nslowmacd = input(26,title=\'MACD Slow Line Length\')\nsignalmacd = input(9,title=\'Signal Line Length\')\n\nmacdslowline1 = ema(ema,slowmacd)\nmacdslowline2 = ema(macdslowline1,slowmacd)\nDEMAslow = ((2 * macdslowline1) - macdslowline2 )\n\nmacdfastline1 = ema(ema,fastmacd)\nmacdfastline2 = ema(macdfastline1,fastmacd)\nDEMAfast = ((2 * macdfastline1) - macdfastline2)\n\nMACDLine = (DEMAfast - DEMAslow)\n\nSignalLine1 = ema(MACDLine, signalmacd)\nSignalLine2 = ema(SignalLine1, signalmacd)\nSignalLine = ((2 * SignalLine1) - SignalLine2 )\n\n\nMACDSignal = MACDLine-SignalLine\n\n\ncolorbar= MACDSignal>0?green:red\n\nplot(MACDSignal,color=colorbar,style=columns,title=\'Histogram\',histbase=0)\np1 = plot(MACDLine,color=blue,title=\'MACDLine\')\np2=plot(SignalLine,color=red,title="SignalLine")\nfill(p1,p2,color=blue)\n\n\nlongCond =  crossover(MACDLine,SignalLine) \n\nshortCond =  crossunder(MACDLine,SignalLine) \n\n\n\n\nmonthfrom =input(1)\nmonthuntil =input(12)\ndayfrom=input(1)\ndayuntil=input(31)\n\nyearfrom= input(2018)\nyearuntil=input(2021)\n\nif (  longCond   ) \n    strategy.entry("LONG", strategy.long, stop=close, oca_name="TREND",  comment="LONG")\n    \nelse\n    strategy.cancel(id="LONG")\n    \n\n\n\nif ( shortCond  ) \n\n    strategy.entry("SHORT", strategy.short,stop=close, oca_name="TREND", comment="SHORT")\nelse\n    strategy.cancel(id="SHORT")\n\n\n\n'

class SM3FB58CA66A765C09(PinePortBase, IStrategy):
    source_id = "SM_3fb58ca66a765c09"
    source_file = '趋势消除MACD策略Trendless-MACD-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maperiod': 9, 'fastmacd': 12, 'slowmacd': 26, 'signalmacd': 9, 'monthfrom': 1, 'monthuntil': 12, 'dayfrom': 1, 'dayuntil': 31, 'yearfrom': 2018, 'yearuntil': 2021}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
