"""batch_011 port of 轴心支撑压力反转策略Pivot-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-18 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Pivot Reversal Strategy", overlay=true)\n\n// === BACKTEST RANGE ===\nFromMonth = input(defval = 2, title = "From Month", minval = 1)\nFromDay   = input(defval = 1, title = "From Day", minval = 1)\nFromYear  = input(defval = 2018, title = "From Year", minval = 2014)\nToMonth   = input(defval = 1, title = "To Month", minval = 1)\nToDay     = input(defval = 1, title = "To Day", minval = 1)\nToYear    = input(defval = 9999, title = "To Year", minval = 2014)\n\n\nleftBars = input(4)\nrightBars = input(2)\n\nswh = pivothigh(leftBars, rightBars)\nswl = pivotlow(leftBars, rightBars)\n\nswh_cond = not na(swh)\n\nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\n\nle = false\nle := swh_cond ? true : (le[1] and high > hprice ? false : le[1])\n\nif (le)\n    strategy.entry("PivRevLE", strategy.long, comment="PivRevLE", stop=hprice + syminfo.mintick)\n\nswl_cond = not na(swl)\n\nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\n\n\nse = false\nse := swl_cond ? true : (se[1] and low < lprice ? false : se[1])\n\nif (se)\n    strategy.entry("PivRevSE", strategy.short, comment="PivRevSE", stop=lprice - syminfo.mintick)\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

class SM8A63CD1A0265137E(PinePortBase, IStrategy):
    source_id = "SM_8a63cd1a0265137e"
    source_file = '轴心支撑压力反转策略Pivot-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'FromMonth': 2, 'FromDay': 1, 'FromYear': 2018, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999, 'leftBars': 4, 'rightBars': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
