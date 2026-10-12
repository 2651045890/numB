"""batch_012 port of 运用布林带突破整合策略Consolidation-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Consolidation Breakout Strategy", shorttitle="CBS", overlay=true)\n\n// Parameters\nlength = input(20, title="Bollinger Bands Length")\nmult = input(2.0, title="Bollinger Bands Multiplier")\nrisk = input.float(1, title="Risk per Trade (%)") / 100\n\n// Calculate Bollinger Bands\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\nupper = basis + dev\nlower = basis - dev\n\n// Entry Conditions\nconsolidating = ta.crossover(close, upper) and ta.crossunder(close, lower)\n\n// Exit Conditions\nbreakout = ta.crossover(close, upper) or ta.crossunder(close, lower)\n\n// Risk Management\natrVal = ta.atr(14)\nstopLoss = atrVal * input.float(2, title="Stop Loss Multiplier", minval=0.1, maxval=5)\n\n// Entry and Exit Conditions\nlongEntry = breakout and close > upper\nshortEntry = breakout and close < lower\n\nif (longEntry)\n    strategy.entry("Long", strategy.long)\n\nif (shortEntry)\n    strategy.entry("Short", strategy.short)\n\nif (longEntry and close < basis - stopLoss)\n    strategy.close("Long Exit")\n\nif (shortEntry and close > basis + stopLoss)\n    strategy.close("Short Exit")\n\n// Plot Entry and Exit Points\nplotshape(consolidating, style=shape.triangleup, location=location.belowbar, color=color.rgb(30, 255, 0), title="Entry Signal")\nplotshape(breakout, style=shape.triangledown, location=location.abovebar, color=color.rgb(255, 0, 0), title="Exit Signal")\n\n\n'

class SMConsolidationBreakoutStrategy562725(PinePortBase, IStrategy):
    source_id = "SM_562725b5e23cd80c"
    source_file = '运用布林带突破整合策略Consolidation-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
