"""batch_011 port of 突破均线交易策略Momentum-Breakout-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-27 00:00:00\nend: 2023-12-03 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("RSI, SuperTrend, and ATR Strategy", overlay=true)\n\n// Define input parameters\nrsiLength1 = input(14, title="RSI Length 1")\nrsiLength2 = input(21, title="RSI Length 2")\nsupertrendMultiplier = input(1.5, title="SuperTrend Multiplier")\n\n// Calculate indicators\nrsi1 = ta.rsi(close, rsiLength1)\nrsi2 = ta.rsi(close, rsiLength2)\nsupertrend = ta.atr(14) * supertrendMultiplier\n\n// Define trading conditions\nrsiLongCondition = rsi1 > rsi2\nrsiShortCondition = rsi1 < rsi2\nsupertrendLongCondition = close > supertrend\nsupertrendShortCondition = close < supertrend\n\n// Execute trades\nif (rsiLongCondition and supertrendLongCondition)\n    strategy.entry("Long", strategy.long)\n\nif (rsiShortCondition and supertrendShortCondition)\n    strategy.entry("Short", strategy.short)\n\nif (strategy.position_size > 0 and (rsiShortCondition or supertrendShortCondition))\n    strategy.close("Long")\n\nif (strategy.position_size < 0 and (rsiLongCondition or supertrendLongCondition))\n    strategy.close("Short")\n\n// Plot indicators on the chart\nplot(rsi1, color=color.orange, title="RSI 1")\nplot(rsi2, color=color.yellow, title="RSI 2")\nplot(supertrend, color=color.blue, title="SuperTrend")\n'

class SM2A310A8EB6DF2802(PinePortBase, IStrategy):
    source_id = "SM_2a310a8eb6df2802"
    source_file = '突破均线交易策略Momentum-Breakout-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rsiLength1': 14, 'rsiLength2': 21, 'supertrendMultiplier': 1.5}
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
