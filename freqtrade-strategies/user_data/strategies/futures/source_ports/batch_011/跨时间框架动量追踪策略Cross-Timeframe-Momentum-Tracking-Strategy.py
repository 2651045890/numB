"""batch_011 port of 跨时间框架动量追踪策略Cross-Timeframe-Momentum-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 28/01/2021\n// This is combo strategies for get a cumulative signal. \n//\n// First strategy\n// This System was created from the Book "How I Tripled My Money In The \n// Futures Market" by Ulf Jensen, Page 183. This is reverse type of strategies.\n// The strategy buys at market, if close price is higher than the previous close \n// during 2 days and the meaning of 9-days Stochastic Slow Oscillator is lower than 50. \n// The strategy sells at market, if close price is lower than the previous close price \n// during 2 days and the meaning of 9-days Stochastic Fast Oscillator is higher than 50.\n//\n// Second strategy\n// MACD – Moving Average Convergence Divergence. The MACD is calculated \n// by subtracting a 26-day moving average of a security\'s price from a \n// 12-day moving average of its price. The result is an indicator that \n// oscillates above and below zero. When the MACD is above zero, it means \n// the 12-day moving average is higher than the 26-day moving average. \n// This is bullish as it shows that current expectations (i.e., the 12-day \n// moving average) are more bullish than previous expectations (i.e., the \n// 26-day average). This implies a bullish, or upward, shift in the supply/demand \n// lines. When the MACD falls below zero, it means that the 12-day moving average \n// is less than the 26-day moving average, implying a bearish shift in the \n// supply/demand lines.\n// A 9-day moving average of the MACD (not of the security\'s price) is usually \n// plotted on top of the MACD indicator. This line is referred to as the "signal" \n// line. The signal line anticipates the convergence of the two moving averages \n// (i.e., the movement of the MACD toward the zero line).\n// Let\'s consider the rational behind this technique. The MACD is the difference \n// between two moving averages of price. When the shorter-term moving average rises \n// above the longer-term moving average (i.e., the MACD rises above zero), it means \n// that investor expectations are becoming more bullish (i.e., there has been an \n// upward shift in the supply/demand lines). By plotting a 9-day moving average of \n// the MACD, we can see the changing of expectations (i.e., the shifting of the \n// supply/demand lines) as they occur.\n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nReversal123(Length, KSmoothing, DLength, Level) =>\n    vFast = sma(stoch(close, high, low, Length), KSmoothing) \n    vSlow = sma(vFast, DLength)\n    pos = 0.0\n    pos := iff(close[2] < close[1] and close > close[1] and vFast < vSlow and vFast > Level, 1,\n\t         iff(close[2] > close[1] and close < close[1] and vFast > vSlow and vFast < Level, -1, nz(pos[1], 0))) \n\tpos\n\nMACD(fastLength,slowLength,signalLength) =>\n    pos = 0.0\n    fastMA = ema(close, fastLength)\n    slowMA = ema(close, slowLength)\n    macd = fastMA - slowMA\n    signal = sma(macd, signalLength)\n    pos:= iff(signal < macd , 1,\n\t       iff(signal > macd, -1, nz(pos[1], 0))) \n    pos\n\nstrategy(title="Combo Backtest 123 Reversal & MACD Crossover", shorttitle="Combo", overlay = true)\nline1 = input(true, "---- 123 Reversal ----")\nLength = input(14, minval=1)\nKSmoothing = input(1, minval=1)\nDLength = input(3, minval=1)\nLevel = input(50, minval=1)\n//-------------------------\nfastLength = input(8, minval=1)\nslowLength = input(16,minval=1)\nsignalLength=input(11,minval=1)\nxSeria = input(title="Source", type=input.source, defval=close)\nreverse = input(false, title="Trade reverse")\nposReversal123 = Reversal123(Length, KSmoothing, DLength, Level)\nposMACD = MACD(fastLength,slowLength, signalLength)\npos = iff(posReversal123 == 1 and posMACD == 1 , 1,\n\t   iff(posReversal123 == -1 and posMACD == -1, -1, 0)) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1 , 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t \nif (possig == 0) \n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404: possig == 1 ? #079605 : #0536b3 )'

class SM41DE76222982B20E(PinePortBase, IStrategy):
    source_id = "SM_41de76222982b20e"
    source_file = '跨时间框架动量追踪策略Cross-Timeframe-Momentum-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'line1': True, 'Length': 14, 'KSmoothing': 1, 'DLength': 3, 'Level': 50, 'fastLength': 8, 'slowLength': 16, 'signalLength': 11, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
