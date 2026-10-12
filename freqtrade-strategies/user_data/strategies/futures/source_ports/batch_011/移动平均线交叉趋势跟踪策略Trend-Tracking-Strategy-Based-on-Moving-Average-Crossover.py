"""batch_011 port of 移动平均线交叉趋势跟踪策略Trend-Tracking-Strategy-Based-on-Moving-Average-Crossover.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-06 00:00:00\nend: 2024-02-05 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Ravikant_sharma\n\n//@version=5\n\nstrategy(\'new\', overlay=true)\n\nstart = timestamp(1990, 1, 1, 0, 0)\nend = timestamp(2023, 12, 12, 23, 59)\nema0 = ta.ema(close, 9)\nema1 = ta.ema(close, 21)\nema2 = ta.ema(close, 51)\nema3 = ta.ema(close, 100)\nema4 = ta.ema(close, 200)\n\nrsi2=ta.rsi(ta.sma(close,14),14)\nplot(ema0, \'9\', color.new(color.green, 0))\nplot(ema1, \'21\', color.new(color.black, 0))\nplot(ema2, \'51\', color.new(color.red, 0))\nplot(ema3, \'200\', color.new(color.blue, 0))   \n\n//plot(ema4, \'100\', color.new(color.gray, 0)) \n\n\n//LongEntry = (  ta.crossover(ema0,ema3)  or  ta.crossover(ema0,ema2) or  ta.crossunder(ema2,ema3) ) // ta.crossover(ema0,ema1) //\nLongEntry=false\nif ta.crossover(ema0,ema1) \n    if rsi2>65\n        LongEntry:=true\nif ta.crossover(ema1,ema2)\n    if rsi2>65\n        LongEntry:=true\n        \nLongExit =  ta.crossunder(ema0,ema2) or close >(strategy.position_avg_price*1.25) or rsi2 <40 or close < (strategy.position_avg_price*0.98)\n\n\n\nif true\n    if(LongEntry and rsi2>60)\n        strategy.entry(\'Long\', strategy.long, 1)\n    if(LongExit)\n        strategy.close(\'Long\') \n\n'

class SM4C1333DAD6B4F4EC(PinePortBase, IStrategy):
    source_id = "SM_4c1333dad6b4f4ec"
    source_file = '移动平均线交叉趋势跟踪策略Trend-Tracking-Strategy-Based-on-Moving-Average-Crossover.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
