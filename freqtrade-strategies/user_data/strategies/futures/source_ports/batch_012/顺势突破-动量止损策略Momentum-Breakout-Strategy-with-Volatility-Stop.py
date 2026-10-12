"""batch_012 port of 顺势突破-动量止损策略Momentum-Breakout-Strategy-with-Volatility-Stop.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-11 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n//@version=4\nstrategy(shorttitle=\'Volatility Stop Strategy\',title=\'Volatility Stop Strategy (by Coinrule)\', overlay=true, initial_capital = 100, process_orders_on_close=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, commission_type=strategy.commission.percent, commission_value=0.1)\n\n// Works better on 3h, 1h, 2h, 4h\n// Best time frame 2H\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2021, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false       // create function "within window of time"\n\nlength = input(20, "Length", minval = 2)\nsrc = input(close, "Source")\nfactor = input(3.0, "vStop Multiplier", minval = 0.25, step = 0.25)\nvolStop(src, atrlen, atrfactor) =>\n    var max     = src\n    var min     = src\n    var uptrend = true\n    var stop    = 0.0\n    atrM        = nz(atr(atrlen) * atrfactor, tr)\n    max         := max(max, src)\n    min         := min(min, src)\n    stop        := nz(uptrend ? max(stop, max - atrM) : min(stop, min + atrM), src)\n    uptrend     := src - stop >= 0.0\n    if uptrend != nz(uptrend[1], true)\n        max    := src\n        min    := src\n        stop   := uptrend ? max - atrM : min + atrM\n    [stop, uptrend]\n\n[vStop, uptrend] = volStop(src, length, factor)\n\n\n//Entry \n\n\nstrategy.entry(id="long", long = true, when = crossover(close, vStop) and window())\n\n//Exit\nstrategy.close("long", when = crossunder(close, vStop))\n\nplot(vStop,"Vstop", color.black, linewidth=2)\n\n'

class SMMomentumBreakoutStrategywithVolatilityStopd8ccd9(PinePortBase, IStrategy):
    source_id = "SM_d8ccd9b84e3bf486"
    source_file = '顺势突破-动量止损策略Momentum-Breakout-Strategy-with-Volatility-Stop.md'
    timeframe = '3m'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2021, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'length': 20, 'src': 'close', 'factor': 3.0}
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
