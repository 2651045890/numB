"""batch_011 port of 移动平均线交叉金叉优化交易策略Golden-Cross-Optimized-Moving-Average-Crossover-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-12 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Golden Cross, SMA 100, Moving Average Strategy (by Coinrule)", shorttitle="Golden_Cross_Strat_MA100_optimized", overlay=true, initial_capital = 1000,process_orders_on_close=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n// Input\nswitch1=input(true, title="Enable Bar Color?")\nswitch2=input(false, title="Show Fast Moving Average")\nswitch3=input(true, title="Show Slow Moving Average")\n\n//Calculate Moving Averages\nmovingaverage_fast = sma(close, input(9))\nmovingaverage_slow = sma(close, input(100))\nmovingaverage_normal= sma(close, input(50))\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false       // create function "within window of time"\n\n\n// Calculation\nbullish_cross = crossover(movingaverage_fast, movingaverage_normal)\nbearish_cross = crossunder(movingaverage_fast, movingaverage_normal)\n\n//Entry and Exit\nif bullish_cross and window() and movingaverage_slow > movingaverage_normal\n    strategy.entry("long", strategy.long)\n\nstrategy.close("long", when = bearish_cross and window())\n\n// Colors\nbartrendcolor = close > movingaverage_fast and close > movingaverage_slow and change(movingaverage_slow) > 0 ? color.green : close < movingaverage_fast and close < movingaverage_slow and change(movingaverage_slow) < 0 ? color.red : color.blue\nbarcolor(switch1?bartrendcolor:na)\n\n// Output\nplot(movingaverage_fast, color=color.orange, linewidth=2)\nplot(movingaverage_slow, color=color.purple, linewidth=3)\nplot(movingaverage_normal, color=color.blue, linewidth=2)\n\nbgcolor(color = showDate and window() ? color.gray : na, transp = 90)'

class SM91F4CB6F5ADC80D7(PinePortBase, IStrategy):
    source_id = "SM_91f4cb6f5adc80d7"
    source_file = '移动平均线交叉金叉优化交易策略Golden-Cross-Optimized-Moving-Average-Crossover-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'switch1': True, 'switch2': False, 'switch3': True, 'fromMonth': 1, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
