"""batch_011 port of 移动平均量价趋势攻击震荡策略Momentum-Trend-Following-Oscillation-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-16 00:00:00\nend: 2023-11-15 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 29/04/2019\n// This is combo strategies for get \n// a cumulative signal. Result signal will return 1 if two strategies \n// is long, -1 if all strategies is short and 0 if signals of strategies is not equal.\n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Secon strategy\n// The Average Directional Movement Index Rating (ADXR) measures the strength \n// of the Average Directional Movement Index (ADX). It\'s calculated by taking \n// the average of the current ADX and the ADX from one time period before \n// (time periods can vary, but the most typical period used is 14 days).\n// Like the ADX, the ADXR ranges from values of 0 to 100 and reflects strengthening \n// and weakening trends. However, because it represents an average of ADX, values \n// don\'t fluctuate as dramatically and some analysts believe the indicator helps \n// better display trends in volatile markets.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nfADX(Len) =>\n    up = change(high)\n    down = -change(low)\n    trur = rma(tr, Len)\n    plus = fixnan(100 * rma(up > down and up > 0 ? up : 0, Len) / trur)\n    minus = fixnan(100 * rma(down > up and down > 0 ? down : 0, Len) / trur)\n    sum = plus + minus \n    100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), Len)\n\nADXR(LengthADX, LengthADXR, Signal1, Signal2) =>\n    xADX = fADX(LengthADX)\n    xADXR = (xADX + xADX[LengthADXR]) / 2\n    pos = 0.0\n    pos := iff(xADXR < Signal1, 1,\n           iff(xADXR > Signal2, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal and Average Directional Movement Index Rating", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\nLengthADX = input(title="Length ADX", defval=14)\nLengthADXR = input(title="Length ADXR", defval=14)\nSignal1 = input(13, step=0.01)\nSignal2 = input(45, step=0.01)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposADXR = ADXR(LengthADX, LengthADXR, Signal1, Signal2 )\npos = iff(posReversal123 == 1 and posADXR == 1 , 1,\n\t   iff(posReversal123 == -1 and posADXR == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? red: possig == 1 ? green : blue ) '

class SM2E7B9D6F5BB26D06(PinePortBase, IStrategy):
    source_id = "SM_2e7b9d6f5bb26d06"
    source_file = '移动平均量价趋势攻击震荡策略Momentum-Trend-Following-Oscillation-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'LengthADX': 14, 'LengthADXR': 14, 'Signal1': 13, 'Signal2': 45, 'reverse': False}
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
