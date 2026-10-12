"""batch_012 port of 震荡突破策略Reversal-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-20 00:00:00\nend: 2023-10-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Bollinger Bands & Stochastic Scalping Strategy", shorttitle="BB & Stoch Scalp", overlay=true)\n\n// Bollinger Bands\nlength = input(20, title="Bollinger Bands Length")\nsrc = input(close, title="Source")\nmult = input(2, title="Multiplier")\nbasis = sma(src, length)\ndev = mult * stdev(src, length)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// Stochastic\nstochLength = input(14, title="Stochastic Length")\nsmoothK = input(5, title="Stochastic %K Smoothing")\nsmoothD = input(3, title="Stochastic %D Smoothing")\nk = sma(stoch(close, high, low, stochLength), smoothK)\nd = sma(k, smoothD)\n\n// Entry Conditions\nlongCondition = crossover(close, lowerBB) and crossover(k, 20)\nshortCondition = crossunder(close, upperBB) and crossunder(k, 80)\n\n// Exit Conditions\ntakeProfit = input(50, title="Take Profit (pips)")\n\nplotshape(series=longCondition, title="Long Entry Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(series=shortCondition, title="Short Entry Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n\n// Stop Loss\nstopLossPips = input(3, title="Stop Loss (pips)")\nstopLossLong = close - stopLossPips * syminfo.mintick\nstopLossShort = close + stopLossPips * syminfo.mintick\n\nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.entry("Short", strategy.short, when=shortCondition)\n\nstrategy.exit("Take Profit/Stop Loss", from_entry="Long", profit=takeProfit, stop=stopLossLong)\nstrategy.exit("Take Profit/Stop Loss", from_entry="Short", profit=takeProfit, stop=stopLossShort)\n\nplot(upperBB, title="Upper Bollinger Band", color=color.red)\nplot(lowerBB, title="Lower Bollinger Band", color=color.green)\n\nhline(80, "Overbought", color=color.red)\nhline(20, "Oversold", color=color.green)\n\n'

class SMReversalBreakoutStrategy63bb70(PinePortBase, IStrategy):
    source_id = "SM_63bb70d5154f58ec"
    source_file = '震荡突破策略Reversal-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'src': 'close', 'mult': 2, 'stochLength': 14, 'smoothK': 5, 'smoothD': 3, 'takeProfit': 50, 'stopLossPips': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
