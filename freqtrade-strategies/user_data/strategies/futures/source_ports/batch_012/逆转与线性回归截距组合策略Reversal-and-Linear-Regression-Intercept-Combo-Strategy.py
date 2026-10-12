"""batch_012 port of 逆转与线性回归截距组合策略Reversal-and-Linear-Regression-Intercept-Combo-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-18 00:00:00\nend: 2023-09-19 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 25/01/2021\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// Linear Regression Intercept is one of the indicators calculated by using the \n// Linear Regression technique. Linear regression indicates the value of the Y \n// (generally the price) when the value of X (the time series) is 0. Linear \n// Regression Intercept is used along with the Linear Regression Slope to create \n// the Linear Regression Line. The Linear Regression Intercept along with the Slope \n// creates the Regression line.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nLRI(Length,xSeria) =>\n    pos = 0.0\n    xX = Length * (Length - 1) * 0.5\n    xDivisor = xX * xX - Length * Length * (Length - 1) * (2 * Length - 1) / 6\n    xXY = 0.0\n    for i = 0 to Length-1\n    \txXY := xXY + (i * xSeria[i])\n    xSlope = (Length * xXY - xX * sum(xSeria, Length)) / xDivisor\n    xLRI = (sum(xSeria, Length) - xSlope * xX) / Length\n    pos:= iff(close > xLRI, 1,\n           iff(close < xLRI, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Line Regression Intercept", shorttitle="Combo", overlay = true)\nline1 = input(true, "---- 123 Reversal ----")\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nline2 = input(true, "---- Line Regression Intercept ----")\nLengthLRI = input(14, minval=1)\nxSeria = input(title="Source", type=input.source, defval=close)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposLRI = LRI(LengthLRI,xSeria)\npos = iff(posReversal123 == 1 and posLRI == 1 , 1,\n\t   iff(posReversal123 == -1 and posLRI == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMReversalandLinearRegressionInterceptComboStrategy5b6017(PinePortBase, IStrategy):
    source_id = "SM_5b6017d026f5f26a"
    source_file = '逆转与线性回归截距组合策略Reversal-and-Linear-Regression-Intercept-Combo-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'line1': True, 'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'line2': True, 'LengthLRI': 14, 'xSeria': 'close', 'reverse': False}
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
