"""batch_012 port of 零延迟移动平均趋势交叉策略Zero-Lag-Moving-Average-Trend-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-06 00:00:00\nend: 2025-03-04 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"SOL_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ChartPrime\n\n//@version=5\nstrategy("Zero-Lag MA Trend Strategy", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 10)\n\n// --------------------------------------------------------------------------------------------------------------------}\n// ???? ??????\n// --------------------------------------------------------------------------------------------------------------------{\nint  length    = input.int(15, title="Length") // Length for moving averages\n\n// Colors for visualization\ncolor up = input.color(#30d453, "+", group = "Colors", inline = "i")\ncolor dn = input.color(#4043f1, "-", group = "Colors", inline = "i")\n\n// --------------------------------------------------------------------------------------------------------------------}\n// ????????? ????????????\n// --------------------------------------------------------------------------------------------------------------------{\nemaValue   = ta.ema(close, length) // EMA\ncorrection = close + (close - emaValue) // Correction factor\nzlma       = ta.ema(correction, length) // Zero-Lag Moving Average (ZLMA)\n\n// Entry signals\nlongSignal  = ta.crossover(zlma, emaValue) // Bullish crossover\nshortSignal = ta.crossunder(zlma, emaValue) // Bearish crossunder\n// Close positions before the market closes\nvar int marketCloseHour = 15\nvar int marketCloseMinute = 45\ntimeToClose = hour == marketCloseHour and minute >= marketCloseMinute\n// --------------------------------------------------------------------------------------------------------------------}\n// ????? ?????????\n// --------------------------------------------------------------------------------------------------------------------{\nif longSignal\n    strategy.entry("Long", strategy.long)\n\nif shortSignal\n    strategy.close("Long")\n\nif timeToClose\n    strategy.close_all("EOD Exit")\n// --------------------------------------------------------------------------------------------------------------------}\n// ?????????????\n// --------------------------------------------------------------------------------------------------------------------{\n// Plot the Zero-Lag Moving Average and EMA\nplot(zlma, color = zlma > zlma[3] ? up : dn, linewidth = 2, title = "ZLMA")\nplot(emaValue, color = emaValue < zlma ? up : dn, linewidth = 2, title = "EMA")\n\n// Mark trade entries with shapes\nplotshape(series=longSignal, location=location.belowbar, color=up, style=shape.labelup, title="Buy Signal")\nplotshape(series=shortSignal, location=location.abovebar, color=dn, style=shape.labeldown, title="Sell Signal")\n\n'

class SMZeroLagMovingAverageTrendCrossoverStrategy1da5a1(PinePortBase, IStrategy):
    source_id = "SM_1da5a1b638fe4894"
    source_file = '零延迟移动平均趋势交叉策略Zero-Lag-Moving-Average-Trend-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
