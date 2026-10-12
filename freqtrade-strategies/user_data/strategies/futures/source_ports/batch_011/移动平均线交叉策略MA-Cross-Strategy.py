"""batch_011 port of 移动平均线交叉策略MA-Cross-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-01 00:00:00\nend: 2024-05-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © syam-mohan-vs @ T7 - wwww.t7wealth.com www.t7trade.com\n//This is an educational code done to describe the fundemantals of pine scritpting language and integration with Indian discount broker Dhan. This strategy is not tested or recommended for live trading. \n\n//@version=5\nstrategy("Pine & Dhan - Moving Average Crossover Strategy", overlay=true)\n\n//Remove excess signals\nexrem(condition1, condition2) =>\n    temp = false\n    temp := na(temp[1]) ? false : not temp[1] and condition1 ? true : temp[1] and condition2 ? false : temp[1]\n    ta.change(temp) == true ? true : false\n\n// Define MA period\nma_period = input(20, title = "MA Length")\n\n// Define target and stop loss levels\ntarget_percentage = input.float(title="Target Profit (%)", defval=2.0)\nstop_loss_percentage = input.float(title="Stop Loss (%)", defval=1.0)\n\n// Calculate the MA\nma = ta.sma(close, ma_period)\n\n// Entry conditions\nlong_entry = close >= ma\nshort_entry = close < ma\n\n// Calculate target and stop loss prices\ntarget_price = long_entry ? strategy.position_avg_price + (close * (target_percentage / 100)) : strategy.position_avg_price - (close * (target_percentage / 100)) \nstop_loss_price = short_entry ? strategy.position_avg_price + (close * (stop_loss_percentage/ 100)) : strategy.position_avg_price - (close * (stop_loss_percentage / 100)) \n\nlong_entry := exrem(long_entry,short_entry)\nshort_entry := exrem(short_entry,long_entry)\n\n// Plot the MA\nplot(ma, color=color.blue, linewidth=2, title="MA")\n\n// Plot the entry and exit signals\nplotshape(long_entry, style=shape.arrowup, color=color.green, size=size.small,location = location.belowbar)\nplotshape(short_entry, style=shape.arrowdown, color=color.red, size=size.small,location = location.abovebar)\n\n//Find absolute value of positon size to exit position properly\nsize = math.abs(strategy.position_size)\n\n//Replace these four JSON strings with those generated from user Dhan account\nlong_msg = \'{"secret":"C0B2u","alertType":"multi_leg_order","order_legs":[{"transactionType":"B","orderType":"MKT","quantity":"1","exchange":"NSE","symbol":"NIFTY1!","instrument":"FUT","productType":"I","sort_order":"1","price":"0"}]}\'\nlong_exit_msg = \'{"secret":"C0B2u","alertType":"multi_leg_order","order_legs":[{"transactionType":"S","orderType":"MKT","quantity":"1","exchange":"NSE","symbol":"NIFTY1!","instrument":"FUT","productType":"M","sort_order":"1","price":"0"}]}\'\nshort_msg = \'{"secret":"C0B2u","alertType":"multi_leg_order","order_legs":[{"transactionType":"S","orderType":"MKT","quantity":"1","exchange":"NSE","symbol":"NIFTY1!","instrument":"FUT","productType":"M","sort_order":"1","price":"0"}]}\'\nshort_exit_msg = \'{"secret":"C0B2u","alertType":"multi_leg_order","order_legs":[{"transactionType":"B","orderType":"MKT","quantity":"1","exchange":"NSE","symbol":"NIFTY1!","instrument":"FUT","productType":"M","sort_order":"1","price":"0"}]}\'\n\n// Submit orders based on signals\nif(strategy.position_size == 0)\n    if long_entry \n        strategy.order("Long", strategy.long,alert_message=long_msg)          \n\n    if short_entry\n        strategy.order("Short", strategy.short,alert_message=short_msg)        \n    \nif(strategy.position_size > 0)\n    \n    if(short_entry)\n        strategy.order("Short", strategy.short, qty = size, alert_message=short_msg)     \n    else\n        strategy.exit("Long Exit", from_entry="Long", qty = size, stop=stop_loss_price, limit= target_price, alert_message=long_exit_msg)\n\nif(strategy.position_size < 0)\n    \n    if(long_entry)\n        strategy.order("Long", strategy.long, qty = size, alert_message=long_msg)    \n    else           \n        strategy.exit("Short Exit", from_entry="Short", qty = size, stop=stop_loss_price, limit= target_price, alert_message=short_exit_msg) \n\n'

class SMCDE5FBCDC63B2BF3(PinePortBase, IStrategy):
    source_id = "SM_cde5fbcdc63b2bf3"
    source_file = '移动平均线交叉策略MA-Cross-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'ma_period': 20, 'target_percentage': 2.0, 'stop_loss_percentage': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
