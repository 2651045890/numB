"""batch_011 port of 移动平均线交叉策略Exponential-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-05 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © rt-maax\n\n//@version=5\n\nstrategy(title = "rt maax EMA cross strategy", shorttitle = "rt maax ema ", overlay = true, precision = 8, max_bars_back = 200, pyramiding = 0, initial_capital = 100000, \n     currency = currency.USD, default_qty_type = strategy.cash, default_qty_value = 100000, commission_type = "percent", commission_value = 0.27)\nfastema = ta.ema (close , 50)\nfema=ta.ema(close,20)\nslowema= ta.ema(close,200)\nprice = close\n\n// === INPUT BACKTEST RANGE ===\nfromMonth = input.int(defval = 1,    title = "From Month",  minval = 1, maxval = 12)\nfromDay   = input.int(defval = 1,    title = "From Day",    minval = 1, maxval = 31)\nfromYear  = input.int(defval = 2021, title = "From Year",   minval = 1970)\nthruMonth = input.int(defval = 10,    title = "Thru Month",  minval = 1, maxval = 12)\nthruDay   = input.int(defval = 25,    title = "Thru Day",    minval = 1, maxval = 31)\nthruYear  = input.int(defval = 2112, title = "Thru Year",   minval = 1970)\n\n// === INPUT SHOW PLOT ===\nshowDate  = input(defval = true, title = "Show Date Range")\n\n// === FUNCTION EXAMPLE ===\n\n\n\nlongCondition1= ta.crossover (fema , fastema) \nlongcondition2= fema> slowema\nlongcondition3=fastema>slowema\n\n\nif (longCondition1 and longcondition2 and longcondition3 )\n    stoploss=low*0.97\n    takeprofit=high*1.12\n    strategy.entry("Long Entry", strategy.long)\n    strategy.exit ("exit","long",stop=stoploss,limit=takeprofit)\n   \n\n\nshortCondition1 = ta.crossunder (fema , fastema )\nshortcondition2= fastema< slowema\nshortcondition3= fema< slowema\n\nif (shortCondition1 and shortcondition2 and shortcondition3 )\n    stoploss=low*0.97 \n    takeprofit=high*1.5\n    strategy.entry("Short Entry", strategy.short)\n    strategy.exit("exit","short",stop=stoploss,limit=takeprofit)\n\n\n\n\n'

class SM3A9ECCD64A03201A(PinePortBase, IStrategy):
    source_id = "SM_3a9eccd64a03201a"
    source_file = '移动平均线交叉策略Exponential-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fromMonth': 1, 'fromDay': 1, 'fromYear': 2021, 'thruMonth': 10, 'thruDay': 25, 'thruYear': 2112, 'showDate': True}
    source_qty_type = 'cash'
    source_qty_value = 100000
    source_commission_percent = 0.27
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
