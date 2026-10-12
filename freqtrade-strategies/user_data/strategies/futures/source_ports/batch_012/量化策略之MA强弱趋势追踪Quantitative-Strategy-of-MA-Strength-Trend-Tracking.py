"""batch_012 port of 量化策略之MA强弱趋势追踪Quantitative-Strategy-of-MA-Strength-Trend-Tracking.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-19 00:00:00\nend: 2024-01-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © HeWhoMustNotBeNamed\n\n//@version=4\nstrategy("MA Strength Strategy", overlay=false, initial_capital = 20000, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, commission_type = strategy.commission.percent, pyramiding = 1, commission_value = 0.01)\nMAType = input(title="Moving Average Type", defval="ema", options=["ema", "sma", "hma", "rma", "vwma", "wma"])\nLookbackPeriod = input(10, step=10)\n\nIndexMAType = input(title="Moving Average Type", defval="hma", options=["ema", "sma", "hma", "rma", "vwma", "wma"])\nIndexMAPeriod = input(200, step=10)\n\nconsiderTrendDirection = input(true)\nconsiderTrendDirectionForExit = input(true)\noffset = input(1, step=1)\ntradeDirection = input(title="Trade Direction", defval=strategy.direction.long, options=[strategy.direction.all, strategy.direction.long, strategy.direction.short])\ni_startTime = input(defval = timestamp("01 Jan 2010 00:00 +0000"), title = "Start Time", type = input.time)\ni_endTime = input(defval = timestamp("01 Jan 2099 00:00 +0000"), title = "End Time", type = input.time)\ninDateRange = true\n\nf_getMovingAverage(source, MAType, length)=>\n    ma = sma(source, length)\n    if(MAType == "ema")\n        ma := ema(source,length)\n    if(MAType == "hma")\n        ma := hma(source,length)\n    if(MAType == "rma")\n        ma := rma(source,length)\n    if(MAType == "vwma")\n        ma := vwma(source,length)\n    if(MAType == "wma")\n        ma := wma(source,length)\n    ma\n    \n\nf_getMaAlignment(MAType, includePartiallyAligned)=>\n    ma5 = f_getMovingAverage(close,MAType,5)\n    ma10 = f_getMovingAverage(close,MAType,10)\n    ma20 = f_getMovingAverage(close,MAType,20)\n    ma30 = f_getMovingAverage(close,MAType,30)\n    ma50 = f_getMovingAverage(close,MAType,50)\n    ma100 = f_getMovingAverage(close,MAType,100)\n    ma200 = f_getMovingAverage(close,MAType,200)\n\n    upwardScore = 0.0\n    upwardScore := close > ma5? upwardScore+1.10:upwardScore\n    upwardScore := ma5 > ma10? upwardScore+1.10:upwardScore\n    upwardScore := ma10 > ma20? upwardScore+1.10:upwardScore\n    upwardScore := ma20 > ma30? upwardScore+1.10:upwardScore\n    upwardScore := ma30 > ma50? upwardScore+1.15:upwardScore\n    upwardScore := ma50 > ma100? upwardScore+1.20:upwardScore\n    upwardScore := ma100 > ma200? upwardScore+1.25:upwardScore\n    \n    upwards = close > ma5 and ma5 > ma10 and ma10 > ma20 and ma20 > ma30 and ma30 > ma50 and ma50 > ma100 and ma100 > ma200\n    downwards = close < ma5 and ma5 < ma10 and ma10 < ma20 and ma20 < ma30 and ma30 < ma50 and ma50 < ma100 and ma100 < ma200\n    trendStrength = upwards?1:downwards?-1:includePartiallyAligned ? (upwardScore > 6? 0.5: upwardScore < 2?-0.5:upwardScore>4?0.25:-0.25) : 0\n    [trendStrength, upwardScore]\n    \nincludePartiallyAligned = true\n[trendStrength, upwardScore] = f_getMaAlignment(MAType, includePartiallyAligned)\n\nupwardSum = sum(upwardScore, LookbackPeriod)\n\nindexSma = f_getMovingAverage(upwardSum,IndexMAType,IndexMAPeriod)\n\nplot(upwardSum, title="Moving Average Strength", color=color.green, linewidth=2, style=plot.style_linebr)\nplot(indexSma, title="Strength MA", color=color.red, linewidth=1, style=plot.style_linebr)\nbuyCondition = crossover(upwardSum,indexSma) and (upwardSum > upwardSum[offset] or not considerTrendDirection) \nsellCondition = crossunder(upwardSum,indexSma) and (upwardSum < upwardSum[offset]  or not considerTrendDirection)\n\nexitBuyCondition = crossunder(upwardSum,indexSma)\nexitSellCondition = crossover(upwardSum,indexSma) \nstrategy.risk.allow_entry_in(tradeDirection)\nstrategy.entry("Buy", strategy.long, when= inDateRange and buyCondition, oca_name="oca_buy")\nstrategy.close("Buy", when = considerTrendDirectionForExit? sellCondition : exitBuyCondition)\nstrategy.entry("Sell", strategy.short, when= inDateRange and sellCondition, oca_name="oca_sell")\nstrategy.close( "Sell", when = considerTrendDirectionForExit? buyCondition : exitSellCondition)\n\n'

class SMMAQuantitativeStrategyofMAStrengthTrendTracking95b8cd(PinePortBase, IStrategy):
    source_id = "SM_95b8cd34ec6f191c"
    source_file = '量化策略之MA强弱趋势追踪Quantitative-Strategy-of-MA-Strength-Trend-Tracking.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'MAType': 'ema', 'LookbackPeriod': 10, 'IndexMAType': 'hma', 'IndexMAPeriod': 200, 'considerTrendDirection': True, 'considerTrendDirectionForExit': True, 'offset': 1, 'tradeDirection': 'strategy.direction.long', 'i_startTime': 'timestamp("01 Jan 2010 00:00 +0000")', 'i_endTime': 'timestamp("01 Jan 2099 00:00 +0000")'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.01
    source_pyramiding = 1
    source_initial_capital = 20000
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
