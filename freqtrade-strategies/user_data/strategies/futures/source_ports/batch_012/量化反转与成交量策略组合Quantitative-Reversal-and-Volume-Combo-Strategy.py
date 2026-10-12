"""batch_012 port of 量化反转与成交量策略组合Quantitative-Reversal-and-Volume-Combo-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-13 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 21/10/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This is another version of FVE indicator that we have posted earlier \n// in this forum.\n// This version has an important enhancement to the previous one that`s \n// especially useful with intraday minute charts.\n// Due to the volatility had not been taken into account to avoid the extra \n// complication in the formula, the previous formula has some drawbacks:\n// The main drawback is that the constant cutoff coefficient will overestimate \n// price changes in minute charts and underestimate corresponding changes in \n// weekly or monthly charts.\n// And now the indicator uses adaptive cutoff coefficient which will adjust to \n// all time frames automatically.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\n\nFVI(Samples,Perma,Cintra,Cinter) =>\n    pos = 0\n    xhl2 = hl2\n    xhlc3 = hlc3\n    xClose = close\n    xIntra = log(high) - log(low)\n    xInter = log(xhlc3) - log(xhlc3[1])\n    xStDevIntra = stdev(sma(xIntra, Samples) , Samples)\n    xStDevInter = stdev(sma(xInter, Samples) , Samples)\n    xVolume = volume\n    TP = xhlc3\n    TP1 = xhlc3[1]\n    Intra = xIntra\n    Vintra = xStDevIntra\n    Inter = xInter\n    Vinter = xStDevInter\n    CutOff = Cintra * Vintra + Cinter * Vinter\n    MF = xClose - xhl2 + TP - TP1\n    FveFactor =  iff(MF > CutOff * xClose, 1, \n                  iff(MF < -1 * CutOff * xClose, -1,  0))\n    xVolumePlusMinus = xVolume * FveFactor\n    Fvesum = sum(xVolumePlusMinus, Samples)\n    VolSum = sum(xVolume, Samples)\n    xFVE = (Fvesum / VolSum) * 100\n    xEMAFVE = ema(xFVE, Perma)\n    pos :=iff(xFVE > xEMAFVE, 1,\n    \t   iff(xFVE < xEMAFVE, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Volatility Finite Volume Elements", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nSamples = input(22, minval=1)\nPerma = input(40, minval=1)\nCintra = input(0.1)\nCinter = input(0.1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposFVI = FVI(Samples,Perma,Cintra,Cinter)\npos = iff(posReversal123 == 1 and posFVI == 1 , 1,\n\t   iff(posReversal123 == -1 and posFVI == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMQuantitativeReversalandVolumeComboStrategyfd6d3f(PinePortBase, IStrategy):
    source_id = "SM_fd6d3f47583fd609"
    source_file = '量化反转与成交量策略组合Quantitative-Reversal-and-Volume-Combo-Strategy.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'Samples': 22, 'Perma': 40, 'Cintra': 0.1, 'Cinter': 0.1, 'reverse': False}
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
