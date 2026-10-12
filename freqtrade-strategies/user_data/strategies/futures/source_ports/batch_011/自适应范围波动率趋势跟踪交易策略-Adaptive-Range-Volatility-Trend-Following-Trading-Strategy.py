"""batch_011 port of 自适应范围波动率趋势跟踪交易策略-Adaptive-Range-Volatility-Trend-Following-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-28 00:00:00\nend: 2024-11-27 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("ASCTrend", shorttitle="ASCTrend", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\neternalfg = input(false, title="eternal 確定")\neternal = eternalfg ? 1 : 0\nASClength = input.int(title="ASC Length", minval=4, defval=10)\nRISK = input.int(title="RISK", minval=0, defval=3)\n\n// Custom sum function\ncustomSum(source, length) =>\n    sum = 0.0\n    for i = 0 to length - 1\n        sum := sum + source[i]\n    sum\n\nx1 = 67 + RISK\nx2 = 33 - RISK\nRange = ta.highest(ASClength) - ta.lowest(ASClength)\nAvgRange = ta.sma(Range, ASClength)\nCountFg = math.abs(open - close) >= AvgRange * 2.0 ? 1 : 0\nTrueCount = customSum(CountFg, ASClength)\nCountFg2 = math.abs(close[3] - close) >= AvgRange * 4.6 ? 1 : 0\nTrueCount2 = customSum(CountFg2, ASClength - 3)\nwpr3RR = ta.wpr(3 + RISK + RISK)\nwpr3 = ta.wpr(3)\nwpr4 = ta.wpr(4)\nWprAbs = 100 + (TrueCount2 > 0 ? wpr4 : TrueCount > 0 ? wpr3 : wpr3RR)\nASC_Trend = 0\nASC_Trend := WprAbs[eternal] < x2[eternal] ? -1 : WprAbs[eternal] > x1[eternal] ? 1 : ASC_Trend[1]\n\nif (ta.crossover(ASC_Trend, 0))\n    strategy.entry("Long", strategy.long)\n\nif (ta.crossunder(ASC_Trend, 0))\n    strategy.entry("Short", strategy.short)\n\nplotshape(ta.crossover(ASC_Trend, 0), location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small, text="B", textcolor=color.white)\nplotshape(ta.crossunder(ASC_Trend, 0), location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small, text="S", textcolor=color.white)\n\nalertcondition(ta.crossover(ASC_Trend, 0), title="ASC_Trend UP", message="ASC_Trend UP")\nalertcondition(ta.crossunder(ASC_Trend, 0), title="ASC_Trend Down", message="ASC_Trend Down")'

class SM9129ACAE32BE7E0C(PinePortBase, IStrategy):
    source_id = "SM_9129acae32be7e0c"
    source_file = '自适应范围波动率趋势跟踪交易策略-Adaptive-Range-Volatility-Trend-Following-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'eternalfg': False, 'ASClength': 10, 'RISK': 3}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
