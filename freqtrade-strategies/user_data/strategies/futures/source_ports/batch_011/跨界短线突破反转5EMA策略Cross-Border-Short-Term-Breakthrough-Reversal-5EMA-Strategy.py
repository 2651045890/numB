"""batch_011 port of 跨界短线突破反转5EMA策略Cross-Border-Short-Term-Breakthrough-Reversal-5EMA-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © samscripter\n\n//@version=5\nstrategy("5 ema strategy",overlay = true,process_orders_on_close = true)\n\n// Choose trade direction\n\nt_dir = input.string("Both", title="Trade Direction",options=["Long", "Short", "Both"],group = \'Trade Direction Set\')\n\nlong_side  = t_dir == "Long" or t_dir == "Both"\nshort_side = t_dir == "Short" or t_dir == "Both"\n\n// number of trade\nmx_num =input.int(4,title = \'number Of trade\',group = \'Maximum Number Of Trade\')\nvar hi =0.0\nvar lo =0.0\n\nvar group_ma1="Ema Set"\n\n//Ema 1\non_ma=input.bool(true,"Enable EMa 1 Plot On/Off"  ,group =group_ma1)\nma_len= input.int(5, minval=1, title="Ema Length",group =group_ma1)\nma_src = input.source(close, title="Ema Source"   ,group = group_ma1)\nma_out = ta.ema(ma_src, ma_len)\n\n// buy and sell ema condition  \nplot(on_ma?ma_out:na, color=color.white, title="MA")\n\n\nif close>ma_out and open>ma_out and low>ma_out and high>ma_out\n    lo:=low\n\nif close<ma_out and open<ma_out and low<ma_out and high<ma_out\n    hi:=high\n    \n// condition when price is crossunder lo take sell and when price crossoing hi take buy \nvar buyp_sl =float(na)\nvar sellp_sl =float(na)\n\n//count number trade since day stra\nvar count_buysell=0\n\nif  close>hi[1] \n    if strategy.position_size==0 and count_buysell<mx_num and long_side\n        strategy.entry(\'El\',strategy.long,comment = \'Long\')\n        count_buysell:=count_buysell+1\n        buyp_sl:=math.min(low,low[1])\n    hi:=na\nif  close<lo[1]\n    if strategy.position_size==0 and count_buysell<mx_num and short_side\n        strategy.entry(\'Es\',strategy.short,comment = \'short\')\n        count_buysell:=count_buysell+1\n        sellp_sl:=math.max(high,high[1])\n    lo:=na\n\n//take profit multiply \n\ntpnew = input.float(title="take profit", step=0.1, defval=1.5, group=\'Tp/SL\')\n\n\n//stop loss previous candle high and previous candle low\nbuy_sl = ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0,buyp_sl , 0)\nsell_sl= ta.valuewhen(strategy.position_size != 0 and strategy.position_size[1] == 0,sellp_sl, 0)\n\n//take profit\ntakeProfit_buy = strategy.position_avg_price - ((buy_sl - strategy.position_avg_price) *tpnew)\ntakeProfit_sell = strategy.position_avg_price - ((sell_sl - strategy.position_avg_price) *tpnew)\n\n\n//  Submit exit orders\nif strategy.position_size > 0\n    strategy.exit(id=\'XL\', stop=buy_sl,limit=takeProfit_buy,comment_loss = \'Long Sl\',comment_profit = \'Long Tp\')\n\nif strategy.position_size < 0\n    strategy.exit(id=\'XS\', stop=sell_sl,limit=takeProfit_sell,comment_loss = \'Short Sl\',comment_profit = \'Short Tp\')\n    \n//plot data\nplot(series=strategy.position_size < 0 ?sell_sl : na, style=plot.style_circles, color=color.red, linewidth=2, title="St red Stop")\nplot(series=strategy.position_size > 0 ?buy_sl  : na, style=plot.style_circles, color=color.green, linewidth=2, title="St green Stop")\n\n\n// plot take profit\nplot(series=strategy.position_size < 0 ? takeProfit_sell : na, style=plot.style_circles, color=color.orange, linewidth=2, title="take profit sell")\nplot(series=strategy.position_size > 0 ? takeProfit_buy: na, style=plot.style_circles, color=color.blue, linewidth=2, title="take profit buy")\n\nif ta.change(time(\'D\'))\n    count_buysell:=0'

class SM4F28C472A9268145(PinePortBase, IStrategy):
    source_id = "SM_4f28c472a9268145"
    source_file = '跨界短线突破反转5EMA策略Cross-Border-Short-Term-Breakthrough-Reversal-5EMA-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'t_dir': 'Both', 'mx_num': 4, 'on_ma': True, 'ma_len': 5, 'tpnew': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
