"""batch_011 port of 趋势跟踪与均值回归双重优化交易系统Double-Seven-Strategy-Trend-Following-and-Mean-Reversion-Dual-Optimization-Trading-SystemDouble-Seven-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EdgeTools\n\n//@version=5\nstrategy("Larry Connors\' Double Seven Strategy", overlay=true)\n\n// 200-day moving average\nma200 = ta.sma(close, 200)\n\n// Conditions for Double Seven Strategy\npriceAboveMa200 = close > ma200\n\n// Find the lowest close over the last 7 days\nlowestClose7Days = ta.lowest(close, 7)\n\n// Find the highest close over the last 7 days\nhighestClose7Days = ta.highest(close, 7)\n\n// Entry and exit rules\nlongCondition = priceAboveMa200 and close <= lowestClose7Days\nexitCondition = close >= highestClose7Days\n\n// Enter long position\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Exit long position\nif (exitCondition)\n    strategy.close("Long")\n    \n// Plot moving averages\nplot(ma200, "200-day MA", color=color.blue)\n'

class SM05E201F448DE714C(PinePortBase, IStrategy):
    source_id = "SM_05e201f448de714c"
    source_file = '趋势跟踪与均值回归双重优化交易系统Double-Seven-Strategy-Trend-Following-and-Mean-Reversion-Dual-Optimization-Trading-SystemDouble-Seven-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
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
