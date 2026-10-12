"""batch_011 port of 移动平均回拉交易策略Moving-Average-Pullback-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-30 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © tsujimoto0403\n\n//@version=5\nstrategy("simple pull back", overlay=true,default_qty_type=strategy.percent_of_equity,\n     default_qty_value=100)\n\n//input value \nmalongperiod=input.int(200,"長期移動平均BASE200/period of long term sma",group = "パラメータ")\nmashortperiod=input.int(10,"長期移動平均BASE10/period of short term sma",group = "パラメータ")\nstoprate=input.int(5,title = "損切の割合％/stoploss percentages",group = "パラメータ")\nprofit=input.int(20,title = "利食いの割合％/take profit percentages",group = "パラメータ")\nstartday=input(title="バックテストを始める日/start trade day", defval=timestamp("01 Jan 2000 13:30 +0000"), group="期間")\nendday=input(title="バックテスを終わる日/finish date day", defval=timestamp("1 Jan 2099 19:30 +0000"), group="期間")\n\n\n//polt indicators that we use \nmalong=ta.sma(close,malongperiod)\nmashort=ta.sma(close,mashortperiod)\n\nplot(malong,color=color.aqua,linewidth = 2)\nplot(mashort,color=color.yellow,linewidth = 2)\n\n//date range \ndatefilter = true\n\n//open conditions\nif close>malong and close<mashort and strategy.position_size == 0 and datefilter and ta.rsi(close,3)<30 \n    strategy.entry(id="long", direction=strategy.long)\n    \n//sell conditions \nstrategy.exit(id="cut",from_entry="long",stop=(1-0.01*stoprate)*strategy.position_avg_price,limit=(1+0.01*profit)*strategy.position_avg_price)\n\n\nif close>mashort and close<low[1] and strategy.position_size>0\n    strategy.close(id ="long")\n        \n\n\n'

class SM855B2C4472341C28(PinePortBase, IStrategy):
    source_id = "SM_855b2c4472341c28"
    source_file = '移动平均回拉交易策略Moving-Average-Pullback-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'malongperiod': 200, 'mashortperiod': 10, 'stoprate': 5, 'profit': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
