"""batch_012 port of 随机游走策略Random-Walk-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-02 00:00:00\nend: 2023-10-08 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//@author=Tr0sT\nstrategy(title = "Random strategy", shorttitle = "Random", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\na = 16\nc = 10\nm = 1000\nGetRandom(prev) =>\n    GetRandom = (a * prev + c) % m\n\nseed = input(200, minval = 2, maxval = m)\nstopLoss = input(30, title = "Stop loss percentage(0.1%)")\ntakeProfit = input(30, title = "Take profit percentage(0.1%)")\n\n\ncurRandom = na\ncurRandom := nz(curRandom[1]) == 0 ? seed : GetRandom(curRandom[1])\nif (strategy.position_size == 0)\n    if (curRandom >= m / 2)\n        strategy.entry("Enter", strategy.long)\n    else\n        strategy.entry("Enter", strategy.short)\n        \n    strategy.exit("Exit", "Enter", loss = close * stopLoss / 1000 / syminfo.mintick, profit = close * takeProfit / 1000 / syminfo.mintick)            \n\n// === Backtesting Dates ===\ntestPeriodSwitch = input(false, "Custom Backtesting Dates")\ntestStartYear = input(2018, "Backtest Start Year")\ntestStartMonth = input(3, "Backtest Start Month")\ntestStartDay = input(6, "Backtest Start Day")\ntestStartHour = input(08, "Backtest Start Hour")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,testStartHour,0)\ntestStopYear = input(2018, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(14, "Backtest Stop Day")\ntestStopHour = input(14, "Backtest Stop Hour")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,testStopHour,0)\ntestPeriod() =>\n    time >= testPeriodStart and time <= testPeriodStop ? true : false\nisPeriod = testPeriodSwitch == true ? testPeriod() : true\n// === /END\nif not isPeriod\n    strategy.cancel_all()\n    strategy.close_all()\n'

class SMRandomWalkStrategy4c52db(PinePortBase, IStrategy):
    source_id = "SM_4c52db34f70704d5"
    source_file = '随机游走策略Random-Walk-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'seed': 200, 'stopLoss': 30, 'takeProfit': 30, 'testPeriodSwitch': False, 'testStartYear': 2018, 'testStartMonth': 3, 'testStartDay': 6, 'testStartHour': 8, 'testStopYear': 2018, 'testStopMonth': 12, 'testStopDay': 14, 'testStopHour': 14}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
