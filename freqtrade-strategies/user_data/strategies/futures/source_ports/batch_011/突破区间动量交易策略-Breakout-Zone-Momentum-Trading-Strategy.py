"""batch_011 port of 突破区间动量交易策略-Breakout-Zone-Momentum-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Breaker Blocks with Buy and Sell Signals", overlay=true)\n\n// Define the lookback period for breaker blocks\nbreakerPeriod = input.int(20, title="Breaker Block Lookback Period")\n\n// Calculate breaker blocks\nbreakerBlockSupport = ta.lowest(low, breakerPeriod)\nbreakerBlockResistance = ta.highest(high, breakerPeriod)\n\n// Buy and Sell Signals\nbuySignal = ta.crossover(close, ta.sma(close, 50))  // Example buy signal using SMA crossover\nsellSignal = ta.crossunder(close, ta.sma(close, 50))  // Example sell signal using SMA crossunder\n\n// Define the conditions for the strategy\nlongCondition = buySignal and close > breakerBlockSupport\nshortCondition = sellSignal and close < breakerBlockResistance\n\n// Plot breaker blocks\nplot(breakerBlockSupport, title="Breaker Block Support", color=color.green, linewidth=2)\nplot(breakerBlockResistance, title="Breaker Block Resistance", color=color.red, linewidth=2)\n\n// Plot buy and sell signals on the chart\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Strategy execution\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)'

class SME2718B36CBC79F35(PinePortBase, IStrategy):
    source_id = "SM_e2718b36cbc79f35"
    source_file = '突破区间动量交易策略-Breakout-Zone-Momentum-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'breakerPeriod': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
