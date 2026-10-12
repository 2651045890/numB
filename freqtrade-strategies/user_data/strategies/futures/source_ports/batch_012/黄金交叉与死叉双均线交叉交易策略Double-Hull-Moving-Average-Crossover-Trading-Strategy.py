"""batch_012 port of 黄金交叉与死叉双均线交叉交易策略Double-Hull-Moving-Average-Crossover-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-10 00:00:00\nend: 2023-10-10 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title = "Hull MA", shorttitle="Junior2", overlay = true)\n\n//HULL MA 1\n\nlength = input(60, minval=1,title="HULL MA 1 LENGTH")\nsrc = input(close, title="Source")\nhullma = wma(2*wma(src, length/2)-wma(src, length), round(sqrt(length)))\n\nplot(hullma, color=color.green)\n\n//HULLMA 2\n\nalength = input(175, minval=1,title="HULL MA 2 LENGTH")\nasrc = input(close, title="Source")\nahullma = wma(2*wma(asrc, alength/2)-wma(asrc, alength), round(sqrt(alength)))\n\nplot(ahullma, color=color.green)\n\nc1up= crossover(hullma,ahullma)\nc1down= crossunder(hullma,ahullma)\n\nlongCondition = c1up\nif longCondition\n\n    strategy.entry("L", strategy.long)\n\n\nshortCondition = c1down \nif shortCondition\n\n    strategy.entry("S", strategy.short)\n\nplot(close)\n'

class SMDoubleHullMovingAverageCrossoverTradingStrategyf07b01(PinePortBase, IStrategy):
    source_id = "SM_f07b013d8b8ae051"
    source_file = '黄金交叉与死叉双均线交叉交易策略Double-Hull-Moving-Average-Crossover-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'length': 60, 'src': 'close', 'alength': 175, 'asrc': 'close'}
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
