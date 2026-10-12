"""batch_012 port of 高级布林带指标组合动态趋势突破交易策略-Advanced-Bollinger-Bands-Multi-Indicator-Dynamic-Trend-Breakout-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-02-01 00:00:00\nend: 2025-02-19 00:00:00\nperiod: 1h\nbasePeriod: 1m\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized Bollinger Bands Breakout Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=1)\n\n// ? Bollinger Bands Settings\nlength = input(20, title="Bollinger Length")\nmult = input(2.0, title="Bollinger Multiplier")\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\nupperBand = basis + dev\nlowerBand = basis - dev\n\n// ? ADX Calculation (Manually Calculated)\nadxLength = input(14, title="ADX Length")\ndmiLength = input(14, title="DMI Length")\nupMove = high - ta.highest(high[1], 1)\ndownMove = ta.lowest(low[1], 1) - low\nplusDM = upMove > downMove and upMove > 0 ? upMove : 0\nminusDM = downMove > upMove and downMove > 0 ? downMove : 0\nplusDI = ta.sma(plusDM, dmiLength) / ta.atr(dmiLength) * 100\nminusDI = ta.sma(minusDM, dmiLength) / ta.atr(dmiLength) * 100\ndx = math.abs(plusDI - minusDI) / (plusDI + minusDI) * 100\nadx = ta.sma(dx, adxLength)\n\n// ? Additional Filters\nrsi = ta.rsi(close, 14)\n\n// ✅ Entry Conditions\nlongCondition = ta.crossover(close, upperBand) and rsi > 40 and rsi < 60 and adx > 25\nshortCondition = ta.crossunder(close, lowerBand) and rsi > 40 and rsi < 60 and adx > 25\n\n// ? ATR-based Stop Loss\nstopLossMultiplier = input(1.5, title="Stop Loss (ATR Multiplier)") \natrValue = ta.atr(14)\nlongSL = close - (atrValue * stopLossMultiplier)\nshortSL = close + (atrValue * stopLossMultiplier)\n\n// ✅ Trailing Stop\ntrailMultiplier = input(1, title="Trailing Stop Multiplier")\nlongTrailStop = close - (atrValue * trailMultiplier)\nshortTrailStop = close + (atrValue * trailMultiplier)\n\n// ? Executing Trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", from_entry="Long", stop=longSL, trail_price=longTrailStop, trail_offset=atrValue * 0.5)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", from_entry="Short", stop=shortSL, trail_price=shortTrailStop, trail_offset=atrValue * 0.5)\n\n// ? Plot Bollinger Bands\nplot(upperBand, title="Upper Band", color=color.blue)\nplot(lowerBand, title="Lower Band", color=color.red)\nplot(basis, title="Middle Band", color=color.gray)\n\n'

class SMAdvancedBollingerBandsMultiIndicatorDynamicTrendBreakoube87a5(PinePortBase, IStrategy):
    source_id = "SM_be87a56ea02d90ac"
    source_file = '高级布林带指标组合动态趋势突破交易策略-Advanced-Bollinger-Bands-Multi-Indicator-Dynamic-Trend-Breakout-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0, 'adxLength': 14, 'dmiLength': 14, 'stopLossMultiplier': 1.5, 'trailMultiplier': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
