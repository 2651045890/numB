"""batch_011 port of 简易枢轴反转量化交易策略Simple-Pivot-Reversal-Algorithmic-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Pivot Reversal Strategy - FIGS & DATES 2.0", overlay=true, pyramiding=0, initial_capital=10000, currency="USD", default_qty_type=strategy.percent_of_equity, default_qty_value=100.0, commission_value=0.075)\n\nleftBars = input(4)\nrightBars = input(2)\n\n// backtesting date range\nfrom_day = input(defval=1, title="From Day", minval=1, maxval=31)\nfrom_month = input(defval=1, title="From Month", minval=1, maxval=12)\nfrom_year = input(defval=2018, title="From Year", minval=1900)\n\nto_day = input(defval=1, title="To Day", minval=1, maxval=31)\nto_month = input(defval=1, title="To Month", minval=1, maxval=12)\nto_year = input(defval=9999, title="To Year", minval=1900)\n\ntime_cond = true\n\nswh = pivothigh(leftBars, rightBars)\nswl = pivotlow(leftBars, rightBars)\n\nmiddle = (swh+swl)/2\n\nswh_cond = not na(swh)\n\n\n\nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\n\nle = false\nle := swh_cond ? true : le[1] and high > hprice ? false : le[1]\n\nif le and time_cond\n    strategy.entry("LONG", strategy.long, comment="LONG", stop=hprice + syminfo.mintick)\n\nswl_cond = not na(swl)\n\nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\n\n\nse = false\nse := swl_cond ? true : se[1] and low < lprice ? false : se[1]\n\nif se and time_cond\n    strategy.entry("SHORT", strategy.short, comment="SHORT", stop=lprice - syminfo.mintick)\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)\n'

class SMB87FDA4AEDE94EA3(PinePortBase, IStrategy):
    source_id = "SM_b87fda4aede94ea3"
    source_file = '简易枢轴反转量化交易策略Simple-Pivot-Reversal-Algorithmic-Trading-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'leftBars': 4, 'rightBars': 2, 'from_day': 1, 'from_month': 1, 'from_year': 2018, 'to_day': 1, 'to_month': 1, 'to_year': 9999}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_commission_percent = 0.075
    source_pyramiding = 0
    source_initial_capital = 10000
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
