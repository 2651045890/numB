"""batch_012 port of 高点低点突破趋势追踪策略High-Low-Breakout-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-13 00:00:00\nend: 2023-09-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=1\nstrategy(title="HIGHER HIGH LOWER LOW STRATEGY", shorttitle="HH LL STRATEGY", overlay=true, calc_on_order_fills=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, currency="USD", default_qty_value=100)\n\n////\n\n\n//Higher High or Lower Low Entry Inputs\nprice = input(hlc3)\nLookBack = input(22)\nHighest = highest(LookBack)\nLowest = lowest(LookBack)\n\nlong = price > Highest[1] \nshort = price < Lowest[1]\n\n\n\n\n//Divergence Check Inputs\nlength = input(14)\nHigh_Guard = highest(length)\nLow_Guard = lowest(length)\n\nlength2 = input(2)\n\nlong1 = long == 1 and Highest[1] > High_Guard[length2]\nshort1 = short == 1 and Lowest[1] < Low_Guard[length2]\n\n\nplot(long and long[1], color=green, style=line)\nplot(short and short[1], color=red, style=line)\n\nstrategy.entry("Long", strategy.long, when=long1)\nstrategy.entry("Short", strategy.short, when=short1)\n\n'

class SMHighLowBreakoutTrendFollowingStrategyefcf8c(PinePortBase, IStrategy):
    source_id = "SM_efcf8c42ab44014b"
    source_file = '高点低点突破趋势追踪策略High-Low-Breakout-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'price': 'hlc3', 'LookBack': 22, 'length': 14, 'length2': 2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
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
