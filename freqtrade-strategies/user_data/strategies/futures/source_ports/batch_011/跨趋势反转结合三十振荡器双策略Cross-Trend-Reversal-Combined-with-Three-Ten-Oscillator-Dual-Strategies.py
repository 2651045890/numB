"""batch_011 port of 跨趋势反转结合三十振荡器双策略Cross-Trend-Reversal-Combined-with-Three-Ten-Oscillator-Dual-Strategies.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-11 00:00:00\nend: 2024-01-18 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 04/12/2019\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// TradeStation does not allow the user to make a Multi Data Chart with \n// a Tick Bar Chart and any other type a chart. This indicator allows the \n// user to plot a daily 3-10 Oscillator on a Tick Bar Chart or any intraday interval.\n// Walter Bressert\'s 3-10 Oscillator is a detrending oscillator derived \n// from subtracting a 10 day moving average from a 3 day moving average. \n// The second plot is an 16 day simple moving average of the 3-10 Oscillator. \n// The 16 period moving average is the slow line and the 3/10 oscillator is \n// the fast line.\n// For more information on the 3-10 Oscillator see Walter Bressert\'s book \n// "The Power of Oscillator/Cycle Combinations" \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nD_Three(Length1, Length2, Length3) =>\n    pos = 0.0\n    xPrice =  security(syminfo.tickerid,"D", hl2)\n    xfastMA = ema(xPrice, Length1)\n    xslowMA = ema(xPrice, Length2)\n    xMACD = xfastMA - xslowMA\n    xSignal = sma(xMACD, Length3)\n    pos := iff(xSignal > xMACD, -1,\n    \t     iff(xSignal < xMACD, 1, nz(pos[1], 0)))     \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & D_Three Ten Osc", shorttitle="Combo", overlay = true)\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nLength1 = input(3, minval=1)\nLength2 = input(10, minval=1)\nLength3 = input(16, minval=1)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposD_Three = D_Three(Length1, Length2, Length3)\npos = iff(posReversal123 == 1 and posD_Three == 1 , 1,\n\t   iff(posReversal123 == -1 and posD_Three == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SME5E95AC2AACD2809(PinePortBase, IStrategy):
    source_id = "SM_e5e95ac2aacd2809"
    source_file = '跨趋势反转结合三十振荡器双策略Cross-Trend-Reversal-Combined-with-Three-Ten-Oscillator-Dual-Strategies.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'Length1': 3, 'Length2': 10, 'Length3': 16, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
