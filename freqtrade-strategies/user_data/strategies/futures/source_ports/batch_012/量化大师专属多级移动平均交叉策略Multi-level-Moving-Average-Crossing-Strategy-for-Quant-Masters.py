"""batch_012 port of 量化大师专属多级移动平均交叉策略Multi-level-Moving-Average-Crossing-Strategy-for-Quant-Masters.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-12 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Coinrule\n\n//@version=4\nstrategy(shorttitle=\'Multi Moving Average Crossing\',title=\'Multi Moving Average Crossing (by Coinrule)\', overlay=true, initial_capital=1000,  default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true       // create function "within window of time"\n\n//MA inputs and calculations\ninlong=input(100, title=\'MAlong\')\ninmid=input(50, title=\'MAmid\')\ninshort=input(9, title=\'MAfast\')\n\nMAlong = sma(close, inlong)\nMAshort= sma(close, inshort)\nMAmid= sma(close, inmid)\n\n\n//Entry \nbullish = crossover(MAmid, MAlong)\n\nstrategy.entry(id="long", long = true, when = bullish and window())\n\n//Exit\nbearish = crossunder(MAshort, MAmid)\n\nstrategy.close("long", when = bearish and window())\n\nplot(MAshort, color=color.orange, linewidth=2)\nplot(MAmid, color=color.red, linewidth=2)\nplot(MAlong, color=color.blue, linewidth=2)\n\n'

class SMMultilevelMovingAverageCrossingStrategyforQuantMastersb90dc5(PinePortBase, IStrategy):
    source_id = "SM_b90dc59716a46f1a"
    source_file = '量化大师专属多级移动平均交叉策略Multi-level-Moving-Average-Crossing-Strategy-for-Quant-Masters.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'inlong': 100, 'inmid': 50, 'inshort': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
