"""batch_012 port of 量化双因子反转惯性交易策略Quantitative-Dual-Factor-Reversal-Inertia-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-12 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 27/11/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// The inertia indicator measures the market, stock or currency pair momentum and \n// trend by measuring the security smoothed RVI (Relative Volatility Index). \n// The RVI is a technical indicator that estimates the general direction of the \n// volatility of an asset.\n// The inertia indicator returns a value that is comprised between 0 and 100. \n// Positive inertia occurs when the indicator value is higher than 50. As long as \n// the inertia value is above 50, the long-term trend of the security is up. The inertia \n// is negative when its value is lower than 50, in this case the long-term trend is \n// down and should stay down if the inertia stays below 50.\n//\n// You can change long to short in the Input Settings\n// Please, use it only for learning or paper trading. Do not for real trading.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nInertia(Period, Smooth) =>\n    pos = 0.0\n    nU = 0.0\n    nD = 0.0\n    xPrice = close\n    StdDev = stdev(xPrice, Period)\n    d = iff(close > close[1], 0, StdDev)\n    u = iff(close > close[1], StdDev, 0)\n    nU := (13 * nz(nU[1],0) + u) / 14\n    nD := (13 * nz(nD[1],0) + d) / 14\n    nRVI = 100 * nU / (nU + nD)\n    nRes = ema(nRVI, Smooth)\n    pos :=iff(nRes > 50, 1,\n    \t   iff(nRes < 50, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & Inertia Strategy", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nPeriod = input(10, minval=1)\nSmooth = input(14, minval=1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposInertia = Inertia(Period, Smooth)\npos = iff(posReversal123 == 1 and posInertia == 1 , 1,\n\t   iff(posReversal123 == -1 and posInertia == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMQuantitativeDualFactorReversalInertiaTradingStrategycb0cb8(PinePortBase, IStrategy):
    source_id = "SM_cb0cb8fd19c3b7cf"
    source_file = '量化双因子反转惯性交易策略Quantitative-Dual-Factor-Reversal-Inertia-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'Period': 10, 'Smooth': 14, 'reverse': False}
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
