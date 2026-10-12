"""batch_012 port of 黄金交叉策略Golden-Cross-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-27 00:00:00\nend: 2023-09-26 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Dumb strategy 2 - Golden Cross", shorttitle="Golden Cross", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nlShort = input(50, title="short length")\nlLong = input(200, title="long length")\nsrc = input(close, title="Source")\n\nsmaShort = sma(src, lShort)\nsmaLong = sma(src, lLong)\n\nplot(smaShort, title="SMA Short", style=line, linewidth=3, color=lime)\nplot(smaLong, title="SMA Long", style=line, linewidth=3, color=red)\n\n\n//\n//Backtest Time Inputs\n//\n\ntestStartYear = input(2009, "Backtest Start Year")\ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(1, "Backtest Stop Month")\ntestStopDay = input(01, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\ntestPeriodBackground = input(title="Color Background?", type=bool, defval=true)\ntestPeriodBackgroundColor = testPeriodBackground and (time >= testPeriodStart) and (time <= testPeriodStop) ? blue : na\nbgcolor(testPeriodBackgroundColor, transp=80)\n\n\ntestPeriod() => true\n\n\t\n\nif testPeriod()\n\tlongCondition = crossover(smaShort, smaLong)\n\tif (longCondition)\n\t\tstrategy.entry("Long Entry", strategy.long)\n\n\tshortCondition = crossunder(smaShort, smaLong)\n\tif (shortCondition)\n\t\tstrategy.close_all(true)\n\t\n'

class SMGoldenCrossStrategy5d1fb8(PinePortBase, IStrategy):
    source_id = "SM_5d1fb8b895a76f57"
    source_file = '黄金交叉策略Golden-Cross-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'lShort': 50, 'lLong': 200, 'src': 'close', 'testStartYear': 2009, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 1, 'testStopDay': 1, 'testPeriodBackground': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
