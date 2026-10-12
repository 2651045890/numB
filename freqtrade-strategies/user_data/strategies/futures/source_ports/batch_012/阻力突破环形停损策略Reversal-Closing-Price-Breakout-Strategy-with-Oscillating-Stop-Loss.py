"""batch_012 port of 阻力突破环形停损策略Reversal-Closing-Price-Breakout-Strategy-with-Oscillating-Stop-Loss.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-03 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © EduardoMattje\n\n//@version=4\nstrategy("Reversal closing price", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10, initial_capital=10000)\n\nsrc = input(hl2, "Price source")\norder_direction = input("Both", "Order direction", options=["Both", "Long", "Short"])\n\n// EMA calculation and plot\n\nema_long_period = input(80, "EMA long period")\nema_short_period = input(8, "EMA short period")\nema_long = ema(src, ema_long_period)\nema_short = ema(src, ema_short_period)\nema_bull = ema_short > ema_long\nema_bear = ema_short < ema_long\nplot(ema_long, "EMA long", ema_bull ? color.green : color.red, 3)\nplot(ema_short, "EMA short", ema_bull ? color.green : color.red, 3)\n\n// Settings\n\nrisk_reward_ratio = input(2.0, "Risk to reward ratio", minval=1.0, step=0.1)\nstop_lookback = input(3, "Stoploss candle lookback", minval=1)\nema_cross_stop = input(true, "Close if EMA crosses in oposite direction")\nallow_retracing = input(true, "Allow price retracing")\n\n// RCP calculation\n\nrcp_bull = low[0] < low[1] and low[0] < low[2] and close[0] > close[1]\nrcp_bear = high[0] > high[1] and high[0] > high[2] and close[0] < close[1]\n\n// Order placement\n\nin_market = strategy.position_size != 0\n\nlong_condition = rcp_bull and ema_bull and not in_market and order_direction != "Short"\nshort_condition = rcp_bear and ema_bear and not in_market and order_direction != "Long"\n\nbought = strategy.position_size[0] > strategy.position_size[1] and strategy.position_size[1] == 0\nsold = strategy.position_size[0] < strategy.position_size[1] and strategy.position_size[1] == 0\nclosed = not in_market and in_market[1]\n\nlong_position = strategy.position_size > 0\nshort_position = strategy.position_size < 0\n\nbuy_price = high + syminfo.mintick\nsell_price = low - syminfo.mintick\n\nif long_condition\n    strategy.entry("Long", true, stop=buy_price)\nif short_condition\n    strategy.entry("Short", false, stop=sell_price)\n    \nif allow_retracing\n    better_price_long = barssince(closed) > barssince(long_condition) and barssince(long_condition) >= 1 and not in_market and ema_bull and buy_price < valuewhen(long_condition, buy_price, 0) and buy_price[0] < buy_price[1]\n    if better_price_long\n        strategy.cancel("Long")\n        strategy.entry("Long", true, stop=buy_price)\n    \n    better_price_short = barssince(closed) > barssince(short_condition) and barssince(short_condition) >= 1 and not in_market and ema_bear and sell_price > valuewhen(short_condition, sell_price, 0) and sell_price[0] > sell_price[1]\n    if better_price_short\n        strategy.cancel("Short")\n        strategy.entry("Short", false, stop=sell_price)\n\n// Stoploss orders\n\nstop_price = long_position ? valuewhen(bought, lowest(stop_lookback)[1] - syminfo.mintick, 0) : short_position ? valuewhen(sold, highest(3)[1] + syminfo.mintick, 0) : na\nstop_comment = "Stoploss triggered"\nstrategy.close("Long", low <= stop_price, stop_comment)\nstrategy.close("Short", high >= stop_price, stop_comment)\nplot(stop_price, "Stop price", color.red, 2, plot.style_linebr)\n\n// EMA cross close orders\n\nif ema_cross_stop\n    if long_position and ema_bear\n        strategy.close("Long", comment=stop_comment)\n    if short_position and ema_bull\n        strategy.close("Short", comment=stop_comment)\n\n// Take profit orders\n\nstop_ticks = abs(strategy.position_avg_price - stop_price)\ntake_profit_price = long_position ? valuewhen(bought, strategy.position_avg_price + stop_ticks * risk_reward_ratio, 0) : short_position ? valuewhen(sold, strategy.position_avg_price  - (stop_ticks * risk_reward_ratio), 0) : na\ntarget_comment = "Take profit"\nstrategy.close("Long", high >= take_profit_price, target_comment)\nstrategy.close("Short", low <= take_profit_price, target_comment)\nplot(take_profit_price, "Target price", color.green, 2, plot.style_linebr)\n\n'

class SMReversalClosingPriceBreakoutStrategywithOscillatingStope3c92a(PinePortBase, IStrategy):
    source_id = "SM_e3c92abe92a34ebb"
    source_file = '阻力突破环形停损策略Reversal-Closing-Price-Breakout-Strategy-with-Oscillating-Stop-Loss.md'
    timeframe = '30m'
    can_short = False
    source_defaults = {'src': 'hl2', 'order_direction': 'Both', 'ema_long_period': 80, 'ema_short_period': 8, 'risk_reward_ratio': 2.0, 'stop_lookback': 3, 'ema_cross_stop': True, 'allow_retracing': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
