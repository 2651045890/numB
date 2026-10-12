"""batch_012 port of 高效趋势捕捉型指数移动平均线交叉与动态追踪止损策略-Advanced-Trend-Capture-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-03-08 00:00:00\nend: 2025-04-07 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("EMA Crossover (New Trailing Stop)", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=20, slippage=5)\n\n// Define EMA and SMA lengths\nshortEMALength = 13\nmidEMALength = 25\nlongEMALength = 33\nsma100Length = 100\nsma200Length = 200\n\n// Calculate EMAs\nshortEMA = ta.ema(close, shortEMALength)\nmidEMA = ta.ema(close, midEMALength)\nlongEMA = ta.ema(close, longEMALength)\n\n// Calculate SMAs\nsma100 = ta.sma(close, sma100Length)\nsma200 = ta.sma(close, sma200Length)\n\n// Plot EMAs and SMAs\nplot(shortEMA, title="13 EMA", color=color.blue)\nplot(midEMA, title="25 EMA", color=color.red)\nplot(longEMA, title="33 EMA", color=color.green)\nplot(sma100, title="100 SMA", color=color.purple)\nplot(sma200, title="200 SMA", color=color.orange)\n\n// ENTRY CONDITIONS\nlongCondition  = shortEMA >= longEMA and strategy.position_size <= 0\nshortCondition = shortEMA <= longEMA and strategy.position_size >= 0\n\n// EXIT CONDITIONS\nexitLong  = shortEMA < longEMA  // Exit long when 13 EMA falls below 33 EMA\nexitShort = shortEMA > midEMA   // Exit short when 13 EMA rises above 25 EMA\n\n// Flag to track if an exit has been processed\nvar bool isExiting = false\n\n// EXECUTE LONG\nif (longCondition and not isExiting)\n    strategy.close("Short", comment="Close Short for Long Entry")\n    strategy.entry("Long", strategy.long, alert_message="FAST Long Entry: 13 EMA >= 33 EMA")\n\n// EXECUTE SHORT\nif (shortCondition and not isExiting)\n    strategy.close("Long", comment="Close Long for Short Entry")\n    strategy.entry("Short", strategy.short, alert_message="FAST Short Entry: 13 EMA <= 33 EMA")\n\n// Trailing Stop Parameters\ntrailOffsetPts = 2\ntrail = 10\n\n// Trailing Stop for Longs\nif (strategy.position_size > 0 and not isExiting)\n    strategy.exit("Long Trail Exit", from_entry="Long", trail_offset=trailOffsetPts, trail_price=high - trail, comment="Long Trailing Stop")\n    isExiting := true\n\n// Trailing Stop for Shorts\nif (strategy.position_size < 0 and not isExiting)\n    strategy.exit("Short Trail Exit", from_entry="Short", trail_offset=trailOffsetPts, trail_price=low + trail, comment="Short Trailing Stop")\n    isExiting := true\n\n// EXIT STRATEGY\nif (exitLong and not isExiting)\n    strategy.close("Long", comment="Exit Long: 13 EMA < 33 EMA")\n    isExiting := true\n\nif (exitShort and not isExiting)\n    strategy.close("Short", comment="Exit Short: 13 EMA > 25 EMA")\n    isExiting := true\n\n// Reset the exit flag at the end of each bar\nif (barstate.isconfirmed)\n    isExiting := false\n\n'

class SMAdvancedTrendCaptureEMACrossoverStrategywithDynamicTrai30f41e(PinePortBase, IStrategy):
    source_id = "SM_30f41e2827271f08"
    source_file = '高效趋势捕捉型指数移动平均线交叉与动态追踪止损策略-Advanced-Trend-Capture-EMA-Crossover-Strategy-with-Dynamic-Trailing-Stop.md'
    timeframe = '1d'
    can_short = True
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
