"""batch_011 port of 移动平均线系统交易策略Moving-Average-System-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-05 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Simple 17 BF ?", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.0)\n\n/////////////// Time Frame ///////////////\ntestStartYear = input(2012, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() => true\n\n///////////// Moving Average /////////////\nsource = input(title="MA Source", defval=ohlc4)\nmaType = input(title="MA Type", defval="sma", options=["sma", "ema", "swma", "wma", "vwma", "rma"])\nlength = input(title="MA Length", defval=17)\n\n///////////// Get MA Function /////////////\ngetMAType(maType, sourceType, maLen) => \n    res = sma(close, 1)\n    \n    if maType == "ema"\n        res := ema(sourceType, maLen)\n    if maType == "sma"\n        res := sma(sourceType, maLen)\n    if maType == "swma"\n        res := swma(sourceType)\n    if maType == "wma"\n        res := wma(sourceType, maLen)\n    if maType == "vwma"\n        res := vwma(sourceType, maLen)\n    if maType == "rma"\n        res := rma(sourceType, maLen)\n    res\n    \nMA = getMAType(maType, source, length)\n\n/////////////// Strategy ///////////////\nlong = close > MA\nshort = close < MA\n\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nlong_signal = crossover(last_long, last_short)\nshort_signal = crossover(last_short, last_long)\n\n/////////////// Execution /////////////// \nif testPeriod()\n    strategy.entry("L", strategy.long, when=long_signal)\n    strategy.entry("S", strategy.short, when=short_signal)\n\n/////////////// Plotting /////////////// \np1 = plot(MA, color = long ? color.lime : color.red, linewidth=2)\np2 = plot(close, linewidth=2)\nfill(p1, p2, color=strategy.position_size > 0 ? color.lime : strategy.position_size < 0 ? color.red : color.white, transp=80)'

class SM325432A96181255E(PinePortBase, IStrategy):
    source_id = "SM_325432a96181255e"
    source_file = '移动平均线系统交易策略Moving-Average-System-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'testStartYear': 2012, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31, 'maType': 'sma', 'length': 17}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
