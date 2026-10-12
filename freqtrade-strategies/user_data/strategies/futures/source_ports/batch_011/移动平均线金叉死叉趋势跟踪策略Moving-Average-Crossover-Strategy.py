"""batch_011 port of 移动平均线金叉死叉趋势跟踪策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-01 00:00:00\nend: 2023-12-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Astorhsu\n\n//@version=5\nstrategy("Astor SMA20/60 TW", overlay=true, margin_long=100, margin_short=100)\nbacktest_year = input(2018, title=\'backtest_year\') //回測開始年分\nbacktest_month = input.int(01, title=\'backtest_month\', minval=1, maxval=12) //回測開始月份\nbacktest_day = input.int(01, title=\'backtest_day\', minval=1, maxval=31)  //回測開始日期\nstart_time = timestamp(backtest_year, backtest_month, backtest_day, 00, 00)  //回測開始的時間函數\n\n//Indicators\nsma20 = ta.sma(close,20)\nsma60 = ta.sma(close,60)\nplot(sma20, color=color.green, title="sma(20)")\nplot(sma60, color=color.red, title="sma(60)")\n\n//進場條件\nlongCondition = ta.crossover(close, ta.sma(close, 20))\nif (longCondition) and time >= start_time\n    strategy.entry("open long20", strategy.long, qty=1, comment="站上m20做多")\n\n\nshortCondition = ta.crossunder(close, ta.sma(close, 20))\nif (shortCondition) and time >= start_time\n    strategy.close("open long20",comment="跌破m20平倉", qty=1)     \n    \nlongCondition1 = ta.crossover(close, ta.sma(close, 60))\nif (longCondition1) and time >= start_time\n    strategy.entry("open long60", strategy.long, qty=1, comment="站上m60做多")\n\n\nshortCondition1 = ta.crossunder(close, ta.sma(close, 60))\nif (shortCondition1) and time >= start_time\n    strategy.close("open long60",comment="跌破m60平倉", qty=1)     '

class SM01FE10BC018587CA(PinePortBase, IStrategy):
    source_id = "SM_01fe10bc018587ca"
    source_file = '移动平均线金叉死叉趋势跟踪策略Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'backtest_year': 2018}
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
