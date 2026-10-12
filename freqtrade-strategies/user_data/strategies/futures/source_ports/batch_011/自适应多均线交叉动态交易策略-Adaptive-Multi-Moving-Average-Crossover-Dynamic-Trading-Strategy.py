"""batch_011 port of 自适应多均线交叉动态交易策略-Adaptive-Multi-Moving-Average-Crossover-Dynamic-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n//@version=5\nstrategy("Two Pick-Your-Moving-Averages Crossover Strategy", overlay=true, margin_long=100, margin_short=100)\nallowShorting = input.bool(true, "Allow Shorting")\nfastMALength = input.int(14, "Fast MA Length")\nslowMALength = input.int(28, "Slow MA Length")\nfastMAType = input.string("Simple", "Fast MA Type", ["Simple", "Exponential", "Weighted", "Relative"])\nslowMAType = input.string("Simple", "Slow MA Type", ["Simple", "Exponential", "Weighted", "Relative"]) \n\nfloat fastMA = switch fastMAType\n    "Simple" => ta.sma(close, fastMALength)\n    "Exponential" => ta.ema(close, fastMALength)\n    "Weighted" => ta.wma(close, fastMALength)\n    "Relative" => ta.rma(close, fastMALength)\n\nplot(fastMA, color = color.aqua, linewidth = 2)\n\nfloat slowMA = switch slowMAType\n    "Simple" => ta.sma(close, slowMALength)\n    "Exponential" => ta.ema(close, slowMALength)\n    "Weighted" => ta.wma(close, slowMALength)\n    "Relative" => ta.rma(close, slowMALength)\n\nplot(slowMA, color = color.blue, linewidth = 2)\n\nlongCondition = ta.crossover(fastMA, slowMA)\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = ta.crossunder(fastMA, slowMA) and allowShorting\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\ncloseCondition = ta.crossunder(fastMA, slowMA) and not allowShorting\nif (closeCondition)\n    strategy.close("Long", "Close")\n'

class SM34D88F0D48D3A04F(PinePortBase, IStrategy):
    source_id = "SM_34d88f0d48d3a04f"
    source_file = '自适应多均线交叉动态交易策略-Adaptive-Multi-Moving-Average-Crossover-Dynamic-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'allowShorting': True, 'fastMALength': 14, 'slowMALength': 28, 'fastMAType': 'Simple', 'slowMAType': 'Simple'}
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
