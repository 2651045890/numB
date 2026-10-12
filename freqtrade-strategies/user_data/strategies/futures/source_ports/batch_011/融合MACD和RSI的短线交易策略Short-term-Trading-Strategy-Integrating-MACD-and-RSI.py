"""batch_011 port of 融合MACD和RSI的短线交易策略Short-term-Trading-Strategy-Integrating-MACD-and-RSI.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-06 00:00:00\nend: 2023-09-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Uraynium V3", overlay=false, pyramiding = 0, calc_on_every_tick=true, precision=1, currency="USD", default_qty_value=10, default_qty_type=strategy.cash,initial_capital=100,commission_type=strategy.commission.percent,commission_value=0.1) \n// === INPUT BACKTEST RANGE ===\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2019, title = "From Year", minval = 2017)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 2020, title = "To Year", minval = 2017)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\ninTimeframe()  => true\n\noverSold      = input( 20 , minval = 1, title = "RSI Oversold")\noverBought    = input( 80 , minval = 1, title = "RSI Overbought")\nrsiLength     = input(14, minval = 1, title = "RSI Length")\nfastLength    = input(12, minval = 1, title = "MACD fast")\nslowlength    = input(26, minval = 1, title = "MACD slow")\nMACDLength    = input( 9, minval = 1, title = "MACD length")\nstopLoss      = input(   10, minval = 1, title = "Stop Loss (price %)")\ntakeProfit    = input(   50, minval = 1, title = "Take Profit (price %)")\ntriggerPosLvl = input(    2, minval = 1 ,title ="Take Position Threshold", type=input.float)\nsrc = close\n\n// === CALC ===\n\nstopLossValue        = close*(stopLoss/100)/syminfo.mintick\ntakeProfitValue      = close*(takeProfit/100)/syminfo.mintick\n\nvrsi = rsi(src, rsiLength)\n//avgRSI = vrsi*0.5 + vrsi[1]*0.25 + vrsi[2]*0.125 + vrsi[3]*0.0625\navgRSI = (4*vrsi + 3*vrsi + 2*vrsi[2] + vrsi[3])/10\n[macdLine, signalLine, histLine] = macd(src, fastLength, slowlength, MACDLength)\n\n\nMACDdelta         = signalLine - macdLine\nisMACDRunLong     = signalLine > macdLine\nisMACDRunShort    = macdLine < signalLine\nisMACDSwitchLong  = crossover(MACDdelta, 0)\nisMACDSwitchShort = crossunder(MACDdelta, 0)\nisMACDCross       = crossover(MACDdelta, 0) or crossunder(MACDdelta, 0)\n\nbuySignal =  (histLine-histLine[1]) + (avgRSI - avgRSI[1])\n\n// === ACTION ===\nisPosLong    = strategy.position_size > 0\nisPosShort   = strategy.position_size < 0\nisNoMarginPos= strategy.position_size == 0\nentryLong  = (isNoMarginPos or isPosShort) and ( buySignal >  triggerPosLvl )\nentryShort = (isNoMarginPos or isPosLong ) and ( buySignal < -triggerPosLvl ) \n\nif inTimeframe()\n    strategy.entry("Long" , strategy.long,  comment="Entry Long",  when=entryLong )\n    strategy.entry("Short", strategy.short, comment="Entry Short", when=entryShort)\n    strategy.entry("Long" , strategy.long,  comment="Switch Long", when=entryLong)\n    strategy.entry("Short", strategy.short, comment="Switch Short",when=entryShort)\n    strategy.exit("Stop (long SL/TP)",  loss=stopLossValue, profit=takeProfitValue, when=entryLong )  \n    strategy.exit("Stop (short SL/TP)", loss=stopLossValue, profit=takeProfitValue, when=entryShort)  \n    strategy.close("Long" , when=entryShort)\n    strategy.close("Short", when=entryLong)    \n\n// === DRAW ===\nposColor = isNoMarginPos ?  color.black : isPosLong ? color.green : color.red\nplot(100, color=posColor,style=plot.style_area, transp=90, histbase=0)\n        \nplot(buySignal+overBought, color=color.green)\nplot(50+macdLine/4, color=color.yellow)\nplot(50+signalLine/4, color=color.orange)\nhistColor = histLine[1]-histLine > 0 ? color.red : color.green\nplot(overSold+histLine/2, color=histColor, style=plot.style_histogram, histbase=overSold, transp=50, linewidth=2)\n\nrsicolor = avgRSI>overBought ? color.red : avgRSI<overSold ? color.green : color.blue\nplot(avgRSI,color=rsicolor, linewidth=2)\n//plot(vrsi,color=color.purple, linewidth=2)\nhline(overBought, color=color.red)\nhline(overSold, color=color.green)\nhline(50, color=color.gray)\n'

class SM1A75526E1125C3E7(PinePortBase, IStrategy):
    source_id = "SM_1a75526e1125c3e7"
    source_file = '融合MACD和RSI的短线交易策略Short-term-Trading-Strategy-Integrating-MACD-and-RSI.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'FromMonth': 1, 'FromDay': 1, 'FromYear': 2019, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 2020, 'overSold': 20, 'overBought': 80, 'rsiLength': 14, 'fastLength': 12, 'slowlength': 26, 'MACDLength': 9, 'stopLoss': 10, 'takeProfit': 50, 'triggerPosLvl': 2}
    source_qty_type = 'cash'
    source_qty_value = 10
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 100
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
