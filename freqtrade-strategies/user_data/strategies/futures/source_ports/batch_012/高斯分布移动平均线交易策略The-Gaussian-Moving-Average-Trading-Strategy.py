"""batch_012 port of 高斯分布移动平均线交易策略The-Gaussian-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-26 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © jensenvilhelm\n\n// Here is an attempt to create a robust strategy for BTCUSD on a 5 minute chart\n// I can\'t seem to get this code to work the way i want.... if you want to give it a try, please let me know -\n// how it goes in comment section. \n\n//@version=5\n// Define the strategy settings\nstrategy("The Z-score", shorttitle="TZS", overlay=true)\n\n// User can set the start date for the strategy\nstartDate = timestamp("2023 06 01")\n\n// Heikin-Ashi Open, Close, High and Low calculation\nhaClose = ohlc4\nvar float haOpen = na\nhaOpen := na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2\nhaHigh = math.max(nz(haOpen, high), nz(haClose, high), high)\nhaLow = math.min(nz(haOpen, low), nz(haClose, low), low)\n\n// Function to calculate the Z-Score\nz_score(_series, _length) =>\n    _mean = ta.sma(_series, _length)\n    _stddev = ta.stdev(_series, _length)\n    (_series - _mean) / _stddev\n\n// Compute the score and its EMA\nscore = z_score(ta.ema(haClose, 10), 25)\nemaScore = ta.ema(score, 20)\n\n// Calculate lower and upper thresholds using percentiles of EMA\nlowerBlue = ta.percentile_linear_interpolation(emaScore, 50, 10)\nupperBlue = ta.percentile_linear_interpolation(emaScore, 50, 90)\n\n// Calculate the middle line as 50th percentile\nmiddleLine = ta.percentile_linear_interpolation(emaScore, 50, 50) \n\n// Plot the EMA of the score and the thresholds\nplot(emaScore,"The White Line", color=color.white, linewidth=2)\nplot(lowerBlue,"Lower Blue Line", linewidth=2)\nplot(upperBlue, "Upper Blue Line", linewidth=2)\nplot(middleLine, "Middle Yellow Line", linewidth=2, color=color.yellow)\nplot(score,"The Z-Score Mixed With EMA 10", color=color.green)\n\n// Calculate highest and lowest EMA score over 100 bars period\nhighest = ta.highest(emaScore, 100)\nlowest = ta.lowest(emaScore, 100)\n\n// Plot highest and lowest EMA score lines \nplot(highest, "Highest of emaScore", color=color.red, linewidth=2)\nplot(lowest, "Lowest of emaScore", color=color.red, linewidth=2)\n\n// Define entry and exit conditions for long and short positions\nlongCon = ta.crossover(score, lowerBlue) or ta.crossover(emaScore, middleLine)\naddOn = ta.crossover(score, highest)\nshortCon = ta.crossunder(emaScore, upperBlue) or ta.crossunder(emaScore, lowerBlue) or ta.crossunder(emaScore, highest)\n\n// Execute trading logic based on conditions and after the start date\nif (time >= startDate)\n    if longCon\n        strategy.entry("Long", strategy.long)\n        if shortCon\n            strategy.close("Long")\n    if addOn\n        strategy.entry("LongNR2", strategy.long)\n        if shortCon\n            strategy.close("LongNR2")\n    \n    if shortCon\n        strategy.entry("Short", strategy.short)\n        if longCon\n            strategy.close("Short")\n\n'

class SMTheGaussianMovingAverageTradingStrategy15ca4d(PinePortBase, IStrategy):
    source_id = "SM_15ca4d206829415d"
    source_file = '高斯分布移动平均线交易策略The-Gaussian-Moving-Average-Trading-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
