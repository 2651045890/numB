"""batch_011 port of 融合布林带与RSI的动态多指标交易策略-Dynamic-Multi-Indicator-Trading-Strategy-Combining-Bollinger-Bands-and-RSI.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-24 00:00:00\nend: 2025-03-01 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Enhanced Bollinger Bands Strategy for Silver", overlay=true)\n\n// ? Input Variables\nlength = input(20, title="Bollinger Bands Length")\nmult = input(2.0, title="Bollinger Bands Multiplier")\nrsiLength = input(14, title="RSI Length")\nrsiOverbought = input(70, title="RSI Overbought Level")\nrsiOversold = input(30, title="RSI Oversold Level")\n\n// ? Volume Confirmation (Check if volume is above SMA of volume)\nvolLength = input(20, title="Volume SMA Length")\nvolSMA = ta.sma(volume, volLength)\nhighVolume = volume > volSMA\n\n// ? Calculate Bollinger Bands\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\nupperBand = basis + dev\nlowerBand = basis - dev\n\n// ? RSI Calculation\nrsi = ta.rsi(close, rsiLength)\n\n// ? Define Trading Conditions\nlongCondition = ta.crossover(close, lowerBand) and rsi < rsiOversold\nshortCondition = ta.crossunder(close, upperBand) and rsi > rsiOverbought\n\n// ? Breakout Conditions (Only valid if volume is high)\nbreakoutLong = ta.crossover(close, upperBand) and highVolume\nbreakoutShort = ta.crossunder(close, lowerBand) and highVolume\n\n// ? Squeeze Condition (Bollinger Bands Tightening)\nbandWidth = (upperBand - lowerBand) / basis\nsqueeze = ta.lowest(bandWidth, length) == bandWidth\n\n// ? Execute Trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\nif (breakoutLong)\n    strategy.entry("Breakout Long", strategy.long)\nif (breakoutShort)\n    strategy.entry("Breakout Short", strategy.short)\n\n// ? Stop Loss, Take Profit, and Trailing Stop\nstopLossPercent = input(2.0, title="Stop Loss %") / 100\ntakeProfitPercent = input(4.0, title="Take Profit %") / 100\ntrailingStopPercent = input(1.5, title="Trailing Stop %") / 100\n\nstopLossLong = close * (1 - stopLossPercent)\ntakeProfitLong = close * (1 + takeProfitPercent)\ntrailingStopLong = close * (1 - trailingStopPercent)\n\nstopLossShort = close * (1 + stopLossPercent)\ntakeProfitShort = close * (1 - takeProfitPercent)\ntrailingStopShort = close * (1 + trailingStopPercent)\n\n// Apply stop loss, take profit, and trailing stop\nstrategy.exit("Exit Long", from_entry="Long", stop=stopLossLong, limit=takeProfitLong, trail_points=trailingStopLong)\nstrategy.exit("Exit Short", from_entry="Short", stop=stopLossShort, limit=takeProfitShort, trail_points=trailingStopShort)\n\n// ? Alerts for Trade Signals\nalertcondition(longCondition, title="Buy Alert", message="Silver Buy Signal - Lower Band Touch & RSI Oversold")\nalertcondition(shortCondition, title="Sell Alert", message="Silver Sell Signal - Upper Band Touch & RSI Overbought")\nalertcondition(breakoutLong, title="Breakout Buy Alert", message="Silver Breakout Buy - High Volume")\nalertcondition(breakoutShort, title="Breakout Sell Alert", message="Silver Breakout Sell - High Volume")\n\n// ? Plot Bollinger Bands\nplot(upperBand, color=color.blue, title="Upper Band")\nplot(basis, color=color.orange, title="Middle Band")\nplot(lowerBand, color=color.blue, title="Lower Band")\n\n// ? Highlight Squeeze Areas\nbgcolor(squeeze ? color.yellow : na, transp=80, title="Bollinger Squeeze")\n\n// ? Plot Volume Confirmation (Optional)\nplot(highVolume ? volume : na, style=plot.style_columns, color=color.green, title="High Volume Confirmation")\n'

class SMAD312A2E0D4711B5(PinePortBase, IStrategy):
    source_id = "SM_ad312a2e0d4711b5"
    source_file = '融合布林带与RSI的动态多指标交易策略-Dynamic-Multi-Indicator-Trading-Strategy-Combining-Bollinger-Bands-and-RSI.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30, 'volLength': 20, 'stopLossPercent': 2.0, 'takeProfitPercent': 4.0, 'trailingStopPercent': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
