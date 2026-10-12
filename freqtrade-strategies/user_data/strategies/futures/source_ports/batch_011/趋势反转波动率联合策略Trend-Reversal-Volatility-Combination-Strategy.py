"""batch_011 port of 趋势反转波动率联合策略Trend-Reversal-Volatility-Combination-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-23 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 31/07/2021\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This indicator used to calculate the statistical volatility, sometime \n// called historical volatility, based on the Extreme Value Method.\n// Please use this link to get more information about Volatility.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\n\nSV(Length,TopBand,LowBand) =>\n    pos = 0.0\n    xMaxC = highest(close, Length)\n    xMaxH = highest(high, Length)\n    xMinC = lowest(close, Length)\n    xMinL = lowest(low, Length)\n    SqrTime = sqrt(253 / Length)\n    Vol = ((0.6 * log(xMaxC / xMinC) * SqrTime) + (0.6 * log(xMaxH / xMinL) * SqrTime)) * 0.5\n    nRes = iff(Vol < 0,  0, iff(Vol > 2.99, 2.99, Vol))\n    pos := iff(nRes > TopBand, 1,\n    \t     iff(nRes < LowBand, -1, nz(pos[1], 0)))\n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Statistical Volatility", shorttitle="Combo", overlay = true)\nline1 = input(true, "---- 123 Reversal ----")\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nline2 = input(true, "---- Statistical Volatility ----")\nLengthSV = input(30, minval=1)\nTopBand = input(0.005, step=0.001)\nLowBand = input(0.0016, step=0.001)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposSV = SV(LengthSV,TopBand,LowBand)\npos = iff(posReversal123 == 1 and posSV == 1 , 1,\n\t   iff(posReversal123 == -1 and posSV == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1 ) \n    strategy.entry("Long", strategy.long)\nif (possig == -1 )\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM1EB481AC4351B255(PinePortBase, IStrategy):
    source_id = "SM_1eb481ac4351b255"
    source_file = '趋势反转波动率联合策略Trend-Reversal-Volatility-Combination-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'line1': True, 'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'line2': True, 'LengthSV': 30, 'TopBand': 0.005, 'LowBand': 0.0016, 'reverse': False}
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
