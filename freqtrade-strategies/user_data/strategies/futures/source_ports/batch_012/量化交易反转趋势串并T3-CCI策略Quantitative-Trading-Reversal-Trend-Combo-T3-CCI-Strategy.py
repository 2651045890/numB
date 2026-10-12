"""batch_012 port of 量化交易反转趋势串并T3-CCI策略Quantitative-Trading-Reversal-Trend-Combo-T3-CCI-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-28 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 23/10/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This simple indicator gives you a lot of useful information - when to enter, when to exit\n// and how to reduce risks by entering a trade on a double confirmed signal.\n// You can use in the xPrice any series: Open, High, Low, Close, HL2, HLC3, OHLC4 and ect...\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\n    \nT3_CCI(CCI_Period,T3_Period,b) =>\n    pos = 0.0\n    e1 = 0.0\n    e2 = 0.0\n    e3 = 0.0\n    e4 = 0.0\n    e5 = 0.0\n    e6 = 0.0\n    xPrice = close\n    b2 = b*b\n    b3 = b2*b\n    c1 = -b3\n    c2 = (3*(b2 + b3))\n    c3 = -3*(2*b2 + b + b3)\n    c4 = (1 + 3*b + b3 + 3*b2)\n    nn = iff(T3_Period < 1, 1, T3_Period)\n    nr = 1 + 0.5*(nn - 1)\n    w1 = 2 / (nr + 1)\n    w2 = 1 - w1    \n    xcci = cci(xPrice, CCI_Period)\n    e1 := w1*xcci + w2*nz(e1[1])\n    e2 := w1*e1 + w2*nz(e2[1])\n    e3 := w1*e2 + w2*nz(e3[1])\n    e4 := w1*e3 + w2*nz(e4[1])\n    e5 := w1*e4 + w2*nz(e5[1])\n    e6 := w1*e5 + w2*nz(e6[1])\n    xccir = c1*e6 + c2*e5 + c3*e4 + c4*e3  \n    pos:= iff(xccir > 0, 1,\n           iff(xccir < 0, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & FX Sniper:  T3-CCI", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nCCI_Period = input(14, minval=1)\nT3_Period = input(5, minval=1)\nb = input(0.618)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposT3_CCI = T3_CCI(CCI_Period,T3_Period,b)\npos = iff(posReversal123 == 1 and posT3_CCI == 1 , 1,\n\t   iff(posReversal123 == -1 and posT3_CCI == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMT3CCIQuantitativeTradingReversalTrendComboT3CCIStrategy50981f(PinePortBase, IStrategy):
    source_id = "SM_50981fc43699c9bb"
    source_file = '量化交易反转趋势串并T3-CCI策略Quantitative-Trading-Reversal-Trend-Combo-T3-CCI-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'CCI_Period': 14, 'T3_Period': 5, 'b': 0.618, 'reverse': False}
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
