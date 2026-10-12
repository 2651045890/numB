"""batch_011 port of 移动平均数RSI相关性加密货币趋势策略Moving-Average-RSI-Crypto-Correlation-Trend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-04 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\nstrategy(title = "Crypto swing correlation", overlay = true,  pyramiding=1,initial_capital = 1, default_qty_type= strategy.percent_of_equity, default_qty_value = 100, calc_on_order_fills=false, slippage=0,commission_type=strategy.commission.percent,commission_value=0.03)\n\n//time\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2010, title = "From Year", minval = 1970)\n //monday and session \n// To Date Inputs\ntoDay = input(defval = 31, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 12, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2021, title = "To Year", minval = 1970)\n\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n\nuseCorrelation    = input(true, title="Use Correlation candles?")\n\nsymbol = input("BTC_USDT:swap", type=input.symbol)\n\nhaClose = useCorrelation ? security(symbol, timeframe.period, close) : close\nhaOpen  = useCorrelation ? security(symbol, timeframe.period, open) : open\nhaHigh  = useCorrelation ? security(symbol, timeframe.period, high) : high\nhaLow   = useCorrelation ? security(symbol, timeframe.period, low) : low\n\nlength = input( 50 )\noverSold = input( 51 )\noverBought = input( 49 )\n\ns = input(title="Source", defval="haClose", options=["haClose", "haOpen", "haHigh", "haLow"])\n\nprice = s == "haClose" ? haClose: s == "haOpen" ? haOpen : s == "haHigh" ? haHigh : s == "haLow" ? haLow : na\n\nlen = input(8, "Length Moving average", minval=1)\nsrc = price\nma = sma(src, len)\n\n\nvrsi = rsi(price, length)\nlong = crossover(vrsi, overSold) and time_cond and price > ma\nshort = crossunder(vrsi, overBought) and time_cond and price < ma\n\n\ntakeProfit_long=input(1.0, step=0.005)\nstopLoss_long=input(0.1, step=0.005)\ntakeProfit_short=input(0.05, step=0.005)\nstopLoss_short=input(0.03, step=0.005)\n\nstrategy.entry("long",1,when=long)\nstrategy.entry("short",0,when=short)\n\nstrategy.exit("short_tp/sl", "long", profit=close * takeProfit_long / syminfo.mintick, loss=close * stopLoss_long / syminfo.mintick, comment=\'LONG EXIT\',  alert_message = \'closeshort\')\nstrategy.exit("short_tp/sl", "short", profit=close * takeProfit_short / syminfo.mintick, loss=close * stopLoss_short / syminfo.mintick, comment=\'SHORT EXIT\',  alert_message = \'closeshort\')\n'

class SMFFC31C27B4B717D8(PinePortBase, IStrategy):
    source_id = "SM_ffc31c27b4b717d8"
    source_file = '移动平均数RSI相关性加密货币趋势策略Moving-Average-RSI-Crypto-Correlation-Trend-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fromDay': 1, 'fromMonth': 1, 'fromYear': 2010, 'toDay': 31, 'toMonth': 12, 'toYear': 2021, 'useCorrelation': True, 'symbol': 'BTC_USDT:swap', 'length': 50, 'overSold': 51, 'overBought': 49, 's': 'haClose', 'len': 8, 'takeProfit_long': 1.0, 'stopLoss_long': 0.1, 'takeProfit_short': 0.05, 'stopLoss_short': 0.03}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.03
    source_pyramiding = 1
    source_initial_capital = 1
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'exit_order', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
