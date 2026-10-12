"""batch_011 port of 移动平均交叉系统Moving-Average-Crossover-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-03 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © gliese581d\n\n//@version=4\nstrategy(title="Moving Averages Testing", overlay=true, precision=2, calc_on_every_tick=false, max_bars_back=5000, pyramiding=2,  \n default_qty_type=strategy.percent_of_equity, default_qty_value=50, commission_type=strategy.commission.percent, initial_capital=10000)\n\n\n//SETTINGS\n\nlongs_on = input(title="Long Trades enabled", defval=true)\nshorts_on = input(title="Short Trades enabled", defval=true)\n\nlong_cond = input(title="Buy/Long Crossover Condition", defval="price x MA1", options=["price x MA1", "price x MA2", "MA1 x MA2"])\nshort_cond = input(title="Sell/Short Crossunder Condition", defval="price x MA2", options=["price x MA1", "price x MA2", "MA1 x MA2"])\n\nma1_type = input(title="Moving Average 1 Type", defval="SMA", options=["SMA", "EMA"])\nma1_len = input(defval=20, title="Moving Average 1 Len", type=input.integer, minval=1, maxval=1000, step=1)\nma2_type = input(title="Moving Average 2 Type", defval="SMA", options=["SMA", "EMA"])\nma2_len = input(defval=30, title="Moving Average 2 Len", type=input.integer, minval=1, maxval=1000, step=1)\n\n\n//MOVING AVERAGES\n\nma_1 = ma1_type == "EMA" ? ema(close, ma1_len) : sma(close, ma1_len)\nma_2 = ma2_type == "EMA" ? ema(close, ma2_len) : sma(close, ma2_len)\n\n\n//STRATEGY\n\n//trade entries\nlong_entry = long_cond == "price x MA1" ? crossover(close, ma_1) : long_cond == "price x MA2" ? crossover(close, ma_2) : long_cond == "MA1 x MA2" ? crossover(ma_1, ma_2) : false\nshort_entry = short_cond == "price x MA1" ? crossunder(close, ma_1) : short_cond == "price x MA2" ? crossunder(close, ma_2) : short_cond == "MA1 x MA2" ? crossunder(ma_1, ma_2) : false\n\nstart_month = input(defval=4, title="Strategy Start Month", type=input.integer, minval=1, maxval=12, step=1)\nstart_year = input(defval=2018, title="Strategy Start Year", type=input.integer, minval=2000, maxval=2025, step=1)\nend_month = input(defval=12, title="Strategy End Month", type=input.integer, minval=1, maxval=12, step=1)\nend_year = input(defval=2020, title="Strategy End Year", type=input.integer, minval=2000, maxval=2025, step=1)\n\nin_time =true\n\nstrategy.entry("Long", strategy.long, when=longs_on and in_time and long_entry)\nstrategy.close("Long", when=longs_on and not shorts_on and short_entry)\n\nstrategy.entry("Short", strategy.short, when=shorts_on and in_time and short_entry)\nstrategy.close("Short", when=shorts_on and not longs_on and long_entry)\n\n\n//PLOTTING\n\n//color background\nlast_entry_was_long = nz(barssince(long_entry)[1], 5000) < nz(barssince(short_entry)[1], 5000)\nbgcol = (longs_on and last_entry_was_long) ? color.green : (shorts_on and not last_entry_was_long) ? color.red : na\nbgcolor(color=bgcol, transp=90)\n\nplot((long_cond == "price x MA1" or long_cond == "MA1 x MA2") or (short_cond == "price x MA1" or short_cond == "MA1 x MA2") ? ma_1 : na, color=color.blue)\nplot((long_cond == "price x MA2" or long_cond == "MA1 x MA2") or (short_cond == "price x MA2" or short_cond == "MA1 x MA2") ? ma_2 : na, color=color.black)\nplotshape(long_entry, style=shape.triangleup, location=location.belowbar, color=color.green)\nplotshape(short_entry, style=shape.triangledown, location=location.abovebar, color=color.red)'

class SMBE6F918EB10720EE(PinePortBase, IStrategy):
    source_id = "SM_be6f918eb10720ee"
    source_file = '移动平均交叉系统Moving-Average-Crossover-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'longs_on': True, 'shorts_on': True, 'long_cond': 'price x MA1', 'short_cond': 'price x MA2', 'ma1_type': 'SMA', 'ma1_len': 20, 'ma2_type': 'SMA', 'ma2_len': 30, 'start_month': 4, 'start_year': 2018, 'end_month': 12, 'end_year': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 50
    source_commission_percent = 0
    source_pyramiding = 2
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
