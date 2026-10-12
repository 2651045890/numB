"""batch_012 port of 追踪止损百分比策略Percentage-Trailing-Stop-Loss-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-08 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © osmaras\n// based on https://kodify.net/tradingview/orders/percentage-trail/\n\n//@version=5\nstrategy("Break even stop loss (% of instrument price)", overlay=true)\n\n// Configure trail stop level with input options (optional)\nlongTrailPerc = input.float(defval=3.0,step=0.1,title="Trail Long Loss (%)")* 0.01 \nlongCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))\n\n// Determine trail stop loss prices\nlongStopPrice = 0.0\nlastEntryPrice = strategy.opentrades.entry_price(strategy.opentrades - 1)\nlongStopPrice := if (strategy.position_size > 0 and close > (lastEntryPrice * (1 + longTrailPerc)))\n    stopValue = lastEntryPrice\n    math.max(stopValue, longStopPrice[1])\nelse\n    longStopPrice := if (strategy.position_size > 0)\n        stopValue = lastEntryPrice * (1 - longTrailPerc)\n        math.max(stopValue, longStopPrice[1])\n    else\n        0\n\n// Plot stop loss values for confirmation\nplot(series=(strategy.position_size > 0) ? longStopPrice : na,\n     color=color.fuchsia, style=plot.style_cross,\n     linewidth=2, title="Long Trail Stop")\n\n// set strategy only long\nstrategy.risk.allow_entry_in(strategy.direction.long)\n\n// Submit entry orders\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))\nif (shortCondition)\n    strategy.close("Long")\n\n\n// Submit exit orders for trail stop loss price\nif (strategy.position_size > 0)\n    strategy.exit(id="Stop Loss", stop=longStopPrice)\n\n\n'

class SMPercentageTrailingStopLossStrategy3e1c1b(PinePortBase, IStrategy):
    source_id = "SM_3e1c1b00957ca6c4"
    source_file = '追踪止损百分比策略Percentage-Trailing-Stop-Loss-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
