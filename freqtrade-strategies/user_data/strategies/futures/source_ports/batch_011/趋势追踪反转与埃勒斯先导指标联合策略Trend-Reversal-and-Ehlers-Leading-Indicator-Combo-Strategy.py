"""batch_011 port of 趋势追踪反转与埃勒斯先导指标联合策略Trend-Reversal-and-Ehlers-Leading-Indicator-Combo-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-07 00:00:00\nend: 2023-11-06 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 26/11/2019\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This Indicator plots a single\n// Daily DSP (Detrended Synthetic Price) and a Daily ELI (Ehlers Leading\n// Indicator) using intraday data.\n// Detrended Synthetic Price is a function that is in phase with the dominant\n// cycle of real price data. This one is computed by subtracting a 3 pole Butterworth\n// filter from a 2 Pole Butterworth filter. Ehlers Leading Indicator gives an advanced\n// indication of a cyclic turning point. It is computed by subtracting the simple\n// moving average of the detrended synthetic price from the detrended synthetic price.\n// Buy and Sell signals arise when the ELI indicator crosses over or under the detrended\n// synthetic price.\n// See "MESA and Trading Market Cycles" by John Ehlers pages 64 - 70. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nD_ELI(Length) =>\n    pos = 0.0\n    xHL2 = security(syminfo.tickerid, \'D\', hl2)\n    xEMA1 = ema(xHL2, Length)\n    xEMA2 = ema(xHL2, 2 * Length)\n    xEMA1_EMA2 = xEMA1 - xEMA2\n    xResultEMA = ema(xEMA1_EMA2, Length)\n    nRes = xEMA1_EMA2 - xResultEMA\n    pos:= iff(nRes > 0, 1,\n\t       iff(nRes < 0, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & D_ELI (Ehlers Leading Indicator)", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nLengthELI = input(7, minval=1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposD_ELI = D_ELI(LengthELI)\npos = iff(posReversal123 == 1 and posD_ELI == 1 , 1,\n\t   iff(posReversal123 == -1 and posD_ELI == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM30422F9BA5C5D556(PinePortBase, IStrategy):
    source_id = "SM_30422f9ba5c5d556"
    source_file = '趋势追踪反转与埃勒斯先导指标联合策略Trend-Reversal-and-Ehlers-Leading-Indicator-Combo-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'LengthELI': 7, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
