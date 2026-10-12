"""batch_012 port of 重要支点反转策略Significant-Pivot-Points-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("QuantNomad - Significant Pivot Reversal Strategy", shorttitle = "SPPS", overlay=true)\n\n// Inputs \nleftBars   = input(4,   title = \'PP Left Bars\')\nrightBars  = input(2,   title = \'PP Right Bars\')\natr_length = input(14,  title = \'ATR Length\')\natr_mult   = input(0.1, title = \'ATR Mult\')\n\n// Pivot High Significant Function\npivotHighSig(left, right) =>\n    pp_ok = true\n    atr   = atr(atr_length)\n    \n    for i = 1 to left\n        if (high[right] < high[right+i] + atr * atr_mult)\n            pp_ok := false\n    for i = 0 to right-1\n        if (high[right] < high[i] + atr * atr_mult)\n            pp_ok := false\n    \n    pp_ok ? high[right] : na\n\n// Pivot Low Significant Function\npivotLowSig(left, right) =>\n    pp_ok = true\n    atr   = atr(atr_length)\n    \n    for i = 1 to left\n        if (low[right] > low[right+i] - atr * atr_mult)\n            pp_ok := false\n    for i = 0 to right-1\n        if (low[right] > low[i] - atr * atr_mult)\n            pp_ok := false\n    \n    pp_ok ? low[right] : na\n\n\nswh = pivotHighSig(leftBars, rightBars)\nswl = pivotLowSig (leftBars, rightBars)\n\nswh_cond = not na(swh)\n\nhprice = 0.0\nhprice := swh_cond ? swh : hprice[1]\n\nle = false\nle := swh_cond ? true : (le[1] and high > hprice ? false : le[1])\n\nif (le)\n    strategy.entry("PivRevLE", strategy.long, comment="PivRevLE", stop=hprice + syminfo.mintick)\n\nswl_cond = not na(swl)\n\nlprice = 0.0\nlprice := swl_cond ? swl : lprice[1]\n\n\nse = false\nse := swl_cond ? true : (se[1] and low < lprice ? false : se[1])\n\nif (se)\n    strategy.entry("PivRevSE", strategy.short, comment="PivRevSE", stop=lprice - syminfo.mintick)\n'

class SMSignificantPivotPointsReversalStrategy166715(PinePortBase, IStrategy):
    source_id = "SM_166715cd809e087c"
    source_file = '重要支点反转策略Significant-Pivot-Points-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'leftBars': 4, 'rightBars': 2, 'atr_length': 14, 'atr_mult': 0.1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
