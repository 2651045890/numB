"""batch_012 port of 高级压力反转与K线重叠策略Advanced-Pressure-Reversal-and-Candlestick-Overlap-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-06 00:00:00\nend: 2025-01-04 08:00:00\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Pressure Reversal & Candle Overlap", overlay=true, default_qty_type=strategy.fixed, default_qty_value=0.1)\n \n// Parameters\ntake_profit_percent = 20  // Take Profit Percentage\nqty = 0.1  // Quantity to trade (BTC)\n \n// Candle Definitions\ngreen_candle = close > open\nred_candle = close < open\ncurrent_body = math.abs(close - open)\n \n// Previous Candle Data\nprev_close = ta.valuewhen(green_candle or red_candle, close, 1)\nprev_open = ta.valuewhen(green_candle or red_candle, open, 1)\n \n// Check Candle Overlaps\ngreen_overlaps_red = green_candle and close >= prev_open and open <= prev_close\nred_overlaps_green = red_candle and close <= prev_open and open >= prev_close\n \n// Define Buying and Selling Pressure\nbuying_pressure = green_candle and volume > ta.sma(volume, 20)\nselling_pressure = red_candle and volume > ta.sma(volume, 20)\n \n// Entry Conditions\nlong_entry_pressure = selling_pressure\nlong_entry_overlap = green_overlaps_red\nshort_entry_pressure = buying_pressure\nshort_entry_overlap = red_overlaps_green\n \n// Calculate Take Profit Levels\ntake_profit_level_long = close * (1 + 20 / 100)\ntake_profit_level_short = close * (1 - 20 / 100)\n \n// Strategy Logic\nif (long_entry_pressure or long_entry_overlap)\n    strategy.entry("Buy Long", strategy.long, qty=qty)\n    strategy.exit("TP Long", "Buy Long", limit=take_profit_level_long)\n \nif (short_entry_pressure or short_entry_overlap)\n    strategy.entry("Sell Short", strategy.short, qty=qty)\n    strategy.exit("TP Short", "Sell Short", limit=take_profit_level_short)\n'

class SMKAdvancedPressureReversalandCandlestickOverlapStrategy72de2f(PinePortBase, IStrategy):
    source_id = "SM_72de2f147ce30dd8"
    source_file = '高级压力反转与K线重叠策略Advanced-Pressure-Reversal-and-Candlestick-Overlap-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 0.1
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
