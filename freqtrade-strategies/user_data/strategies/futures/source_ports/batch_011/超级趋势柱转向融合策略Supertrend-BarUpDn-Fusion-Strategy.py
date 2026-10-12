"""batch_011 port of 超级趋势柱转向融合策略Supertrend-BarUpDn-Fusion-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend and BarUpDn Indicator Fusion", overlay=true)\n\n// Supertrend indicator\natrLength = input(10, title="ATR Length")\nfactor = input(3.0, title="Factor")\n[supertrend, direction] = ta.supertrend(factor, atrLength)\nlastBar = 0\n\n// BarUpDn indicator\nbarUpDn = close > open and open > close[1] ? 1 : close < open and open < close[1] ? -1 : 0\n\nif (barUpDn == 1)\n    lastBar := 1\nelse if barUpDn == -1\n    lastBar := -1\n\n\n// Determine long or short position\nlongCondition = (direction > 0 and barUpDn > 0) or (direction > 0 and lastBar == 1)\nshortCondition = (direction < 0 and barUpDn < 0) or (direction < 0 and lastBar == -1)\n\n// Enter long or short position\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    lastBar := 1\nelse if (shortCondition)\n    strategy.entry("Short", strategy.short)\n    lastBar := -1\n\nif (direction < 0 and barUpDn > 0)\n    strategy.entry("Long", strategy.long)\n\n// Exit long or short position\nif (direction > 0 and barUpDn < 0)\n    strategy.entry("Short", strategy.short)\n\n// Exit long or short position\n// if (direction < 0 and barUpDn > 0 or direction > 0 and barUpDn < 0)\n//   strategy.close_all()\n'

class SM1D1C801175CC8BEF(PinePortBase, IStrategy):
    source_id = "SM_1d1c801175cc8bef"
    source_file = '超级趋势柱转向融合策略Supertrend-BarUpDn-Fusion-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrLength': 10, 'factor': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
