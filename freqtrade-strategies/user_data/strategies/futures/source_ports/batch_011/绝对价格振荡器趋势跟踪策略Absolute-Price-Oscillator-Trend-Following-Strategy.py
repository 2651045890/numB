"""batch_011 port of 绝对价格振荡器趋势跟踪策略Absolute-Price-Oscillator-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-14 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 20/09/2018\n// The Absolute Price Oscillator displays the difference between two exponential \n// moving averages of a security\'s price and is expressed as an absolute value.\n// How this indicator works\n//    APO crossing above zero is considered bullish, while crossing below zero is bearish.\n//    A positive indicator value indicates an upward movement, while negative readings \n//      signal a downward trend.\n//    Divergences form when a new high or low in price is not confirmed by the Absolute Price \n//      Oscillator (APO). A bullish divergence forms when price make a lower low, but the APO \n//      forms a higher low. This indicates less downward momentum that could foreshadow a bullish \n//      reversal. A bearish divergence forms when price makes a higher high, but the APO forms a \n//      lower high. This shows less upward momentum that could foreshadow a bearish reversal.\n//\n// You can change long to short in the Input Settings\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nstrategy(title="Absolute Price Oscillator (APO) Backtest 2.0", shorttitle="APO")\nLengthShortEMA = input(10, minval=1)\nLengthLongEMA = input(20, minval=1)\nBuyZone = input(3, step = 0.01)\nSellZone = input(-3, step = 0.01)\nreverse = input(false, title="Trade reverse")\nhline(BuyZone, color=green, linestyle=line)\nhline(SellZone, color=red, linestyle=line)\nhline(0, color=gray, linestyle=line)\nxPrice = close\nxShortEMA = ema(xPrice, LengthShortEMA)\nxLongEMA = ema(xPrice, LengthLongEMA)\nxAPO = xShortEMA - xLongEMA\npos = iff(xAPO > BuyZone, 1,\n       iff(xAPO < SellZone, -1, nz(pos[1], 0))) \npossig = iff(reverse and pos == 1, -1,\n          iff(reverse and pos == -1, 1, pos))\t   \nif (possig == 1) \n    strategy.entry("Long", strategy.long)\nif (possig == -1)\n    strategy.entry("Short", strategy.short)\t   \t    \nbarcolor(possig == -1 ? red: possig == 1 ? green : blue )  \nplot(xAPO, color=blue, title="APO")'

class SM6DC7D1C5A970071F(PinePortBase, IStrategy):
    source_id = "SM_6dc7d1c5a970071f"
    source_file = '绝对价格振荡器趋势跟踪策略Absolute-Price-Oscillator-Trend-Following-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'LengthShortEMA': 10, 'LengthLongEMA': 20, 'BuyZone': 3, 'SellZone': -3, 'reverse': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
