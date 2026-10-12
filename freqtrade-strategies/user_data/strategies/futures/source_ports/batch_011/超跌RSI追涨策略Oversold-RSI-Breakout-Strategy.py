"""batch_011 port of 超跌RSI追涨策略Oversold-RSI-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-18 00:00:00\nend: 2023-09-25 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © brodieCoinrule\n\n//@version=4\nstrategy(shorttitle=\'Oversold RSI with tight SL\',title=\'Oversold RSI with tight SL Strategy (by Coinrule)\', overlay=true, initial_capital = 1000, process_orders_on_close=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 50, commission_type=strategy.commission.percent, commission_value=0.1)\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true       // create function "within window of time"\n\nperc_change(lkb) =>\n    overall_change = ((close[0] - close[lkb]) / close[lkb]) * 100\n\n\n\n// RSI inputs and calculations\nlengthRSI = 14\nRSI = rsi(close, lengthRSI)\noversold= input(30)\n\n\n//Entry \nstrategy.entry(id="long", long = true, when = RSI< oversold and window())\n\n//Exit\nStop_loss= ((input (1))/100)\nTake_profit= ((input (7)/100))\n\nlongStopPrice  = strategy.position_avg_price * (1 - Stop_loss)\nlongTakeProfit = strategy.position_avg_price * (1 + Take_profit)\n\nstrategy.close("long", when = close < longStopPrice or close > longTakeProfit and window())\n\n'

class SM03E1AA9ED4D9E9EB(PinePortBase, IStrategy):
    source_id = "SM_03e1aa9ed4d9e9eb"
    source_file = '超跌RSI追涨策略Oversold-RSI-Breakout-Strategy.md'
    timeframe = '15m'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'oversold': 30}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 50
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
