"""batch_012 port of 高低指标与均线配合指标策略Aligned-Moving-Average-and-Cumulative-High-Low-Index-Combination-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-21 00:00:00\nend: 2023-11-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © HeWhoMustNotBeNamed\n\n//@version=4\nstrategy("AlignedMA and Cumulative HighLow Strategy", overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, commission_type = strategy.commission.percent, pyramiding = 1, commission_value = 0.01, calc_on_order_fills = true)\n\nMAType = input(title="Moving Average Type", defval="sma", options=["ema", "sma", "hma", "rma", "vwma", "wma"])\nincludePartiallyAligned = input(true)\nHighLowPeriod = input(50, minval=1,step=1)\nLookbackPeriod = input(10, minval=1,step=1)\n\nsupertrendMult = input(2, minval=1, maxval=10, step=0.5)\nsupertrendLength = input(10, minval=1)\n\ntradeDirection = input(title="Trade Direction", defval=strategy.direction.long, options=[strategy.direction.all, strategy.direction.long, strategy.direction.short])\nbacktestYears = input(10, minval=1, step=1)\n\nf_getMovingAverage(source, MAType, length)=>\n    ma = sma(source, length)\n    if(MAType == "ema")\n        ma := ema(source,length)\n    if(MAType == "hma")\n        ma := hma(source,length)\n    if(MAType == "rma")\n        ma := rma(source,length)\n    if(MAType == "vwma")\n        ma := vwma(source,length)\n    if(MAType == "wma")\n        ma := wma(source,length)\n    ma\n    \nf_getMaAlignment(MAType, includePartiallyAligned)=>\n    ma5 = f_getMovingAverage(close,MAType,5)\n    ma10 = f_getMovingAverage(close,MAType,10)\n    ma20 = f_getMovingAverage(close,MAType,20)\n    ma30 = f_getMovingAverage(close,MAType,30)\n    ma50 = f_getMovingAverage(close,MAType,50)\n    ma100 = f_getMovingAverage(close,MAType,100)\n    ma200 = f_getMovingAverage(close,MAType,200)\n\n    upwardScore = 0\n    upwardScore := close > ma5? upwardScore+1:upwardScore\n    upwardScore := ma5 > ma10? upwardScore+1:upwardScore\n    upwardScore := ma10 > ma20? upwardScore+1:upwardScore\n    upwardScore := ma20 > ma30? upwardScore+1:upwardScore\n    upwardScore := ma30 > ma50? upwardScore+1:upwardScore\n    upwardScore := ma50 > ma100? upwardScore+1:upwardScore\n    upwardScore := ma100 > ma200? upwardScore+1:upwardScore\n    \n    upwards = close > ma5 and ma5 > ma10 and ma10 > ma20 and ma20 > ma30 and ma30 > ma50 and ma50 > ma100 and ma100 > ma200\n    downwards = close < ma5 and ma5 < ma10 and ma10 < ma20 and ma20 < ma30 and ma30 < ma50 and ma50 < ma100 and ma100 < ma200\n    upwards?1:downwards?-1:includePartiallyAligned ? (upwardScore > 5? 0.5: upwardScore < 2?-0.5:upwardScore>3?0.25:-0.25) : 0\n\nf_getHighLowValue(HighLowPeriod)=>\n    currentHigh = highest(high,HighLowPeriod) == high\n    currentLow = lowest(low,HighLowPeriod) == low\n    currentHigh?1:currentLow?-1:0\n\ninDateRange = time >= timestamp(syminfo.timezone, year(timenow) - backtestYears, 01, 01, 0, 0)\n\nmaAlignment = f_getMaAlignment(MAType,includePartiallyAligned)\nalignedMaIndex = sum(maAlignment,LookbackPeriod)\n\nmaAlignmentDirection = alignedMaIndex > alignedMaIndex[1] ? 1 : alignedMaIndex < alignedMaIndex[1] ? -1 : 0\nmaAlignmentDirection := maAlignmentDirection == 0? nz(maAlignmentDirection[1],0):maAlignmentDirection\n\nhighLowIndex = f_getHighLowValue(HighLowPeriod)\ncumulativeHighLowIndex = sum(highLowIndex,LookbackPeriod)\n\nhlDirection = cumulativeHighLowIndex > cumulativeHighLowIndex[1] ? 1 : cumulativeHighLowIndex < cumulativeHighLowIndex[1] ? -1 : 0\nhlDirection := hlDirection == 0? nz(hlDirection[1],0):hlDirection\n\n[superTrend, dir] = supertrend(supertrendMult, supertrendLength)\n\nbuyEntry = (dir == -1 and maAlignmentDirection == 1 and hlDirection == 1)\nsellEntry = (dir == 1 and maAlignmentDirection == -1 and hlDirection == -1)\n\nbarColor = buyEntry?color.lime:sellEntry?color.orange:color.gray\nbarcolor(barColor)\n\n// strategy.risk.allow_entry_in(tradeDirection)\nstrategy.entry("Buy", strategy.long, when=barColor == color.lime and inDateRange, oca_name="oca_buy")\nstrategy.close("Buy", when=dir == 1)\n\nstrategy.entry("Sell", strategy.short, when=barColor == color.orange and inDateRange, oca_name="oca_sell")\nstrategy.close("Sell", when=dir == -1)\n\n'

class SMAlignedMovingAverageandCumulativeHighLowIndexCombinatio55ca22(PinePortBase, IStrategy):
    source_id = "SM_55ca22882a709e21"
    source_file = '高低指标与均线配合指标策略Aligned-Moving-Average-and-Cumulative-High-Low-Index-Combination-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'MAType': 'sma', 'includePartiallyAligned': True, 'HighLowPeriod': 50, 'LookbackPeriod': 10, 'supertrendMult': 2, 'supertrendLength': 10, 'tradeDirection': 'strategy.direction.long', 'backtestYears': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.01
    source_pyramiding = 1
    source_initial_capital = 1000
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
