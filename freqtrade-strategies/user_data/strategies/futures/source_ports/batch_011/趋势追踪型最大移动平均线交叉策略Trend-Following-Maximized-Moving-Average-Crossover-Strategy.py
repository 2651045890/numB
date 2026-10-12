"""batch_011 port of 趋势追踪型最大移动平均线交叉策略Trend-Following-Maximized-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-16 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © relevantLeader16058\n\n//@version=4\nstrategy(shorttitle=\'Maximized Moving Average Crossing \',title=\'Maximized Moving Average Crossing (by Coinrule)\', overlay=true, initial_capital=1000,  default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false       // create function "within window of time"\n\n//MA inputs and calculations\ninlong=input(50, title=\'MA long period\')\ninshort=input(9, title=\'MA short period\')\n\nMAlong = sma(close, inlong)\nMAshort= sma(close, inshort)\n\n// RSI inputs and calculations\nlengthRSI = (14)\n\nRSI = rsi(close, lengthRSI)\nRSI_Signal = input(55, title = \'RSI Trigger\', minval=1)\n\n//Entry and Exit\nbullish = crossover(MAshort, MAlong)\nbearish = crossunder(MAshort, MAlong)\n\nstrategy.entry(id="long", long = true, when = bullish and RSI > RSI_Signal and window())\nstrategy.close(id="long", when = bearish and window())\n\n \nplot(MAshort, color=color.purple, linewidth=2)\nplot(MAlong, color=color.red, linewidth=2)'

class SM68851142C9AA1D6B(PinePortBase, IStrategy):
    source_id = "SM_68851142c9aa1d6b"
    source_file = '趋势追踪型最大移动平均线交叉策略Trend-Following-Maximized-Moving-Average-Crossover-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'inlong': 50, 'inshort': 9, 'RSI_Signal': 55}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
