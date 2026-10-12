"""batch_012 port of 高低位突破量化策略High-Low-Breakout-for-Quantitative-Trading.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-10 00:00:00\nend: 2023-11-09 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 25/11/2020\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// This script shows a high and low period value.\n//    Width - width of lines\n//    SelectPeriod - Day or Week or Month and etc.\n//    LookBack - Shift levels 0 - current period, 1 - previous and etc. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\n    \nHLL(LookBack, SelectPeriod) =>\n    pos = 0.0\n    xHigh  = security(syminfo.tickerid, SelectPeriod, high[LookBack])\n    xLow   = security(syminfo.tickerid, SelectPeriod, low[LookBack])\n    vS1 = xHigh\n    vR1 = xLow\n    pos := iff(close > vR1, 1,\n             iff(close < vS1, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & High and Low Levels", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nSelectPeriod = input(title="Resolution", type=input.resolution, defval="D")\nLookBack = input(1,  minval=0)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposHLL = HLL(LookBack, SelectPeriod)\npos = iff(posReversal123 == 1 and posHLL == 1 , 1,\n\t   iff(posReversal123 == -1 and posHLL == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )\n'

class SMHighLowBreakoutforQuantitativeTradingc27a4c(PinePortBase, IStrategy):
    source_id = "SM_c27a4ca77c997b90"
    source_file = '高低位突破量化策略High-Low-Breakout-for-Quantitative-Trading.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'SelectPeriod': 'D', 'LookBack': 1, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
