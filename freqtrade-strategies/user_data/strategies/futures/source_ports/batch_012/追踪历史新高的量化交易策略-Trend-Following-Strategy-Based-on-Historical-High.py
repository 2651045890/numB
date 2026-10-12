"""batch_012 port of 追踪历史新高的量化交易策略-Trend-Following-Strategy-Based-on-Historical-High.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-21 00:00:00\nend: 2024-01-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("All-time-high", "ATH", overlay=true, initial_capital=10000, default_qty_value=100, default_qty_type=strategy.percent_of_equity, pyramiding=1, commission_type=strategy.commission.cash_per_contract, commission_value=0.000)\n\n// input\nAthlw = input(title="All-time-high line widths", type=input.integer, defval=4, minval=0, maxval=4)\nAthlc = input(title="All-time-high line color", type=input.color, defval=color.new(color.fuchsia,50))\nyears = input(title="Years back to search for an ATH", type=input.integer, defval=6,minval=0, maxval=100)\n\nvar float   highestHigh = 0\n// var line    allTimeHigh = line.new(na, na, na, na, extend=extend.both, color=Athlc, width=Athlw)\n\nif high > highestHigh\n    highestHigh := high\n\n// if barstate.islast\n//     line.set_xy1(allTimeHigh, bar_index-1, highestHigh)\n//     line.set_xy2(allTimeHigh, bar_index,   highestHigh)\n\nplot(highestHigh)\nbuyzone=highestHigh*0.9\nbuyzone2=highestHigh*0.8\nbuyzone3=highestHigh*0.7\nsellzone=highestHigh*0.99\n\nplot(buyzone, color=color.red)\nplot(buyzone2, color=color.white)\nplot(buyzone3, color=color.green)\n\nbegin = timestamp(2011,1,1,0,0)\nend = timestamp(2022,4,19,0,0)\n\nlongCondition = close<buyzone2\nif (longCondition)\n    strategy.entry("Buy", strategy.long)\ncloseCondition = close>sellzone\nif (closeCondition)\n    strategy.close("Buy", strategy.long)\n\n'

class SMTrendFollowingStrategyBasedonHistoricalHigh3853eb(PinePortBase, IStrategy):
    source_id = "SM_3853ebfca8628e7a"
    source_file = '追踪历史新高的量化交易策略-Trend-Following-Strategy-Based-on-Historical-High.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'Athlw': 4, 'Athlc': 'color.new(color.fuchsia', 'years': 6}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 1
    source_initial_capital = 10000
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
