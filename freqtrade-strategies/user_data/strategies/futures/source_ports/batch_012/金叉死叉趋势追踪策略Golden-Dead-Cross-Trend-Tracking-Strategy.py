"""batch_012 port of 金叉死叉趋势追踪策略Golden-Dead-Cross-Trend-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-08 00:00:00\nend: 2023-12-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Ta3MooChi\n//@version=5\nstrategy("전략", overlay=true,process_orders_on_close = true, pyramiding = 100)\n\nshort_ma = ta.sma(close,input.int(3, "단기 이평", minval = 1))\nlong_ma = ta.sma(close, input.int(19,"장기 이평", minval = 1))\n\ntrend_ma = ta.sma(close, input.int(100," 추세 이평", minval = 20, group = "추세 이평"))\nup_trend = (trend_ma > trend_ma[1])\nuse_trend_ma = input.bool(true, title = "추세용 이평 사용", group = "추세 이평" )\ninTrendMa = not use_trend_ma or up_trend\n\nuseDateFilter = input.bool(true, title = "특정 기간 백테스트", group = "기간 백테스트")\nbacktestStartDate = input(timestamp("1 Jan 2021"), title = "시작날짜", group = "기간 백테스트")\nbacktestEndDate = input(timestamp("1 Jan 2022"), title = "종료날짜", group = "기간 백테스트")\ninTradeWindow = true\n\nlongStopPerc = 1 + input.float(3, "최소수익률%", minval = 1)*0.01\n\nlongcondition = ta.crossover(short_ma, long_ma)\nshortcondition = ta.crossunder(short_ma, long_ma)\n\nif (longcondition) and inTradeWindow and inTrendMa\n    strategy.entry("long", strategy.long)\n\nif (shortcondition) and (close > strategy.position_avg_price*longStopPerc) and inTradeWindow\n    strategy.close_all()\n\nif not inTradeWindow and inTradeWindow[1]\n    strategy.cancel_all()\n    strategy.close_all(comment = "매매 종료")\n\nplot(short_ma,color = color.yellow)\nplot(long_ma,color = color.blue)\nplot(trend_ma,color = color.gray)\n    \n\n\n'

class SMGoldenDeadCrossTrendTrackingStrategye96d8a(PinePortBase, IStrategy):
    source_id = "SM_e96d8a2c1189ba29"
    source_file = '金叉死叉趋势追踪策略Golden-Dead-Cross-Trend-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'use_trend_ma': True, 'useDateFilter': True, 'backtestStartDate': 'timestamp("1 Jan 2021")', 'backtestEndDate': 'timestamp("1 Jan 2022")'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 100
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
