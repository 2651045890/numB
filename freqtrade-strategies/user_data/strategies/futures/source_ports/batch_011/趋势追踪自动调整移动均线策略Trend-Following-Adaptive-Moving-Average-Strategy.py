"""batch_011 port of 趋势追踪自动调整移动均线策略Trend-Following-Adaptive-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-03 00:00:00\nend: 2023-10-09 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//\n// @version=4\n// © Ehsan Haghpanah, (ehsanha)\n// Algorithmic Trading Research\n//\n// eha Moving Averages Strategy, \n// A simple strategy based on crossing Moving Averages of \n// different lengths (a fast moving average and slow one)\n//\n\nstrategy(title = "eha Moving Averages Strategy", shorttitle = "eha MA Strategy", overlay = true)\n\n// \n// -- strategy parameter(s)\n// moving averages parameter(s)\nvar _fastMA_len  = input(title = "Fast MA Length",  defval = 21,    type = input.integer, minval = 1, step = 1)\nvar _slowMA_len  = input(title = "Slow MA Length",  defval = 34,    type = input.integer, minval = 1, step = 1)\nvar _ma_algo_id  = input(title = "MA Algorithm",    defval = "SMA", options = ["SMA", "EMA", "WMA"])\n// backtesting date and time range parameter(s)\nvar _startYear   = input(defval = 2020, title = "Start Year",  type = input.integer, minval = 1976)\nvar _startMonth  = input(defval = 1,    title = "Start Month", type = input.integer, minval = 1, maxval = 12)\nvar _startDay    = input(defval = 1,    title = "Start Day",   type = input.integer, minval = 1, maxval = 31)\nvar _closeYear   = input(defval = 2020, title = "Close Year",  type = input.integer, minval = 1984)\nvar _closeMonth  = input(defval = 9,    title = "Close Month", type = input.integer, minval = 1, maxval = 12)\nvar _closeDay    = input(defval = 1,    title = "Close Day",   type = input.integer, minval = 1, maxval = 31)\n\n//\n// -- function(s) and calculation(s)\n// checks whether current time is in backtesting time range\nstart_t = timestamp(_startYear, _startMonth, _startDay, 00, 00)     // backtesting range start time, (00, 00); (hour, minute)\nclose_t = timestamp(_closeYear, _closeMonth, _closeDay, 23, 59)     // backtesting range close time, (23, 59); (hour, minute)\nisInRange() => true\n//\n// calculates moving average based on provided algorithm, source and length\n// alg : moving average algorithm\n// len : length\n// ser : series\ncalcMA(alg, len, ser) =>\n    (len == 0) ? ser : ((alg == "SMA") ? sma(ser, len) : ((alg == "EMA") ? ema(ser, len) : (alg == "WMA" ? wma(ser, len) : na)))\n\n//\n// -- strategy logic and calculation(s)\nma_fast  = calcMA(_ma_algo_id, _fastMA_len, close)\nma_slow  = calcMA(_ma_algo_id, _slowMA_len, close)\ncross_ov = crossover (ma_fast, ma_slow) // returns true if fastMA crosses over slowMA\ncross_un = crossunder(ma_fast, ma_slow) // returns true if slowMA crosses over fastMA\n\n//\n// -- strategy execution logic\n// opens a long position whenever the time is in range and crosses over\nstrategy.entry("ID", comment = "-", long = strategy.long, when = isInRange() and cross_ov)\n// closes the position whenever the time is in range and crosses under\nstrategy.close("ID", comment = "-", when = isInRange() and cross_un)\n\n//\n// -- drawing and visualization\nco_fast = color.new(color.gray, 25)\nco_slow = color.new(color.gray, 75)\n// drawing moving average(s)\nplot(ma_fast, color = co_fast, linewidth = 2, style = plot.style_line)\nplot(ma_slow, color = co_slow, linewidth = 3, style = plot.style_line)'

class SM728C5AB35B9E2383(PinePortBase, IStrategy):
    source_id = "SM_728c5ab35b9e2383"
    source_file = '趋势追踪自动调整移动均线策略Trend-Following-Adaptive-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'_fastMA_len': 21, '_slowMA_len': 34, '_ma_algo_id': 'SMA', '_startYear': 2020, '_startMonth': 1, '_startDay': 1, '_closeYear': 2020, '_closeMonth': 9, '_closeDay': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
