"""batch_011 port of 移动平均线交叉指标与反转指标组合策略Moving-Average-Crossover-and-Reversal-Indicator-Combination-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-06 00:00:00\nend: 2023-12-12 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © SuchitRaju\n\n//@version=4\nstrategy("MA RSI CCI")\n\nprice_up = if(close > open and close > sma(hl2,14))\n    1\nelse\n    0\n\nprice_down = if(open > close and close < sma(hl2,14))\n    1\nelse\n    0\n// \n\ncci_indicator = cci(hl2, 14)\n// plot(cci_indicator, color=color.blue)\n\nrsi_slow = sma(rsi(close, 14), 50)\n// plot(rsi_slow, color=color.red)\n\nrsi_fast = rsi(close, 14)\n// plot(rsi_fast, color=color.green)\n\nisCrossover = if(rsi_fast > rsi_slow and cci_indicator > 0)\n    1\nelse\n    0\n// plotshape(isCrossover, style = shape.arrowup, color = color.green, size = size.huge)\n\nisCrossunder = if(rsi_fast < rsi_slow and cci_indicator < 0)\n    1\nelse\n    0\n// plotshape(isCrossunder, style = shape.arrowup, color = color.red, size = size.huge)\n\n// start = timestamp("GMT-5", 2016,9,1,0,0)\n// end = timestamp("GMT-5", 2017,9,1,0,0)\n\n// strategy.entry("Long", strategy.long, 1, when = isCrossover and price_up)\n// strategy.entry("Short", strategy.short, 1, when = isCrossunder and price_down)\n// strategy.close("Long", when = isCrossunder and price_down)\n// strategy.close("Short", when = isCrossover and price_up)\n\nstrategy.entry("Long", strategy.long, 1, when = isCrossover)\nstrategy.entry("Short", strategy.short, 1, when = isCrossunder)\nstrategy.close("Long", when = isCrossunder)\nstrategy.close("Short", when = isCrossover)'

class SMED5BFEAC05CE2CD8(PinePortBase, IStrategy):
    source_id = "SM_ed5bfeac05ce2cd8"
    source_file = '移动平均线交叉指标与反转指标组合策略Moving-Average-Crossover-and-Reversal-Indicator-Combination-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
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
