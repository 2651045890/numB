"""batch_012 port of 顺势而为RSI策略Go-With-The-Trend-RSI-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-30 00:00:00\nend: 2023-10-07 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Pivot Point Reversal + RSI Strategy", shorttitle = \'PP + RSI Strategy\', overlay=true)\n\n////////////\n// Inputs //\n\nleftBars   = input(3,  title = \'PP - Left Bars\')\nrightBars  = input(3,  title = \'PP - Right Bars\')\nrsi_length = input(14, title = "RSI - Length")\nrsi_long   = input(70, title = "RSI - Overbought level")\nrsi_short  = input(30, title = "RSI - Overold level")\n\n//////////////////\n// Calculations //\n\n// Pivot Points\nswh = pivothigh(leftBars, rightBars)\nswl = pivotlow(leftBars, rightBars)\n\n// Pivot High \nswh_cond = not na(swh)\n \nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\n \nle = false\nle := swh_cond ? true : (le[1] and high > hprice ? false : le[1])\n\n// Pivot Low \nswl_cond = not na(swl)\n \nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\n \nse = false\nse := swl_cond ? true : (se[1] and low < lprice ? false : se[1])\n\n// RSI \nrsi = rsi(close, 14)\n\n//////////////\n// STRATEGY //\n\nif (le and rsi[rightBars] < rsi_long )\n    strategy.entry("PivRevLE", strategy.long,  comment = "PivRSI Long",  stop = hprice + syminfo.mintick)\n \nif (se and rsi[rightBars] > rsi_short)\n    strategy.entry("PivRevSE", strategy.short, comment = "PivRSI Short", stop = lprice - syminfo.mintick)\n \n'

class SMRSIGoWithTheTrendRSIStrategy6b5bf3(PinePortBase, IStrategy):
    source_id = "SM_6b5bf3aa35580aa3"
    source_file = '顺势而为RSI策略Go-With-The-Trend-RSI-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'leftBars': 3, 'rightBars': 3, 'rsi_length': 14, 'rsi_long': 70, 'rsi_short': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
