"""batch_012 port of 震荡型通道突破策略Oscillating-Channel-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-08 00:00:00\nend: 2023-11-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Copyright, 2022, Cache_that_pass.  You are free to use this script however you see fit and reproduce it in any manner.\n\n//@version=5\n\n            //////  Name the strategy between the 2 quotation marks.  Consider setting commission type and value in strategy header to match exchanges rates. //////\n\nstrategy("Oscillating SSL Channel Strategy", "O-SSL Strat", overlay=true, pyramiding=1, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, initial_capital = 100, calc_on_order_fills=true)\n\n\n\n            //////  Inputs and calculations used by script  //////\n\nperiod = input(title=\'Period\', defval=25)\nlen = input(title=\'Period\', defval=25)\nsmaHigh = ta.sma(high, len)\nsmaLow = ta.sma(low, len)\nHlv = int(na)\nHlv := close > smaHigh ? 1 : close < smaLow ? -1 : Hlv[1]\nsslDown = Hlv < 0 ? smaHigh : smaLow\nsslUp = Hlv < 0 ? smaLow : smaHigh\n\n            //////  Show me the money  //////\n\nplot(sslDown, linewidth=2, color=color.new(color.red, 0))\nplot(sslUp, linewidth=2, color=color.new(color.lime, 0))\n\n\n            //////  Trade execution logic  //////  \n            \n//pseudo-code//\n        //Go long when high (or maybe close) breaks above the sslUp and volume is 2x or > Volume[1] and sslUp > sslDown\n        //Close the above longs when sslUp crosses under sslDown (or set takeprofit and stop loss exits)\n        //\n        //Go short when low is lower than the sslUp and volume is 2x or > Volume[1] and sslDown > sslUp\n        //Close shorts when sslDown crosses under sslUp\n\nlongCondition1 = (sslUp > sslDown)\nlongCondition2 = ta.crossover(high, sslUp)\n//longCondition3 = (volume >= (volume[1]*1.89))\nlongCondition = ((longCondition1) and (longCondition2))// and (longCondition3))\n\nlongExit = ta.crossunder(sslUp, sslDown)\n\n            //////  Bring It  //////\nif (longCondition)\n    strategy.entry("Bring It", strategy.long)\n\n            //////  Sling It  //////\nif (longExit)\n    strategy.close("Bring It", comment="Sling It")\n\n\nshortCondition1 = (sslDown) > (sslUp)\nshortCondition2 = ta.crossunder(low, sslUp)\n//shortCondition3 = (volume >= (volume[1]*1.89))\nshortCondition = ((shortCondition1) and (shortCondition2))// and (shortCondition3))\n\nshortExit = ta.crossunder(sslDown, sslUp)\n\n            //////  Bring It  //////\nif (shortCondition)\n    strategy.entry("Bring It", strategy.long)\n\n            //////  Sling It  //////\nif (shortExit)\n    strategy.close("Bring It", comment="Sling It")\n\n            //////  Sling It  //////\nif (shortCondition)\n    strategy.entry("Sling It", strategy.short)\n\n            //////  Bling It  //////\nif (shortExit)\n    strategy.close("Sling It", comment="Bring It")\n\n\n'

class SMOscillatingChannelBreakoutStrategy82910a(PinePortBase, IStrategy):
    source_id = "SM_82910a4d82762f1a"
    source_file = '震荡型通道突破策略Oscillating-Channel-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'period': 25, 'len': 25}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 1
    source_initial_capital = 100
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
