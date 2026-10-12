"""batch_011 port of 结合123反转与平滑RSI的交易策略Combo-Strategy-of-123-Reversal-and-Smoothed-RSI.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-15 00:00:00\nend: 2023-10-15 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 20/07/2021\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This is new version of RSI oscillator indicator, developed by John Ehlers. \n// The main advantage of his way of enhancing the RSI indicator is smoothing \n// with minimum of lag penalty. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\n\nSRSI(Length, TopBand,LowBand) =>\n    pos = 0.0\n    xValue = (close + 2 * close[1] + 2 * close[2] + close[3] ) / 6\n    CU23 = sum(iff(xValue > xValue[1], xValue - xValue[1], 0), Length)\n    CD23 = sum(iff(xValue < xValue[1], xValue[1] - xValue, 0), Length)\n    nRes = iff(CU23 + CD23 != 0, CU23/(CU23 + CD23), 0)\n    pos:= iff(nRes > TopBand, 1,\n    \t   iff(nRes < LowBand, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Smoothed RSI", shorttitle="Combo", overlay = true)\nline1 = input(true, "---- 123 Reversal ----")\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nline2 = input(true, "---- Smoothed RSI ----")\nLengthRSI = input(10, minval=1)\nTopBand = input(0.8, step=0.01)\nLowBand = input(0.2, step=0.01)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposSRSI = SRSI(LengthRSI, TopBand,LowBand )\npos = iff(posReversal123 == 1 and posSRSI == 1 , 1,\n\t   iff(posReversal123 == -1 and posSRSI == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1 ) \n    strategy.entry("Long", strategy.long)\nif (possig == -1 )\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM93560E990EBFEF56(PinePortBase, IStrategy):
    source_id = "SM_93560e990ebfef56"
    source_file = '结合123反转与平滑RSI的交易策略Combo-Strategy-of-123-Reversal-and-Smoothed-RSI.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'line1': True, 'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'line2': True, 'LengthRSI': 10, 'TopBand': 0.8, 'LowBand': 0.2, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
