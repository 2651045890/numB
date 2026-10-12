"""batch_011 port of 移动平均线跟踪策略Moving-Average-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-19 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("MA X 200 BF", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.0)\n\n/////////////// Time Frame ///////////////\ntestStartYear = input(2012, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() => true\n\n///////////// MA 200 /////////////\nslowMA = sma(close, input(200))\n\n/////////////// Strategy ///////////////\nlong = close > slowMA\nshort = close < slowMA\n\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nlong_signal = crossover(last_long, last_short)\nshort_signal = crossover(last_short, last_long)\n\n/////////////// Execution /////////////// \nif testPeriod()\n    strategy.entry("Long Entry",  strategy.long, when=long_signal)\n    strategy.entry("Short Entry", strategy.short, when=short_signal)\n    strategy.exit("Long Ex", "Long Entry")\n    strategy.exit("Short Ex", "Short Entry")\n\n/////////////// Plotting /////////////// \nplot(slowMA, color = long ? color.lime : color.red, linewidth=2)\nbgcolor(strategy.position_size > 0 ? color.lime : strategy.position_size < 0 ? color.red : color.white, transp=80)\nbgcolor(long_signal ? color.lime : short_signal ? color.red : na, transp=30)'

class SMC73EF22B9D08A846(PinePortBase, IStrategy):
    source_id = "SM_c73ef22b9d08a846"
    source_file = '移动平均线跟踪策略Moving-Average-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'testStartYear': 2012, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
