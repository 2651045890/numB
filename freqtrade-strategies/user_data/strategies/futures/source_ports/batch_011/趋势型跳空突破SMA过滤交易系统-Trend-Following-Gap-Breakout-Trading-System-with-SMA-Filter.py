"""batch_011 port of 趋势型跳空突破SMA过滤交易系统-Trend-Following-Gap-Breakout-Trading-System-with-SMA-Filter.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Simplified Gap Strategy with SMA Filter", overlay=true)\n\n// Input fields for user control\nlong_gap_threshold = input.float(0.1, title="Gap Threshold (%)", minval=0.01, step=0.01)  // Minimum percentage for gaps\nhold_duration = input.int(10, title="Hold Duration (bars)", minval=1)  // Duration to hold the position\ngap_trade_option = input.string("Long Up Gap", title="Select Trade Option", options=["Long Up Gap", "Short Down Gap", "Short Up Gap", "Long Down Gap"])  // Combined option\nuse_sma_filter = input.bool(false, title="Use SMA Filter")  // Checkbox to activate SMA filter\nsma_length = input.int(200, title="SMA Length", minval=1)  // Length of the SMA\n\n// RGB color definitions for background\ncolor_up_gap = color.new(color.green, 50)    // Green background for up gaps\ncolor_down_gap = color.new(color.red, 50)    // Red background for down gaps\n\n// Gap size calculation in percentage terms\ngap_size = (open - close[1]) / close[1] * 100  // Gap size in percentage\n\n// Calculate gaps based on threshold input\nup_gap = open > close[1] and gap_size >= long_gap_threshold  // Long gap condition\ndown_gap = open < close[1] and math.abs(gap_size) >= long_gap_threshold  // Short gap condition\n\n// Calculate the SMA\nsma_value = ta.sma(close, sma_length)\n\n// Define the trading logic based on selected option and SMA filter\nif (gap_trade_option == "Long Up Gap" and up_gap and (not use_sma_filter or close > sma_value))\n    strategy.entry("Long", strategy.long)\nif (gap_trade_option == "Short Down Gap" and down_gap and (not use_sma_filter or close < sma_value))\n    strategy.entry("Short", strategy.short)\nif (gap_trade_option == "Short Up Gap" and up_gap and (not use_sma_filter or close < sma_value))\n    strategy.entry("Short", strategy.short)\nif (gap_trade_option == "Long Down Gap" and down_gap and (not use_sma_filter or close > sma_value))\n    strategy.entry("Long", strategy.long)\n\n// Exit position after the hold duration\nif (strategy.opentrades > 0)\n    if (bar_index - strategy.opentrades.entry_bar_index(0) >= hold_duration)\n        strategy.close("Long")\n        strategy.close("Short")\n\n// Background coloring to highlight gaps on the chart\nbgcolor((gap_trade_option == "Long Up Gap" and up_gap) ? color_up_gap : na, title="Up Gap Background")\nbgcolor((gap_trade_option == "Short Down Gap" and down_gap) ? color_down_gap : na, title="Down Gap Background")\nbgcolor((gap_trade_option == "Short Up Gap" and up_gap) ? color_down_gap : na, title="Short Up Gap Background")\nbgcolor((gap_trade_option == "Long Down Gap" and down_gap) ? color_up_gap : na, title="Long Down Gap Background")\n\n// Plot the SMA for visualization\nplot(use_sma_filter ? sma_value : na, color=color.white, title="SMA", linewidth=1)\n'

class SM8513F81778E87808(PinePortBase, IStrategy):
    source_id = "SM_8513f81778e87808"
    source_file = '趋势型跳空突破SMA过滤交易系统-Trend-Following-Gap-Breakout-Trading-System-with-SMA-Filter.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'long_gap_threshold': 0.1, 'hold_duration': 10, 'gap_trade_option': 'Long Up Gap', 'use_sma_filter': False, 'sma_length': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
