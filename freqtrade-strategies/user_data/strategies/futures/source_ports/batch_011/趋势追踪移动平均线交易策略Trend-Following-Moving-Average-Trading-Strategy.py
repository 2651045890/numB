"""batch_011 port of 趋势追踪移动平均线交易策略Trend-Following-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-05 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("I Like Winners And Love Loosers!", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nhighest_length = input(200, type=input.integer, minval=1, title="Highest Length")\nhighest_average = input(10, type=input.integer, minval=1, title="Highest Average Length")\n\nlowest_length = input(200, type=input.integer, minval=1, title="Lowest Length")\nlowest_average = input(10, type=input.integer, minval=1, title="Lowest Average Length")\n\natr_length = input(14, type=input.integer, minval=1, title="ATR Length")\natr_multiplier = input(2, type=input.integer, minval=1, title="ATR Multiplier")\na = atr(atr_length) * atr_multiplier\n\nh1 = sma(highest(high, highest_length), highest_average)\nl1 = h1 - a\n\nh2 = sma(lowest(low, lowest_length), lowest_average)\nl2 = h2 + a\n\nbuy1_signal = crossover(close, h1)\nsell1_signal = crossunder(close, l1)\nstrategy.entry("Buy", strategy.long, when=buy1_signal)\nstrategy.close("Buy", when=sell1_signal)\n\nbuy2_signal = crossunder(close, h2)\nsell2_signal = crossover(close, l2)\nstrategy.entry("Sell", strategy.short, when=buy2_signal)\nstrategy.close("Sell", when=sell2_signal)\n\ny1 = plot(h1, title="H1", color=color.green, transp=50, linewidth=2)\ny2 = plot(l1, title="L1", color=color.red, transp=50, linewidth=2)\ny3 = plot(h2, title="H2", color=color.green, transp=50, linewidth=2)\ny4 = plot(l2, title="L2", color=color.red, transp=50, linewidth=2)\n\nfill(y1,y2,color=color.green)\nfill(y3,y4,color=color.red)\n'

class SM0EC67A3712A4B6D6(PinePortBase, IStrategy):
    source_id = "SM_0ec67a3712a4b6d6"
    source_file = '趋势追踪移动平均线交易策略Trend-Following-Moving-Average-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'highest_length': 200, 'highest_average': 10, 'lowest_length': 200, 'lowest_average': 10, 'atr_length': 14, 'atr_multiplier': 2}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
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
