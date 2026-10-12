"""batch_012 port of 配置化多均线投票交易策略Configurable-Multi-MA-Crossover-Voting-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-16 00:00:00\nend: 2023-09-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © levieux\n\n//@version=5\nstrategy(title=\'Configurable Multi MA Crossover Voting System\', shorttitle=\'Configurable Multi MA Crossover Voting System\', initial_capital=1000, overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1)\ncrossoverConfig= input.string(defval="2x4,3x5,4x6", title="Crossover Config")\nsource= input.source(high)\nmaType= input.string("WMA", title="Moving Average Type", options=["WMA","SMA","VWMA"])\natrPeriod= input(14, title="ATR Period")\nprofitAtr = input(10, title="Profit ATR x")\nlossAtr = input(5, title="Loss ATR x")\n\n\nma(src,length,type) => \n    float ma = switch type\n\t    "SMA" => ta.sma(src, length)\n\t    "WMA" => ta.wma(src, length)\n\t    "VWMA" => ta.vwma(src, length)\n\ncrossoverGroups= str.split(crossoverConfig, ",")\ncrossoverCount= array.size(crossoverGroups)\ncrossovers= array.new_string(crossoverCount)\npositions= array.new_int(crossoverCount, 0)\nlongVotes= 0\nfor i= 0 to crossoverCount-1\n    crossover= str.tostring(array.get(crossoverGroups, i))\n    crossoverBoundaries= str.split(crossover, "x")\n    int fastLength= math.round(str.tonumber(array.get(crossoverBoundaries, 0)))\n    int slowLength= math.round(str.tonumber(array.get(crossoverBoundaries, 1)))\n    wmaFast= ma(source,fastLength,maType)\n    wmaSlow= ma(source,slowLength,maType)\n    if wmaFast>wmaSlow\n        longVotes:= longVotes + 1\n        array.set(positions, i, 1)\n\nlongCondition= longVotes==crossoverCount and strategy.position_size==0\n\n\n//profitTicks = profitAtr*ta.atr(atrPeriod)/syminfo.mintick\n//lossTicks = lossAtr*ta.atr(atrPeriod)/syminfo.mintick\nprofitPrice= close+profitAtr*ta.atr(atrPeriod)\nlossPrice= close-lossAtr*ta.atr(atrPeriod)\n\nif strategy.position_size>0\n    profitPrice:= profitPrice[1]\n    lossPrice:= lossPrice[1]\n\nplot(profitPrice, color=color.green)\nplot(lossPrice, color=color.red)\n\nif longCondition and profitPrice>0\n    strategy.entry("Long", strategy.long)\n\nif longVotes<crossoverCount and strategy.position_size>0 and (high>profitPrice or low<lossPrice)\n    strategy.close("Long")\n    \nlongVotes:= 0\n'

class SMConfigurableMultiMACrossoverVotingSysteme89c85(PinePortBase, IStrategy):
    source_id = "SM_e89c851af3caed42"
    source_file = '配置化多均线投票交易策略Configurable-Multi-MA-Crossover-Voting-System.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'crossoverConfig': '"2x4', 'source': 'high', 'maType': 'WMA', 'atrPeriod': 14, 'profitAtr': 10, 'lossAtr': 5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'Array/matrix operations are present and are not parity-certified by the generic adapter.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
