"""batch_011 port of 自适应ATR-ADX趋势策略V2An-Adaptive-ATR-ADX-Trend-Strategy-V2.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-28 00:00:00\nend: 2023-12-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n// From mortdiggiddy\'s indicator to strategy\n// See also: https://www.tradingview.com/u/mortdiggiddy/\n\nstrategy(title = "Adaptive ATR-ADX Trend V2", shorttitle = "Adaptive ATR V2 Strategy", overlay = true)\n\n//Mode\nsrc = input(title = "Source",  defval = hlc3)\natrLen = input(title = "ATR",  defval = 21, minval = 1, maxval = 100)\nm1 = input(title = "ATR Multiplier - ADX Rising", type = float, defval = 3.5, minval = 1, step = 0.1, maxval = 100)\nm2 = input(title = "ATR Multiplier - ADX Falling", type = float, defval = 1.75, minval = 1, step = 0.1, maxval = 100)\n\nadxLen = input(title = "ADX",  defval = 14, minval = 1, maxval = 100)\nadxThresh = input(title = "ADX Threshold",  defval = 30, minval = 1)\naboveThresh = input(true, title = "ADX Above Threshold uses ATR Falling Multiplier Even if Rising?")\nuseHeiken = input(false, title = "Use Heiken-Ashi Bars (Source will be ohlc4)")\n    \n// DI-Pos, DI-Neg, ADX\n\nhR = change(high)\nlR = -change(low)\n\ndmPos = hR > lR ? max(hR, 0) : 0\ndmNeg = lR > hR ? max(lR, 0) : 0\n\nsTR = nz(sTR[1]) - nz(sTR[1]) / adxLen + tr\nsDMPos = nz(sDMPos[1]) - nz(sDMPos[1]) / adxLen + dmPos\nsDMNeg = nz(sDMNeg[1]) - nz(sDMNeg[1]) / adxLen + dmNeg\n\nDIP = sDMPos / sTR * 100\nDIN = sDMNeg / sTR * 100\nDX = abs(DIP - DIN) / (DIP + DIN) * 100\nadx = sma(DX, adxLen)\n\n// Heiken-Ashi\n\nxClose = ohlc4\nxOpen = (nz(xOpen[1]) + nz(close[1])) / 2\nxHigh = max(high, max(xOpen, xClose))\nxLow = min(low, min(xOpen, xClose))\n\n// Trailing ATR\n\nv1 = abs(xHigh - xClose[1])\nv2 = abs(xLow - xClose[1])\nv3 = xHigh - xLow\n\ntrueRange = max(v1, max(v2, v3))\natr = useHeiken ? rma(trueRange, atrLen) : atr(atrLen)\n\nm = rising(adx, 1) and (adx < adxThresh or not aboveThresh) ? m1 : falling(adx, 1) or (adx > adxThresh and aboveThresh) ? m2 : nz(m[1])\nmUp = DIP >= DIN ? m : m2\nmDn = DIN >= DIP ? m : m2\n\nsrc_ = useHeiken ? xClose : src\nc = useHeiken ? xClose : close\nt = useHeiken ? (xHigh + xLow) / 2 : hl2\n\nup = t - mUp * atr\ndn = t + mDn * atr\n\nTUp = max(src_[1], c[1]) > TUp[1] ? max(up, TUp[1]) : up\nTDown = min(src_[1], c[1]) < TDown[1] ? min(dn, TDown[1]) : dn\n\ntrend = min(src_, min(c, close)) > TDown[1] ? 1 : max(src_, max(c, close)) < TUp[1]? -1 : nz(trend[1], 1)\nstop = trend == 1 ? TUp : TDown\ntrendChange = change(trend)\n\nlongCondition = (trendChange > 0)\nif (longCondition)\n    strategy.entry("long", strategy.long)\nshortCondition = (trendChange < 0)\nif (shortCondition)\n    strategy.entry("short", strategy.short)    \n    \n// Plot\n\nlineColor = not(trendChange) ? trend > 0 ? #00FF00DD : #FF0000DD : #00000000\nshapeColor = trendChange ? trendChange > 0 ? #00FF00F8 : #FF0000F8 : #00000000\n\nplot(stop, color = lineColor, style = line, linewidth = 1, title = "ATR Trend")\nplotshape(trendChange ? stop : na, style = shape.circle, size = size.tiny, location = location.absolute, color = shapeColor, title = "Change")\n\nalertcondition(trendChange > 0, title = "ATR-ADX Change Up", message = "ATR-ADX Change Up")\nalertcondition(trendChange < 0, title = "ATR-ADX Change Down", message = "ATR-ADX Change Down")\n\n// end'

class SMCA83588FE710F090(PinePortBase, IStrategy):
    source_id = "SM_ca83588fe710f090"
    source_file = '自适应ATR-ADX趋势策略V2An-Adaptive-ATR-ADX-Trend-Strategy-V2.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrLen': 21, 'm1': 3.5, 'm2': 1.75, 'adxLen': 14, 'adxThresh': 30, 'aboveThresh': True, 'useHeiken': False}
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
