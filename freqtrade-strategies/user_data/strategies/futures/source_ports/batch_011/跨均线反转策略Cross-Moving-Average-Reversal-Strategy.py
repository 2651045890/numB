"""batch_011 port of 跨均线反转策略Cross-Moving-Average-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-19 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 2d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Valeria 181 Bot Strategy Mejorado 2.21", overlay=true, margin_long=100, margin_short=100)\n \nvar float lastLongOrderPrice = na\nvar float lastShortOrderPrice = na\n\nlongCondition = ta.crossover(ta.sma(close, 1), ta.sma(close, 5))\nif (longCondition)\n    strategy.entry("Long Entry", strategy.long)  // Enter long\n\nshortCondition = ta.crossunder(ta.sma(close, 1), ta.sma(close, 5))\nif (shortCondition)\n    strategy.entry("Short Entry", strategy.short)  // Enter short\n\nif (longCondition)\n    lastLongOrderPrice := close\n\nif (shortCondition)\n    lastShortOrderPrice := close\n\n// Calculate stop loss and take profit based on the last executed order\'s price\nstopLossLong = lastLongOrderPrice - 5  // 10 USDT lower than the last long order price\ntakeProfitLong = lastLongOrderPrice + 151  // 100 USDT higher than the last long order price\nstopLossShort = lastShortOrderPrice + 5  // 10 USDT higher than the last short order price\ntakeProfitShort = lastShortOrderPrice - 150  // 100 USDT lower than the last short order price\n\n// Apply stop loss and take profit to long positions\nstrategy.exit("Long Exit", from_entry="Long Entry", stop=stopLossLong, limit=takeProfitLong)\n\n// Apply stop loss and take profit to short positions\nstrategy.exit("Short Exit", from_entry="Short Entry", stop=stopLossShort, limit=takeProfitShort)'

class SMD595E5373311FC24(PinePortBase, IStrategy):
    source_id = "SM_d595e5373311fc24"
    source_file = '跨均线反转策略Cross-Moving-Average-Reversal-Strategy.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
