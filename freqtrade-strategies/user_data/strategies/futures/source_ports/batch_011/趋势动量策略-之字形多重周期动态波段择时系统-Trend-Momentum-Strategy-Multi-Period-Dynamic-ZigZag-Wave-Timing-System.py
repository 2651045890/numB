"""batch_011 port of 趋势动量策略-之字形多重周期动态波段择时系统-Trend-Momentum-Strategy-Multi-Period-Dynamic-ZigZag-Wave-Timing-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-18 00:00:00\nend: 2025-02-15 08:00:00\nperiod: 2d\nbasePeriod: 2d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Zig Zag + Williams %R Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=300)\n\n// ====================\n// === Parameters\n// ====================\n\n// Zig Zag parameters\nzigzag_depth = input.int(5, title="Zig Zag Depth", minval=1)\nzigzag_deviation = input.float(1.0, title="Zig Zag Deviation (%)", minval=0.1, step=0.1)\n\n// Williams %R parameters\nwilliams_length = input.int(14, title="Williams %R Length", minval=1)\nwilliams_overbought = input.int(-20, title="Williams %R Overbought", minval=-100, maxval=0)\nwilliams_oversold = input.int(-80, title="Williams %R Oversold", minval=-100, maxval=0)\n\n// ====================\n// === Zig Zag Calculation\n// ====================\n\n// Initialize variables\nvar float last_pivot_high = na\nvar float last_pivot_low = na\nvar int zz_dir = 0  // 1 for uptrend, -1 for downtrend\n\n// Calculate pivots\npivot_high = ta.pivothigh(high, zigzag_depth, zigzag_depth)\npivot_low = ta.pivotlow(low, zigzag_depth, zigzag_depth)\n\n// Update Zig Zag direction and last pivots with deviation\nif (not na(pivot_high))\n    if (zz_dir != -1)  // Only change to downtrend if not already in downtrend\n        if (na(last_pivot_high) or (high[zigzag_depth] > last_pivot_high * (1 + zigzag_deviation / 100)))\n            last_pivot_high := high[zigzag_depth]\n            zz_dir := -1\n            label.new(bar_index[zigzag_depth], high[zigzag_depth], text="PH", color=color.red, style=label.style_label_down)\n\nif (not na(pivot_low))\n    if (zz_dir != 1)  // Only change to uptrend if not already in uptrend\n        if (na(last_pivot_low) or (low[zigzag_depth] < last_pivot_low * (1 - zigzag_deviation / 100)))\n            last_pivot_low := low[zigzag_depth]\n            zz_dir := 1\n            label.new(bar_index[zigzag_depth], low[zigzag_depth], text="PL", color=color.green, style=label.style_label_up)\n\n// ====================\n// === Williams %R Calculation\n// ====================\n\n// Calculate Williams %R manually\nhighest_high = ta.highest(high, williams_length)\nlowest_low = ta.lowest(low, williams_length)\nwilliams_r = (highest_high - close) / (highest_high - lowest_low) * -100\n\n// ====================\n// === Trade Conditions\n// ====================\n\n// Assign crossover and crossunder results to variables\ncrossover_williams = ta.crossover(williams_r, williams_oversold)\ncrossunder_williams = ta.crossunder(williams_r, williams_overbought)\n\n// Define trade conditions\nlongCondition = (zz_dir == 1) and crossover_williams\nshortCondition = (zz_dir == -1) and crossunder_williams\n\n// ====================\n// === Trading\n// ====================\n\n// Enter Long\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    label.new(bar_index, low, text="BUY", color=color.green, style=label.style_label_up)\n\n// Enter Short\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    label.new(bar_index, high, text="SELL", color=color.red, style=label.style_label_down)\n\n// ====================\n// === Visualization\n// ====================\n\n// Plot Zig Zag pivot shapes\nplotshape(series=(not na(pivot_high) and high[zigzag_depth] == last_pivot_high), title="Swing High", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small, text="ZZ High")\nplotshape(series=(not na(pivot_low) and low[zigzag_depth] == last_pivot_low), title="Swing Low", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small, text="ZZ Low")\n\n// Plot Williams %R\nhline(williams_overbought, "Overbought", color=color.red, linestyle=hline.style_dashed)\nhline(williams_oversold, "Oversold", color=color.green, linestyle=hline.style_dashed)\nplot(williams_r, title="Williams %R", color=color.blue)\n\n// Debug plot for Zig Zag direction\nplot(zz_dir, title="Zig Zag Direction", color=color.orange, linewidth=2)\n\n// ====================\n// === Risk Management\n// ====================\n\n// Risk parameters\nstop_loss_perc = input.float(1.0, title="Stop Loss (%)") / 100\ntake_profit_perc = input.float(2.0, title="Take Profit (%)") / 100\n\n// Stop Loss and Take Profit for Long\nif (longCondition)\n    strategy.exit("Long Exit", from_entry="Long", stop=close * (1 - stop_loss_perc), limit=close * (1 + take_profit_perc))\n\n// Stop Loss and Take Profit for Short\nif (shortCondition)\n    strategy.exit("Short Exit", from_entry="Short", stop=close * (1 + stop_loss_perc), limit=close * (1 - take_profit_perc))\n'

class SME8CC5DC259C84B1E(PinePortBase, IStrategy):
    source_id = "SM_e8cc5dc259c84b1e"
    source_file = '趋势动量策略-之字形多重周期动态波段择时系统-Trend-Momentum-Strategy-Multi-Period-Dynamic-ZigZag-Wave-Timing-System.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'zigzag_depth': 5, 'zigzag_deviation': 1.0, 'williams_length': 14, 'williams_overbought': -20, 'williams_oversold': -80, 'stop_loss_perc': 1.0, 'take_profit_perc': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 300
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
