"""batch_011 port of 趋势跟踪止损策略Trend-Following-Strategy-with-Trailing-Stop-Loss.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-29 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © felipefs\n\n//@version=4\nstrategy("Meu Script", overlay=true)\nplot(ohlc4)\n\n//Funçao de Datas\ntestStartYear = input(2018, "Backtest Start Year")\ntestStartMonth = input(6, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(30, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\ntestPeriod() => time >= testPeriodStart and time <= testPeriodStop ? true : false\n\n//Funções de Trailing Stop\nlong_stop_price = 0.0\nshort_stop_price = 0.0\nlong_trail_perc = 0\nshort_trail_perc = 0\n\nlong_stop_price := if (strategy.position_size > 0)\n    stopValue = close * (1 - long_trail_perc)\n    max(stopValue, long_stop_price[1])\nelse\n    0\n\nshort_stop_price := if (strategy.position_size < 0)\n    stopValue = close * (1 + short_trail_perc)\n    min(stopValue, short_stop_price[1])\nelse\n    999999\n\n//Função de Debug\ndebug(value) =>\n    x = bar_index\n    y = close\n    label.new(x, y, tostring(value))\n    \n//Take Profit\nprofit = close * (1 + 0.12)\nstrategy.entry("Long", true)\nstrategy.exit("Take Profit 1 Long", from_entry="Long", limit=profit, qty_percent=50.0)\n \n//ATR Stop\n \n// xATRTrailingStopLong = 0.0\n// xATR = atr(nATRPeriod)\n// nLossLong = nATRMultipLong * xATR\n\n// if (strategy.position_size > 0)\n//     xATRTrailingStopLong := max(nz(xATRTrailingStopLong[1]), close - nLossLong)'

class SMEFA4980DE623827C(PinePortBase, IStrategy):
    source_id = "SM_efa4980de623827c"
    source_file = '趋势跟踪止损策略Trend-Following-Strategy-with-Trailing-Stop-Loss.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'testStartYear': 2018, 'testStartMonth': 6, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
