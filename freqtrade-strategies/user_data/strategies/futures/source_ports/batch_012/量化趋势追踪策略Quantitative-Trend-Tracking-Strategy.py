"""batch_012 port of 量化趋势追踪策略Quantitative-Trend-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 5h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © abilash.s.90\n\n\ndIMinusCalc(adxLen) =>\n    \n    smoothedTrueRange = 0.0\n    smoothedDirectionalMovementMinus = 0.0\n    dIMinus = 0.0\n    trueRange = 0.0\n    directionalMovementMinus = 0.0\n    \n    trueRange := max(max(high-low, abs(high-nz(close[1]))), abs(low-nz(close[1])))\n    directionalMovementMinus := nz(low[1])-low > high-nz(high[1]) ? max(nz(low[1])-low, 0): 0\n    \n    smoothedTrueRange := nz(smoothedTrueRange[1]) - (nz(smoothedTrueRange[1])/adxLen) + trueRange\n    smoothedDirectionalMovementMinus := nz(smoothedDirectionalMovementMinus[1]) - (nz(smoothedDirectionalMovementMinus[1])/adxLen) + directionalMovementMinus\n    \n    dIMinus := smoothedDirectionalMovementMinus / smoothedTrueRange * 100\n    \n    dIMinus\n\ndIPlusCalc(adxLen) =>\n    \n    smoothedTrueRange = 0.0\n    smoothedDirectionalMovementPlus = 0.0\n    dIPlus =  0.0\n    trueRange = 0.0\n    directionalMovementPlus = 0.0\n    \n    trueRange := max(max(high-low, abs(high-nz(close[1]))), abs(low-nz(close[1])))\n    directionalMovementPlus := high-nz(high[1]) > nz(low[1])-low ? max(high-nz(high[1]), 0): 0\n    \n    smoothedTrueRange := nz(smoothedTrueRange[1]) - (nz(smoothedTrueRange[1])/adxLen) + trueRange\n    smoothedDirectionalMovementPlus := nz(smoothedDirectionalMovementPlus[1]) - (nz(smoothedDirectionalMovementPlus[1])/adxLen) + directionalMovementPlus\n    \n    dIPlus := smoothedDirectionalMovementPlus / smoothedTrueRange * 100\n    \n    dIPlus\n    \n    \nAdx(adxLen) =>\n    dIPlus =  0.0\n    dIMinus = 0.0\n    dX = 0.0\n    aDX = 0.0\n    dIPlus := dIPlusCalc(adxLen)\n    dIMinus := dIMinusCalc(adxLen)\n    dX := abs(dIPlus-dIMinus) / (dIPlus+dIMinus)*100\n    aDX := sma(dX, adxLen)\n    \n    aDX\n    \nBarInSession(sess) => time(timeframe.period, sess) != 0\n\n\n//@version=4\nstrategy("Bollinger Band + RSI + ADX + MACD", overlay=true)\n\n//Session\n\nsession = input(title="Trading Session", type=input.session, defval="0930-1500")\n\nsessionColor = BarInSession(session) ? color.green : na\n\nbgcolor(color=sessionColor, transp=95)\n\n// Bollinger Bands\nsrc = input(high, title="Bollinger Band Source", type=input.source)\nlength = input(3, minval=1, type=input.integer, title="Bollinger Band Length")\nmult = input(4.989, minval=0.001, maxval=50, step=0.001, type=input.float, title="Bollinger Band Std Dev")\nbasis = sma(src, length)\ndev = mult * stdev(src, length)\nupper = basis + dev\nlower = basis - dev\n\n\nplot(upper, title="Bollinger Band Upper", color=color.red)\nplot(lower, title="Bollinger Band Lower", color=color.green)\n\n// RSI\nrsiSrc = input(close, title="RSI Source", type=input.source)\nrsiLength = input(16, minval=1, type=input.integer, title="RSI Length")\nrsiComparator = input(39.2, title="RSI Comparator", type=input.float, step=0.1)\n\nrsi = rsi(rsiSrc, rsiLength)\n\n// ADX\nadxLength = input(14, minval=1, type=input.integer, title="ADX Length")\nadxComparator = input(14, minval=1, type=input.integer, title="ADX Comparator")\n\nadx = Adx(adxLength)\n\n// Heikinashi\n\nhaClose = security(heikinashi(syminfo.ticker), timeframe.period, close)\nhaOpen = security(heikinashi(syminfo.ticker), timeframe.period, open)\n\nnextHaOpen = (haOpen + haClose) / 2\n\n//MACD\n\nmacdCalcTypeProcessed = input(title="MACD Source", type=input.source, defval=high)\nfast = input(12, title="MACD Fast")\nslow = input(20, title="MACD Slow")\nsignalLen = input(15, title="MACD Signal")\n\nfastMA = ema(macdCalcTypeProcessed, fast)\nslowMA = ema(macdCalcTypeProcessed, slow)\nmacd = fastMA - slowMA\nsignal = sma(macd, signalLen)\n\n\n\nlongCondition() =>\n    (low < lower) and (rsi[0] > rsiComparator) and (adx > adxComparator) and (close > nextHaOpen) and BarInSession(session) and macd > signal\n\nstop = (close - max((low - (low * 0.0022)), (close - (close * 0.0032)))) / syminfo.mintick\ntarget = (max(upper, (close + (close * 0.0075))) - close) / syminfo.mintick\n\n\nstrategy.entry("SX,LE", strategy.long, when=longCondition(), comment="SX,LE")\nstrategy.close_all(when=(not BarInSession(session)))\nstrategy.exit("LX", from_entry="SX,LE", profit=target, loss=stop)\n\n'

class SMQuantitativeTrendTrackingStrategyf34e09(PinePortBase, IStrategy):
    source_id = "SM_f34e0911c72b4213"
    source_file = '量化趋势追踪策略Quantitative-Trend-Tracking-Strategy.md'
    timeframe = '5h'
    can_short = False
    source_defaults = {'session': '0930-1500', 'src': 'high', 'length': 3, 'mult': 4.989, 'rsiSrc': 'close', 'rsiLength': 16, 'rsiComparator': 39.2, 'adxLength': 14, 'adxComparator': 14, 'macdCalcTypeProcessed': 'high', 'fast': 12, 'slow': 20, 'signalLen': 15}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
