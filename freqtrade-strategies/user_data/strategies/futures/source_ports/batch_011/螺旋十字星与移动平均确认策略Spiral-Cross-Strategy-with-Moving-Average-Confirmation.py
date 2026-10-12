"""batch_011 port of 螺旋十字星与移动平均确认策略Spiral-Cross-Strategy-with-Moving-Average-Confirmation.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-01 00:00:00\nend: 2024-02-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © DraftVenture\n\n//@version=5\nstrategy("Vortex + Moving Average Strategy", overlay=true)\n\n//Vortex settings\nperiod_ = input.int(14, title="Vortex Length", minval=2)\nVMP = math.sum( math.abs( high - low[1]), period_ )\nVMM = math.sum( math.abs( low - high[1]), period_ )\nSTR = math.sum( ta.atr(1), period_ )\nVIP = VMP / STR\nVIM = VMM / STR\nplot(VIP, title="VI +", color=color.white)\nplot(VIM, title="VI -", color=color.white)\n\nlen = input.int(9, minval=1, title="MA Length")\nsrc = input(close, title="Source")\noffset = input.int(title="Offset", defval=0, minval=-500, maxval=500)\nout = ta.sma(src, len)\nplot(out, color=color.blue, title="MA", offset=offset)\n\nma(source, length, type) =>\n    switch type\n        "SMA" => ta.sma(source, length)\n        "EMA" => ta.ema(source, length)\n        "SMMA (RMA)" => ta.rma(source, length)\n        "WMA" => ta.wma(source, length)\n        "VWMA" => ta.vwma(source, length)\n\ntypeMA = input.string(title = "Method", defval = "SMA", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"], group="Smoothing")\nsmoothingLength = input.int(title = "Length", defval = 5, minval = 1, maxval = 100, group="Smoothing")\n\nsmoothingLine = ma(out, smoothingLength, typeMA)\nplot(smoothingLine, title="Smoothing Line", color=#f37f20, offset=offset, display=display.none)\n\n// Determine long and short conditions\nlongCondition = ta.crossover(VIP, VIM) and close > smoothingLine\nshortCondition = ta.crossunder(VIP, VIM) and close < smoothingLine\ncrossCondition = ta.crossunder(VIP, VIM) or ta.crossunder(VIM, VIP)\n\n// Strategy entry and exit logic\nif longCondition\n    strategy.entry("Long", strategy.long)\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\n\nbgcolor(crossCondition ? color.new(color.white, 80) : na)\n\n// Strategy by KP'

class SM137A1CC4FCAFEEAC(PinePortBase, IStrategy):
    source_id = "SM_137a1cc4fcafeeac"
    source_file = '螺旋十字星与移动平均确认策略Spiral-Cross-Strategy-with-Moving-Average-Confirmation.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'period_': 14, 'len': 9, 'offset': 0, 'typeMA': 'SMA', 'smoothingLength': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'switch']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
