"""batch_011 port of 移动平均交叉动态止盈止损策略-Dynamic-Stop-Loss-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-09-24 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("RAMZY CRYPTO-KING", overlay=true)\n\n// Input for moving averages\nshortMA = input(9, title="Short EMA Period")\nlongMA = input(21, title="Long EMA Period")\ntrailOffset = input(0, title="Trailing Drawdown Offset")\n\n// Calculate moving averages\nshortEMA = ta.ema(close, shortMA)\nlongEMA = ta.ema(close, longMA)\n\n// Plot moving averages\nplot(shortEMA, color=color.blue, title="Short EMA")\nplot(longEMA, color=color.red, title="Long EMA")\n\n// Identify recent swing high and low\nswingHigh = ta.highest(high, 5)\nswingLow = ta.lowest(low, 5)\n\n// Buy condition: EMA crossover\nlongCondition = ta.crossover(shortEMA, longEMA)\nif (longCondition)\n    strategy.close("Short")  // Close any existing short position\n    stopLoss = swingLow  // At swing low\n    takeProfit = close + (3 * (close - stopLoss))  // 1:3 RR\n    strategy.entry("Long", strategy.long)\n    strategy.exit("TP/SL", "Long", limit=takeProfit, stop=stopLoss, trail_offset=trailOffset)\n\n// Sell condition: EMA crossover\nshortCondition = ta.crossunder(shortEMA, longEMA)\nif (shortCondition)\n    strategy.close("Long")  // Close any existing long position\n    stopLoss = swingHigh  // At swing high\n    takeProfit = close - (3 * (stopLoss - close))  // 1:3 RR\n    strategy.entry("Short", strategy.short)\n    strategy.exit("TP/SL", "Short", limit=takeProfit, stop=stopLoss, trail_offset=trailOffset)\n\n// Debugging Labels\nif (longCondition)\n    label.new(bar_index, high, "Buy", style=label.style_label_down, color=color.green, textcolor=color.white)\n\nif (shortCondition)\n    label.new(bar_index, low, "Sell", style=label.style_label_up, color=color.red, textcolor=color.white)\n'

class SMC312624F51654C82(PinePortBase, IStrategy):
    source_id = "SM_c312624f51654c82"
    source_file = '移动平均交叉动态止盈止损策略-Dynamic-Stop-Loss-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'shortMA': 9, 'longMA': 21, 'trailOffset': 0}
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
