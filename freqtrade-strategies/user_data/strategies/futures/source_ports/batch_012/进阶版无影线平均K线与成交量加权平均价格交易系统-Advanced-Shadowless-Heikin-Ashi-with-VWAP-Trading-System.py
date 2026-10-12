"""batch_012 port of 进阶版无影线平均K线与成交量加权平均价格交易系统-Advanced-Shadowless-Heikin-Ashi-with-VWAP-Trading-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-07-16 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Buy and Sell Signal with VWAP and Timed Exit", overlay=true)\n\n// VWAP Calculation\nvwap = ta.vwap(close)\n\n// Heikin-Ashi Formula\nvar float heikin_open = na\nvar float heikin_close = na\n\nheikin_open := na(heikin_open[1]) ? (open + close) / 2 : (heikin_open[1] + heikin_close[1]) / 2\nheikin_close := (open + high + low + close) / 4\nheikin_high = math.max(high, math.max(heikin_open, heikin_close))\nheikin_low = math.min(low, math.min(heikin_open, heikin_close))\n\n// Conditions for Sell (Red Heikin-Ashi with no upper shadow) and Buy (Green Heikin-Ashi with no lower shadow)\nno_upper_shadow = heikin_high == math.max(heikin_open, heikin_close)\nno_lower_shadow = heikin_low == math.min(heikin_open, heikin_close)\n\n// Condition for red (sell) and green (buy) Heikin-Ashi candles\nis_red_candle = heikin_close < heikin_open\nis_green_candle = heikin_close > heikin_open\n\n// Buy and Sell Signal Conditions\nsell_signal = is_red_candle and no_upper_shadow and close < vwap\nbuy_signal = is_green_candle and no_lower_shadow and close > vwap\n\n// Check current time (for 15:01 IST)\nis_after_1501 = (hour == 15 and minute > 1) or (hour > 15)\n\n// Check for open positions\nopen_sell_position = strategy.position_size < 0\nopen_buy_position = strategy.position_size > 0\n\n// Trigger Sell order only if no open sell position exists and time is before 15:01, and price is below VWAP\nif sell_signal and not open_sell_position and not is_after_1501\n    strategy.entry("Sell", strategy.short)\n\n// Trigger Buy order only if no open buy position exists and time is before 15:01, and price is above VWAP\nif buy_signal and not open_buy_position and not is_after_1501\n    strategy.entry("Buy", strategy.long)\n\n// Define exit condition for Sell (opposite of Buy conditions)\nexit_sell_condition = false\n\nif open_sell_position\n    entry_price = strategy.position_avg_price  // Get the average entry price for Sell\n    current_price = close  // Current market price for Sell\n\n    // Exit conditions for Sell\n    exit_sell_condition := current_price > entry_price or entry_price - current_price >= 50\n\n    // Exit if conditions are met\n    if exit_sell_condition\n        strategy.close("Sell")\n\n// Define exit condition for Buy (opposite of Sell conditions)\nexit_buy_condition = false\n\nif open_buy_position\n    entry_price = strategy.position_avg_price  // Get the average entry price for Buy\n    current_price = close  // Current market price for Buy\n\n    // Exit conditions for Buy\n    exit_buy_condition := current_price < entry_price or current_price - entry_price >= 50\n\n    // Exit if conditions are met\n    if exit_buy_condition\n        strategy.close("Buy")\n\n// Exit at 15:01 IST for both Buy and Sell if not already exited\nif (open_sell_position or open_buy_position) and (hour == 15 and minute == 1)\n    strategy.close("Sell")\n    strategy.close("Buy")\n\n// Plot VWAP\nplot(vwap, color=color.blue, linewidth=2, title="VWAP")\n\n// Plot Heikin-Ashi Candles\nplotcandle(heikin_open, heikin_high, heikin_low, heikin_close, color = is_red_candle ? color.red : (is_green_candle ? color.green : color.gray))\n\n// Plot Sell signal on the chart\nplotshape(sell_signal and not open_sell_position and not is_after_1501, style=shape.labeldown, location=location.abovebar, color=color.red, text="SELL", size=size.small)\n\n// Plot Buy signal on the chart\nplotshape(buy_signal and not open_buy_position and not is_after_1501, style=shape.labelup, location=location.belowbar, color=color.green, text="BUY", size=size.small)\n\n// Plot Exit signals on the chart\nplotshape(exit_sell_condition and open_sell_position, style=shape.labelup, location=location.belowbar, color=color.blue, text="EXIT SELL", size=size.small)\nplotshape(exit_buy_condition and open_buy_position, style=shape.labeldown, location=location.abovebar, color=color.blue, text="EXIT BUY", size=size.small)\n\n'

class SMKAdvancedShadowlessHeikinAshiwithVWAPTradingSystem91eb43(PinePortBase, IStrategy):
    source_id = "SM_91eb43e258426b4d"
    source_file = '进阶版无影线平均K线与成交量加权平均价格交易系统-Advanced-Shadowless-Heikin-Ashi-with-VWAP-Trading-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
