"""batch_011 port of 趋势反转型跨时间幅特异波动率交易策略Trend-Reversal-with-Intrabar-Volatility-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-26 00:00:00\nend: 2024-02-25 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("3 10 Oscillator Profile Flagging", shorttitle="3 10 Oscillator Profile Flagging", overlay=false)\n\nsignalBiasValue = input(title="Signal Bias", defval=0.26)\nmacdBiasValue = input(title="MACD Bias", defval=0.8)\nshortLookBack = input( title="Short LookBack", defval=3)\nlongLookBack = input( title="Long LookBack", defval=10)\ntakeProfit = input( title="Take Profit", defval=0.75)\nstopLoss = input( title="Stop Loss", defval=0.5)\n\nfast_ma = ta.sma(close, 3)\nslow_ma = ta.sma(close, 10)\nmacd = fast_ma - slow_ma\nsignal = ta.sma(macd, 16)\nhline(0, "Zero Line", color = color.black)\n\nbuyVolume = volume*((close-low)/(high-low))\nsellVolume = volume*((high-close)/(high-low))\nbuyVolSlope = buyVolume - buyVolume[1]\nsellVolSlope = sellVolume - sellVolume[1]\nsignalSlope = ( signal - signal[1] )\nmacdSlope = ( macd - macd[1] )\nplot(macd, color=color.blue, title="Total Volume")\nplot(signal, color=color.orange, title="Total Volume")\nintrabarRange = high - low\n\ngetLookBackSlope(lookBack) => signal - signal[lookBack]\ngetBuyerVolBias(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if buyVolume[i] > sellVolume[i]\n            j += 1\n    j\n\ngetSellerVolBias(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if sellVolume[i] > buyVolume[i]\n            j += 1\n    j\n\ngetVolBias(lookBack) =>\n    float b = 0\n    float s = 0\n    for i = 1 to lookBack\n        b += buyVolume[i]\n        s += sellVolume[i]\n    b > s\n\ngetSignalBuyerBias(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if signal[i] > signalBiasValue\n            j += 1\n    j\n\ngetSignalSellerBias(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if signal[i] < ( 0 - signalBiasValue )\n            j += 1\n    j\n\ngetSignalNoBias(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if signal[i] < signalBiasValue and signal[i] > ( 0 - signalBiasValue )\n            j += 1\n    j\n\ngetPriceRising(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if close[i] > close[i + 1]\n            j += 1\n    j\n\n\ngetPriceFalling(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if close[i] < close[i + 1] \n            j += 1\n    j\n\ngetRangeNarrowing(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if intrabarRange[i] < intrabarRange[i + 1] \n            j+= 1\n    j\n\ngetRangeBroadening(lookBack) =>\n    j = 0\n    for i = 1 to lookBack\n        if intrabarRange[i] > intrabarRange[i + 1] \n            j+= 1\n    j\n\nbool isNegativeSignalReversal = signalSlope < 0 and signalSlope[1] > 0\nbool isNegativeMacdReversal = macdSlope < 0 and macdSlope[1] > 0\n\nbool isPositiveSignalReversal = signalSlope > 0 and signalSlope[1] < 0\nbool isPositiveMacdReversal = macdSlope > 0 and macdSlope[1] < 0\n\nbool hasBearInversion = signalSlope > 0 and macdSlope < 0\nbool hasBullInversion = signalSlope < 0 and macdSlope > 0\n\nbool hasSignalBias = math.abs(signal) >= signalBiasValue\nbool hasNoSignalBias = signal < signalBiasValue and signal > ( 0 - signalBiasValue )\n\nbool hasSignalBuyerBias = hasSignalBias and signal > 0\nbool hasSignalSellerBias = hasSignalBias and signal < 0\n\nbool hasPositiveMACDBias = macd > macdBiasValue\nbool hasNegativeMACDBias = macd < ( 0 - macdBiasValue )\n\nbool hasBullAntiPattern = ta.crossunder(macd, signal)\nbool hasBearAntiPattern = ta.crossover(macd, signal)\n\nbool hasSignificantBuyerVolBias = buyVolume > ( sellVolume * 1.5 )\nbool hasSignificantSellerVolBias = sellVolume > ( buyVolume * 1.5 )\n\n// 7.48 Profit 52.5% \nif ( hasSignificantBuyerVolBias and getPriceRising(shortLookBack) == shortLookBack  and getBuyerVolBias(shortLookBack) == shortLookBack and hasPositiveMACDBias and hasBullInversion)\n    strategy.entry("Short1", strategy.short, qty=10)\nstrategy.exit("TPS", "Short1", limit=strategy.position_avg_price - takeProfit, stop=strategy.position_avg_price + stopLoss)\n\n// 32.53 Profit 47.91%\nif ( getPriceFalling(shortLookBack) and (getVolBias(shortLookBack) == false) and signalSlope < 0 and hasSignalSellerBias)\n    strategy.entry("Long1", strategy.long, qty=10)\nstrategy.exit("TPS", "Long1", limit=strategy.position_avg_price + takeProfit, stop=strategy.position_avg_price - stopLoss)'

class SM6FED7FC9001F4605(PinePortBase, IStrategy):
    source_id = "SM_6fed7fc9001f4605"
    source_file = '趋势反转型跨时间幅特异波动率交易策略Trend-Reversal-with-Intrabar-Volatility-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'signalBiasValue': 0.26, 'macdBiasValue': 0.8, 'shortLookBack': 3, 'longLookBack': 10, 'takeProfit': 0.75, 'stopLoss': 0.5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'loop', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
