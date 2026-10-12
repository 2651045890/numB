"""batch_012 port of 顺势而为的移动平均线交叉策略Going-with-the-Trend-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-17 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Glenn234\n\n//@version=5\nstrategy("MA cross strategy", shorttitle="macs", overlay=true)\n\n\n// Create indicator\'s\nshortSMA = ta.sma(close, 10)\nlongSMA = ta.sma(close, 30)\nrsi = ta.rsi(close, 14)\natr = ta.atr(14)\n\n\n// Crossover conditions\nlongCondition = ta.crossover(shortSMA, longSMA)\nshortCondition = ta.crossunder(shortSMA, longSMA)\n\n\n// trade conditions\nif (longCondition)\n    stopLoss = low - atr * 2\n    takeProfit = high + atr * 2\n    strategy.entry("long", strategy.long, when = rsi > 50)\n    strategy.exit("exit", "long", stop=stopLoss, limit=takeProfit)\n\nif (shortCondition)\n    stopLoss = high + atr * 2\n    takeProfit = low - atr * 2\n    strategy.entry("short", strategy.short, when = rsi < 50)\n    strategy.exit("exit", "short", stop=stopLoss, limit=takeProfit)\n\n\n// Plot SMA to chart\nplot(shortSMA, color=color.red, title="Short SMA")\nplot(longSMA, color=color.green, title="Long SMA")\n'

class SMGoingwiththeTrendMovingAverageCrossoverStrategy9f2308(PinePortBase, IStrategy):
    source_id = "SM_9f23086fb6b52d64"
    source_file = '顺势而为的移动平均线交叉策略Going-with-the-Trend-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
