"""batch_011 port of 简单移动平均线金叉死叉策略Simple-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-14 00:00:00\nend: 2023-11-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © xyzdesign1989\n//@version=5\nstrategy("SMA crossover buy/sell [SCSM_Algo]", overlay=true, margin_long=3000, margin_short=3000)\n\n\nBuyCond = ta.crossover(ta.sma(close, 20), ta.sma(close, 50)) and ta.sma(close, 20) > ta.sma(close, 50) and  ta.sma(close, 50) > ta.sma(close, 100) and  ta.sma(close, 100) > ta.sma(close, 200) or (ta.crossover(ta.sma(close, 20), ta.sma(close, 100)) and ta.sma(close, 20) > ta.sma(close, 50))\nif (BuyCond)\n    strategy.entry("SCSM ? Buy", strategy.long)\n\nSellCond = ta.crossunder(ta.sma(close, 20), ta.sma(close, 50))\nif (SellCond)\n    strategy.entry("الحمد للہ،Sell", strategy.short)\n\nma(source, length, type) =>\n    type == "SMA" ? ta.sma(source, length) :\n     type == "EMA" ? ta.ema(source, length) :\n     type == "SMMA (RMA)" ? ta.rma(source, length) :\n     type == "WMA" ? ta.wma(source, length) :\n     type == "VWMA" ? ta.vwma(source, length) :\n     na\n\nshow_ma1   = input(true   , "MA №1", inline="MA #1")\nma1_type   = input.string("SMA"  , ""     , inline="MA #1", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nma1_source = input(close  , ""     , inline="MA #1")\nma1_length = input.int(20     , ""     , inline="MA #1", minval=1)\nma1_color  = input(#0929f6, ""     , inline="MA #1")\nma1 = ma(ma1_source, ma1_length, ma1_type)\nplot(show_ma1 ? ma1 : na, color = ma1_color, title="MA №1")\n\nshow_ma2   = input(true   , "MA №2", inline="MA #2")\nma2_type   = input.string("SMA"  , ""     , inline="MA #2", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nma2_source = input(close  , ""     , inline="MA #2")\nma2_length = input.int(50     , ""     , inline="MA #2", minval=1)\nma2_color  = input(#00fb04, ""     , inline="MA #2")\nma2 = ma(ma2_source, ma2_length, ma2_type)\nplot(show_ma2 ? ma2 : na, color = ma2_color, title="MA №2")\n\nshow_ma3   = input(true   , "MA №3", inline="MA #3")\nma3_type   = input.string("SMA"  , ""     , inline="MA #3", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nma3_source = input(close  , ""     , inline="MA #3")\nma3_length = input.int(100    , ""     , inline="MA #3", minval=1)\nma3_color  = input(#131313, ""     , inline="MA #3")\nma3 = ma(ma3_source, ma3_length, ma3_type)\nplot(show_ma3 ? ma3 : na, color = ma3_color, title="MA №3")\n\nshow_ma4   = input(true   , "MA №4", inline="MA #4")\nma4_type   = input.string("SMA"  , ""     , inline="MA #4", options=["SMA", "EMA", "SMMA (RMA)", "WMA", "VWMA"])\nma4_source = input(close  , ""     , inline="MA #4")\nma4_length = input.int(200    , ""     , inline="MA #4", minval=1)\nma4_color  = input(#f60c0c, ""     , inline="MA #4")\nma4 = ma(ma4_source, ma4_length, ma4_type)\nplot(show_ma4 ? ma4 : na, color = ma4_color, title="MA №4")'

class SM6EBBDC0C5BD8B735(PinePortBase, IStrategy):
    source_id = "SM_6ebbdc0c5bd8b735"
    source_file = '简单移动平均线金叉死叉策略Simple-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'show_ma1': True, 'ma1_type': 'SMA', 'ma1_length': 20, 'show_ma2': True, 'ma2_type': 'SMA', 'ma2_length': 50, 'show_ma3': True, 'ma3_type': 'SMA', 'ma3_length': 100, 'show_ma4': True, 'ma4_type': 'SMA', 'ma4_length': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
