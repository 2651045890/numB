"""batch_011 port of 突破EMA滑动止损三角策略Elevated-Touch-Short-Triangle-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-30 00:00:00\nend: 2024-02-29 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Short Entry EMA Strategy with Visual SL and TP", shorttitle="SE-EMA-SL-TP-Viz", overlay=true)\n\n// Customization Inputs\nemaPeriod = input.int(5, title="EMA Period", minval=1)\n\n// EMA Calculation\nemaValue = ta.ema(close, emaPeriod)\nplot(emaValue, title="5 EMA", color=color.blue)\n\n// Detecting Short Entry Conditions\nshortEntryCondition = close > emaValue and low <= emaValue and low[1] > emaValue[1] and close[1] > emaValue[1]\n\n// Entry, SL, and TP Logic\nif (shortEntryCondition)\n    entryPrice = open[1]\n    slLevel = high[1]\n    risk = slLevel - entryPrice\n    tpLevel = entryPrice - risk * 3  // Assuming a 2:1 risk-reward ratio for TP calculation\n\n    // Execute short trade\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit", "Short", stop=slLevel, limit=tpLevel)\n\n    // Visualizing SL and TP levels\n    // line.new(bar_index, slLevel, bar_index + 20, slLevel, color=color.red, width=2)\n    // line.new(bar_index, tpLevel, bar_index + 20, tpLevel, color=color.green, width=2)\n\n// Plotting Short Entry Signal\nplotshape(series=shortEntryCondition, style=shape.triangledown, location=location.abovebar, color=color.red, title="Short Signal")\n'

class SM9D3D5B4B6F5E5AD1(PinePortBase, IStrategy):
    source_id = "SM_9d3d5b4b6f5e5ad1"
    source_file = '突破EMA滑动止损三角策略Elevated-Touch-Short-Triangle-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'emaPeriod': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
