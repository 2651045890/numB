"""batch_011 port of 超级趋势RSI与EMA交叉策略SuperTrend-RSI-EMA-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend, RSI, and EMA Strategy", overlay=true)\n\n// Supertrend Indicator\natrPeriod = input.int(10, "ATR Length", minval=1)\nfactor = input.float(3.0, "Factor", minval=0.01, step=0.01)\n[supertrend, direction] = ta.supertrend(factor, atrPeriod)\n\n// RSI Indicator\nrsiLength = input.int(14, "RSI Length")\nrsi = ta.rsi(close, rsiLength)\n\n// EMA Indicator\nemaLength = 9\nema = ta.ema(close, emaLength)\n\n// Entry Conditions\nlongCondition1 = close > supertrend and rsi > 70\nlongCondition2 = close > ema\n\n// Combined Entry Condition\nlongCondition = longCondition1 and longCondition2\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Exit Condition\nexitCondition = close < supertrend\nif (exitCondition)\n    strategy.close("Long")\n\n'

class SME7F7AB6DBC5B62CD(PinePortBase, IStrategy):
    source_id = "SM_e7f7ab6dbc5b62cd"
    source_file = '超级趋势RSI与EMA交叉策略SuperTrend-RSI-EMA-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'atrPeriod': 10, 'factor': 3.0, 'rsiLength': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
