"""batch_011 port of 趋势追踪网格策略Trend-Following-Grid-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-01 00:00:00\nend: 2023-12-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © zxcvbnm3260\n\n//@version=5\nstrategy("grid strategy long", overlay=true)\n\n\n// 版本更新记录：\n// v1.0 2021/11/09 只做多、不做空，选择大趋势向上的时间段。网格大小默认为1倍ATR，往下1、2、3个网格吃单，第5个网格止损。空仓时到达往上一个网格则网格整体抬升。（Only go long, not short, choose a time period when the general trend is up. The default grid size is 1x ATR, the next one, two, and three grids will take orders, and the fifth grid will stop loss. When the empty position reaches the upper grid, the grid as a whole rises.）\n\n\nX_ATR = input.float(title=\'网格大小是多少倍ATR？\', defval = 1)\n\n\n// 1.基础变量\nema169 = ta.ema(close, 169)\nema144 = ta.ema(close, 144)\nema12 = ta.ema(close, 12)\n\nema576 = ta.ema(close, 576)\nema676 = ta.ema(close, 676)\n\nplot(ema169, color=color.new(color.orange, 0), linewidth=2)\n// plot(ema144, color=color.orange)\nplot(ema12,  color=color.blue)\n// plot(ema676, color=color.orange, linewidth=1)\n\nmtr = math.max(high - low, math.abs(close[1] - high), math.abs(close[1] - low))\natr = ta.ema(mtr, 30)\n\nis_0930 = hour(time, \'GMT-4\') == 9  and minute(time, \'GMT-4\') == 30\nis_1500 = hour(time, \'GMT-4\') == 15 and minute(time, \'GMT-4\') == 00\nis_1530 = hour(time, \'GMT-4\') == 15 and minute(time, \'GMT-4\') == 30\n\nis_yangxian = close>open\nis_yinxian = close<open\n\n// 2.基本趋势标记\n\nbig_trend  = ema12 >= ema169 ? 1 : 0\nbig_trend2 = ema12 <= ema169 ? 1 : 0\n\n// 背景的变色处理：\nbgcolor(big_trend == 1 ? color.new(color.green, 90) : color.new(color.red, 90) )\n\n// 3.网格点位初始化\n\ngrid_size = atr * X_ATR // 网格大小\n        \nprice_entry1 = open - grid_size*1\nprice_entry2 = open - grid_size*2\nprice_entry3 = open - grid_size*3\nprice_stop_loss = open - grid_size*5\n\nprice_exit1 = price_entry1 + grid_size*1\nprice_exit2 = price_entry2 + grid_size*1\nprice_exit3 = price_entry3 + grid_size*1\n\nqty1 = int(1000/price_entry1)\nqty2 = int(1000/price_entry2)\nqty3 = int(1000/price_entry3)\n\n\n// 标出各种点位\nslm_lines_time(time, price_entry1, price_entry2, price_entry3, price_stop_loss, price_exit1)=>\n    time2 = time + 1000*3600*24*5\n    line.new(time, price_stop_loss, time2, price_stop_loss, color=color.red, xloc = xloc.bar_time, width=2)  // 止损位\n    line.new(time, price_entry1, time2, price_entry1, color=color.green, xloc = xloc.bar_time)  // \n    line.new(time, price_entry2, time2, price_entry2, color=color.green, xloc = xloc.bar_time)  // \n    line.new(time, price_entry3, time2, price_entry3, color=color.green, xloc = xloc.bar_time)  // \n    line.new(time, price_exit1,  time2, price_exit1,  color=color.green, xloc = xloc.bar_time, width=2)  // \n\nslm_lines(time, price_entry1, price_entry2, price_entry3, price_stop_loss, price_exit1)=>\n    line.new(bar_index, price_stop_loss, bar_index[5], price_stop_loss, color=color.red, xloc = xloc.bar_index, width=2)  // 止损位\n    line.new(bar_index, price_entry1, bar_index[5], price_entry1, color=color.green, xloc = xloc.bar_index)  // \n    line.new(bar_index, price_entry2, bar_index[5], price_entry2, color=color.green, xloc = xloc.bar_index)  // \n    line.new(bar_index, price_entry3, bar_index[5], price_entry3, color=color.green, xloc = xloc.bar_index)  // \n    line.new(bar_index, price_exit1,  bar_index[5], price_exit1,  color=color.green, xloc = xloc.bar_index, width=2)  // \n\n\n// 4.网格点位更新和下单\n\nis_entry0 = big_trend==1 and year>=2020\n\nvar is_entry = false\n\n// 未进场时：\nif is_entry0 and not is_entry\n    is_entry := true\n    \n    grid_size := atr * X_ATR // 网格大小\n    \n    price_entry1 := close - grid_size*1\n    price_entry2 := close - grid_size*2\n    price_entry3 := close - grid_size*3\n    price_stop_loss := close - grid_size*5\n    \n    price_exit1 := price_entry1 + grid_size*1\n    price_exit2 := price_entry2 + grid_size*1\n    price_exit3 := price_entry3 + grid_size*1\n    \n    qty1 := int(1000/price_entry1)\n    qty2 := int(1000/price_entry2)\n    qty3 := int(1000/price_entry3)\n    \n    // slm_lines(time, price_entry1, price_entry2, price_entry3, price_stop_loss, price_exit1)\n    \n    strategy.entry("open1", strategy.long, qty1, limit = price_entry1)\n    strategy.entry("open2", strategy.long, qty2, limit = price_entry2)\n    strategy.entry("open3", strategy.long, qty3, limit = price_entry3)\n    \n    strategy.exit("close1", qty = qty1, limit = price_exit1, stop = price_stop_loss)\n    strategy.exit("close2", qty = qty2, limit = price_exit2, stop = price_stop_loss)\n    strategy.exit("close3", qty = qty3, limit = price_exit3, stop = price_stop_loss)\n\n// 已进场的各类情况\n\n// 1.止损\nif is_entry and close <= price_stop_loss\n    strategy.close_all()\n    is_entry := false\n\n// 2.网格抬升\nif is_entry and close >= price_exit1\n    is_entry := false\n        \n\n\n'

class SM53C07567A9A9E92D(PinePortBase, IStrategy):
    source_id = "SM_53c07567a9a9e92d"
    source_file = '趋势追踪网格策略Trend-Following-Grid-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'X_ATR': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'entry_price_order', 'exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
