"""batch_011 port of 简单低买高卖策略Simple-Buy-Low-Sell-High-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=3\nstrategy(shorttitle=\'Buy the Dips\',title=\'Buy the Dips (by Coinrule)\', overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,  title = "From Month")     \nfromDay   = input(defval = 10,    title = "From Day")       \nfromYear  = input(defval = 2020, title = "From Year")       \nthruMonth = input(defval = 1,    title = "Thru Month")     \nthruDay   = input(defval = 1,    title = "Thru Day")     \nthruYear  = input(defval = 2112, title = "Thru Year")       \n\nshowDate  = input(defval = true, title = "Show Date Range")\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false       // create function "within window of time"\n\ninp_lkb = input(1, title=\'Lookback Period\')\n \nperc_change(lkb) =>\n    overall_change = ((close[0] - close[lkb]) / close[lkb]) * 100\n\n// Call the function    \noverall = perc_change(inp_lkb)\n\n//Entry\n\ndip= -(input(2))\n\nstrategy.entry(id="long", long = true, when = overall< dip and window()) \n\n//Exit\nStop_loss= ((input (2))/100)\nTake_profit= ((input (2))/100)\n\nlongStopPrice  = strategy.position_avg_price * (1 - Stop_loss)\nlongTakeProfit = strategy.position_avg_price * (1 + Take_profit)\n\nstrategy.close("long", when = close < longStopPrice or close > longTakeProfit and window())\n'

class SM51F2DACF4432177E(PinePortBase, IStrategy):
    source_id = "SM_51f2dacf4432177e"
    source_file = '简单低买高卖策略Simple-Buy-Low-Sell-High-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 10, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'inp_lkb': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30
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
