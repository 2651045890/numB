"""batch_011 port of 轨迹追踪指数移动均线策略Trend-Following-Exponential-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-31 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © moondevonyt\n\n//@version=5\nstrategy("Cornoflower Trend Following Crypto", overlay=true)\n\n// Input Settings\nlenEma8 = input(8, title="Length of 8 EMA")\nlenEma12 = input(12, title="Length of 12 EMA")\nlenEma24 = input(24, title="Length of 24 EMA")\nlenEma72 = input(72, title="Length of 72 EMA")\n\n// Calculate the EMAs\nema8 = ta.ema(close, lenEma8)\nema12 = ta.ema(close, lenEma12)\nema24 = ta.ema(close, lenEma24)\nema72 = ta.ema(close, lenEma72)\n\n// Entry Conditions\npullbackEntry = ta.crossover(close, ema12) and ta.crossover(close, ema24) and ta.crossover(close, ema72)\ninitialEntry = ta.crossover(close, ema72) and ta.crossover(ema8, ema12) and ta.crossover(ema8, ema24)\n\n// Exit Conditions\nprofitTarget = 100 // Example target in pips, adjust according to your preference\ntrailingStop = 50 // Example trailing stop value in pips, adjust according to your preference\nexitCondition = ta.crossunder(ema12, ema24)\n\n// Execute Strategy\nif pullbackEntry\n    strategy.entry("Pullback Entry", strategy.long)\nif initialEntry\n    strategy.entry("Initial Entry", strategy.long)\n\nif strategy.position_size > 0\n    strategy.exit("Profit Target", "Pullback Entry", limit=close + (profitTarget * syminfo.mintick))\n    strategy.exit("Trailing Stop", "Pullback Entry", stop=close - (trailingStop * syminfo.mintick), trail_points=trailingStop)\n    strategy.exit("Exit Condition", "Initial Entry", stop=close, when=exitCondition)\n    \n// Plot EMAs\nplot(ema8, color=color.yellow, title="8 EMA", linewidth=1, style=plot.style_line)\nplot(ema12, color=color.purple, title="12 EMA", linewidth=1, style=plot.style_line)\nplot(ema24, color=color.blue, title="24 EMA", linewidth=1, style=plot.style_line)\nplot(ema72, color=color.rgb(235, 255, 59), title="72 EMA", linewidth=1, style=plot.style_line)'

class SM380A217EC2B276EC(PinePortBase, IStrategy):
    source_id = "SM_380a217ec2b276ec"
    source_file = '轨迹追踪指数移动均线策略Trend-Following-Exponential-Moving-Average-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'lenEma8': 8, 'lenEma12': 12, 'lenEma24': 24, 'lenEma72': 72}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
