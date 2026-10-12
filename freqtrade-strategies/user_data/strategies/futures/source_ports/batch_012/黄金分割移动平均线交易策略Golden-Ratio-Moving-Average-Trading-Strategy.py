"""batch_012 port of 黄金分割移动平均线交易策略Golden-Ratio-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-29 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © tsujimoto0403\n\n//@version=5\nstrategy("聖杯", overlay=true,default_qty_type=strategy.percent_of_equity,\n     default_qty_value=100)\n\n//ユーザーインプットの準備\nmalongperiod=input.int(200,"長期移動平均BASE200",group = "パラメータ")\nmashortperiod=input.int(10,"長期移動平均BASE10",group = "パラメータ")\nstop=input.int(20,title = "損切の割合％",group = "パラメータ")\nprofit=input.int(5,title = "利食いの割合％",group = "パラメータ")\nstartday=input(title="バックテストを始める日", defval=timestamp("01 Jan 2018 13:30 +0000"), group="期間")\nendday=input(title="バックテスを終わる日", defval=timestamp("1 Jan 2099 19:30 +0000"), group="期間")\n\n//使う変数\nvar float stopprice=0\nvar float takeprofit=0\n\n//とりあえず使うインジケーターをプロット\nmalong=ta.sma(close,malongperiod)\nmashort=ta.sma(close,mashortperiod)\n\n\nplot(malong,color=color.aqua,linewidth = 2)\nplot(mashort,color=color.yellow,linewidth = 2)\nbgcolor(ta.rsi(close,3)<30?color.rgb(229, 86, 86, 48):na)\n\n//期間条件\ndatefilter = true\n\n//エントリー条件\nif close>malong and close<mashort and strategy.position_size == 0 and datefilter and ta.rsi(close,3)<30\n    strategy.entry(id="long", direction=strategy.long)\n\nif strategy.position_size>0 \n    strategy.exit(id="long",stop=(1-0.01*stop)*strategy.position_avg_price)\n\n//売り\nif  strategy.position_size > 0 and close>mashort and close<low[1] \n    strategy.close(id ="long")\n\n\n\n'

class SMGoldenRatioMovingAverageTradingStrategy09692d(PinePortBase, IStrategy):
    source_id = "SM_09692d358db0ba1f"
    source_file = '黄金分割移动平均线交易策略Golden-Ratio-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'malongperiod': 200, 'mashortperiod': 10, 'stop': 20, 'profit': 5, 'startday': 'timestamp("01 Jan 2018 13:30 +0000")', 'endday': 'timestamp("1 Jan 2099 19:30 +0000")'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
