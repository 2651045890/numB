"""batch_012 port of 量化双击利反转策略Quant-Trading-Double-Click-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-22 00:00:00\nend: 2023-11-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 23/12/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// The Klinger Oscillator (KO) was developed by Stephen J. Klinger. Learning \n// from prior research on volume by such well-known technicians as Joseph Granville, \n// Larry Williams, and Marc Chaikin, Mr. Klinger set out to develop a volume-based \n// indicator to help in both short- and long-term analysis.\n// The KO was developed with two seemingly opposite goals in mind: to be sensitive \n// enough to signal short-term tops and bottoms, yet accurate enough to reflect the \n// long-term flow of money into and out of a security.\n// The KO is based on the following tenets:\n// Price range (i.e. High - Low) is a measure of movement and volume is the force behind \n// the movement. The sum of High + Low + Close defines a trend. Accumulation occurs when \n// today\'s sum is greater than the previous day\'s. Conversely, distribution occurs when \n// today\'s sum is less than the previous day\'s. When the sums are equal, the existing trend \n// is maintained.\n// Volume produces continuous intra-day changes in price reflecting buying and selling pressure. \n// The KO quantifies the difference between the number of shares being accumulated and distributed \n// each day as "volume force". A strong, rising volume force should accompany an uptrend and then \n// gradually contract over time during the latter stages of the uptrend and the early stages of \n// the following downtrend. This should be followed by a rising volume force reflecting some \n// accumulation before a bottom develops.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nKVO(TrigLen,FastX,SlowX) =>\n    pos = 0.0\n    xTrend = iff(hlc3 > hlc3[1], volume * 100, -volume * 100)\n    xFast = ema(xTrend, FastX)\n    xSlow = ema(xTrend, SlowX)\n    xKVO = xFast - xSlow\n    xTrigger = ema(xKVO, TrigLen)\n    pos := iff(xKVO > xTrigger, 1,\n    \t     iff(xKVO < xTrigger, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Klinger Volume Oscillator", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nTrigLen = input(13, minval=1)\nFastX = input(34, minval=1)\nSlowX = input(55, minval=1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposKVO = KVO(TrigLen,FastX,SlowX)\npos = iff(posReversal123 == 1 and posKVO == 1 , 1,\n\t   iff(posReversal123 == -1 and posKVO == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMQuantTradingDoubleClickReversalStrategyc4fb91(PinePortBase, IStrategy):
    source_id = "SM_c4fb910b9a9f49f5"
    source_file = '量化双击利反转策略Quant-Trading-Double-Click-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'TrigLen': 13, 'FastX': 34, 'SlowX': 55, 'reverse': False}
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
