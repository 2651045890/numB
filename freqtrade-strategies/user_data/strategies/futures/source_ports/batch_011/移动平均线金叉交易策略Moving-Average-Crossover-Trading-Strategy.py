"""batch_011 port of 移动平均线金叉交易策略Moving-Average-Crossover-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-30 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © TwoChiefs\n\n//@version=4\nstrategy("John EMA Crossover Strategy", overlay=true)\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2020, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2021, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\n//CREATE USER-INPUT VARIABLES\n\nperiodShort = input(13, minval=1, title="Enter Period for Short Moving Average")\nsmoothingShort = input(title="Choose Smoothing Type for Short Moving Average", defval="EMA", options=["RMA", "SMA", "EMA", "WMA", "VWMA", "SMMA", "DEMA", "TEMA", "HullMA", "LSMA"])\n\nperiodLong = input(48, minval=1, title="Enter Period for Long Moving Average")\nsmoothingLong = input(title="Choose Smoothing Type for Long Moving Average", defval="EMA", options=["RMA", "SMA", "EMA", "WMA", "VWMA", "SMMA", "DEMA", "TEMA", "HullMA", "LSMA"])\n\nperiodExit = input(30, minval=1, title="Enter Period for Exit Moving Average")\nsmoothingExit = input(title="Choose Smoothing Type for Exit Moving Average", defval="EMA", options=["RMA", "SMA", "EMA", "WMA", "VWMA", "SMMA", "DEMA", "TEMA", "HullMA", "LSMA"])\n\n\nsrc1 = close\npivot = (high + low + close) / 3\n\n//MA CALCULATION FUNCTION\nma(smoothing, src, length) => \n    if smoothing == "RMA"\n        rma(src, length)\n    else\n        if smoothing == "SMA"\n            sma(src, length)\n        else \n            if smoothing == "EMA"\n                ema(src, length)\n            else \n                if smoothing == "WMA"\n                    wma(src, length)\n\t\t\t\telse\n\t\t\t\t\tif smoothing == "VWMA"\n\t\t\t\t\t\tvwma(src, length)\n\t\t\t\t\telse\n\t\t\t\t\t\tif smoothing == "SMMA"\n\t\t\t\t\t\t\tna(src[1]) ? sma(src, length) : (src[1] * (length - 1) + src) / length\n\t\t\t\t\t\t\n\t\t\t\t\t\telse\n\t\t\t\t\t\t\tif smoothing == "HullMA"\n\t\t\t\t\t\t\t\twma(2 * wma(src, length / 2) - wma(src, length), round(sqrt(length)))\n\n\n\n\n//ASSIGN A MOVING AVERAGE RESULT TO A VARIABLE\nshortMA=ma(smoothingShort, pivot, periodShort)\nlongMA=ma(smoothingLong, pivot, periodLong)\nexitMA=ma(smoothingExit, pivot, periodExit)\n\n//PLOT THOSE VARIABLES\nplot(shortMA, linewidth=4, color=color.yellow,title="The Short Moving Average")\nplot(longMA, linewidth=4, color=color.blue,title="The Long Moving Average")\nplot(exitMA, linewidth=1, color=color.red,title="The Exit CrossUnder Moving Average")\n\n\n\n//BUY STRATEGY\nbuy = crossover(shortMA,longMA) ? true : na\nexit = crossunder(close,exitMA) ? true : na\n\n\nstrategy.entry("long",true,when=buy and time_cond)\nstrategy.close("long",when=exit and time_cond)\n\n\nif (not time_cond)\n    strategy.close_all()\n'

class SMBF32C7892B7EB803(PinePortBase, IStrategy):
    source_id = "SM_bf32c7892b7eb803"
    source_file = '移动平均线金叉交易策略Moving-Average-Crossover-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fromDay': 1, 'fromMonth': 1, 'fromYear': 2020, 'toDay': 1, 'toMonth': 1, 'toYear': 2021, 'periodShort': 13, 'smoothingShort': 'EMA', 'periodLong': 48, 'smoothingLong': 'EMA', 'periodExit': 30, 'smoothingExit': 'EMA'}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
