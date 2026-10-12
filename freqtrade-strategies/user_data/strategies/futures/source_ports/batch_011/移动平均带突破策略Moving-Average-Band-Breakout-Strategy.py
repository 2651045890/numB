"""batch_011 port of 移动平均带突破策略Moving-Average-Band-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-17 00:00:00\nend: 2023-09-16 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © TaylorTneh\n//@version=4\n\n// strategy("Moving Average Band Taylor V1",shorttitle="MA Band+",overlay=true,default_qty_type=strategy.cash,default_qty_value=1000,initial_capital=1000,currency=currency.USD,commission_value=.1)\n\nprice = input(close, title="Source")\nmabtype = input(title="Moving Average Type", defval="RMA", options=["SMA", "EMA", "RMA", "WMA"])\nmalen = input(10, "MA Period : 10")\nmagap = input(0.6, "Band Gap : 0.6", minval = -10, maxval = 10, step = 0.1)\nmabup = if mabtype == "SMA"\n    sma(high, malen)\nelse\n    if mabtype == "EMA"\n        ema(high, malen)\n    else\n        if mabtype == "WMA"\n            wma(high, malen)\n        else\n            if mabtype == "RMA"\n                rma(high, malen)\n                    \nmabdn = if mabtype == "SMA"\n    sma(low, malen)\nelse\n    if mabtype == "EMA"\n        ema(low, malen)\n    else\n        if mabtype == "WMA"\n            wma(low, malen)\n        else\n            if mabtype == "RMA"\n                rma(low, malen)\n                    \nupex = mabup * (1 + magap/100)\ndnex = mabdn * (1 - magap/100)\nplot(upex, "Upper MA Band", color.orange)\nplot(dnex, "Lower MA Band", color.orange)\n\n\n//-------------------------------------------- (Strategy)\nstrategy.entry("Long", strategy.long, stop = upex)\nstrategy.entry("Short", strategy.short, stop = dnex)\n//Long Only//strategy.entry("Long", strategy.long, stop = upex)\n//Long Only//strategy.exit("Short", stop = dnex)\n//Short Only//strategy.entry("Short", strategy.short, stop = dnex)\n//Short Only//strategy.exit("Long", stop = upex)\n\n\n//-------------------------------------------- (Take Profit & Stop Lose)\nstopPer = input(500.0, title=\'# Stop Loss %\', type=input.float) / 100\ntakePer = input(500.0, title=\'# Take Profit %\', type=input.float) / 100\n//Determine where you\'ve entered and in what direction\nlongStop = strategy.position_avg_price * (1 - stopPer)\nshortStop = strategy.position_avg_price * (1 + stopPer)\nshortTake = strategy.position_avg_price * (1 - takePer)\nlongTake = strategy.position_avg_price * (1 + takePer)\nif strategy.position_size > 0 \n    strategy.exit(id="L-TP/SL", stop=longStop, limit=longTake)\nif strategy.position_size < 0 \n    strategy.exit(id="S-TP/SL", stop=shortStop, limit=shortTake)\n\n\n//-------------------------------------------- (Sample Time Filter Strategy)\n//fromyear = input(2018, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\n//toyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\n//frommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\n//tomonth = input(10, defval = 10, minval = 01, maxval = 12, title = "To Month")\n//fromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\n//today = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n//strategy.entry("Long", strategy.long, stop = upex, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n//strategy.entry("Short", strategy.short, stop = dnex, when = (time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n//--------------------------------------------\n'

class SM54849F6813BD5211(PinePortBase, IStrategy):
    source_id = "SM_54849f6813bd5211"
    source_file = '移动平均带突破策略Moving-Average-Band-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'mabtype': 'RMA', 'malen': 10, 'magap': 0.6, 'stopPer': 500.0, 'takePer': 500.0}
    source_qty_type = 'cash'
    source_qty_value = 1000
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
