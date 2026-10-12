"""batch_012 port of 黄金交叉凯尔特通道趋势跟踪策略Golden-Cross-Keltner-Channel-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-26 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © OversoldPOS\n\n//@version=5\n// strategy("Keltner Channel Strategy by OversoldPOS", overlay=true,initial_capital = 100000,default_qty_type = strategy.percent_of_equity,default_qty_value = 10, commission_type = strategy.commission.cash_per_order, commission_value = 7)\n\n// Parameters\nlength = input(21, title="MA Length")\nEntrymult = input(1, title="Entry ATR")\nprofit_mult = input(4, title="Profit Taker")\nexit_mult = input(-1, title="Exit ATR")\n\n// Moving Average Type Input\nma_type = input.string("SMA", title="Moving Average Type", options=["SMA", "EMA", "WMA"])\n\n// Calculate Keltner Channels for different ATR multiples\natr_value = ta.atr(length)\n\nbasis = switch ma_type\n    "SMA" => ta.sma(close, length)\n    "EMA" => ta.ema(close, length)\n    "WMA" => ta.wma(close, length)\n \n\n//\nEntryKeltLong = basis + Entrymult * ta.atr(10)\nEntryKeltShort = basis - Entrymult * ta.atr(10)\nupper_channel1 = basis + 1 * ta.atr(10)\nlower_channel1 = basis - 1 * ta.atr(10)\nupper_channel2 = basis + 2 * ta.atr(10)\nlower_channel2 = basis - 2 * ta.atr(10)\nupper_channel3 = basis + 3 * ta.atr(10)\nlower_channel3 = basis - 3 * ta.atr(10)\nupper_channel4 = basis + 4 * ta.atr(10)\nlower_channel4 = basis - 4 * ta.atr(10)\n\n// Entry condition parameters\nlong_entry_condition = input(true, title="Long Positions")\nshort_entry_condition = input(true, title="Enable Short Positions")\n\n// Additional conditions for long and short entries\nis_long_entry = ta.ema(close, 20) > ta.ema(close, 50)\nis_short_entry = ta.ema(close, 20) < ta.ema(close, 50)\n\n// Additional conditions for long and short entries\nMAShort =  input(50, title="Short MA for Golden Cross")\nMALong =  input(200, title="Long MA for Golden Cross")\nis_long_entry2 = ta.ema(close, MAShort) > ta.ema(close, MALong)\nis_short_entry2 = ta.ema(close, MAShort) < ta.ema(close, MALong)\n\n// Exit condition parameters\nlong_exit_condition1_enabled = input(true, title="Enable Long Profit Taker")\nlong_exit_condition2_enabled = input(true, title="Enable Long Stop")\nshort_exit_condition1_enabled = input(true, title="Enable Short Profit Taker")\nshort_exit_condition2_enabled = input(true, title="Enable Short Stop")\n\n// Take Profit condition parameters\ntake_profit_enabled = input(true, title="Enable Take Profit Condition")\n\nTakeprofit = basis + profit_mult * atr_value\nSTakeprofit = basis - profit_mult * atr_value\n\n// Long entry condition\nlong_condition = long_entry_condition and ta.crossover(close, EntryKeltLong) and is_long_entry2\n\n// Short entry condition\nshort_condition = short_entry_condition and ta.crossunder(close, EntryKeltShort) and is_short_entry2\n\n// Exit conditions\nlong_exit_condition1 = long_exit_condition1_enabled and close > Takeprofit\nlong_exit_condition2 = long_exit_condition2_enabled and close < basis + exit_mult * atr_value\nshort_exit_condition1 = short_exit_condition1_enabled and close < STakeprofit\nshort_exit_condition2 = short_exit_condition2_enabled and close > basis - exit_mult * atr_value\n\n// Strategy logic\nif (long_condition)\n    strategy.entry("Long", strategy.long)\nif (short_condition)\n    strategy.entry("Short", strategy.short)\n\nif (long_exit_condition1 or long_exit_condition2)\n    strategy.close("Long")\n\nif (short_exit_condition1 or short_exit_condition2)\n    strategy.close("Short")\n\n// Moving Averages\nvar float MA1 = na\nvar float MA2 = na\n\nif (ma_type == "SMA")\n    MA1 := ta.sma(close, MAShort)\n    MA2 := ta.sma(close, MALong)\nelse if (ma_type == "EMA")\n    MA1 := ta.ema(close, MAShort)\n    MA2 := ta.ema(close, MALong)\nelse if (ma_type == "WMA")\n    MA1 := ta.wma(close, MAShort)\n    MA2 := ta.wma(close, MALong)\n\n// Plotting Keltner Channels with adjusted transparency\ntransparentColor = color.rgb(255, 255, 255, 56)\n\nplot(upper_channel1, color=transparentColor, title="Upper Channel 1")\nplot(lower_channel1, color=transparentColor, title="Lower Channel 1")\nplot(upper_channel2, color=transparentColor, title="Upper Channel 2")\nplot(lower_channel2, color=transparentColor, title="Lower Channel 2")\nplot(upper_channel3, color=transparentColor, title="Upper Channel 3")\nplot(lower_channel3, color=transparentColor, title="Lower Channel 3")\nplot(upper_channel4, color=transparentColor, title="Upper Channel 4")\nplot(lower_channel4, color=transparentColor, title="Lower Channel 4")\nplot(basis, color=color.white, title="Basis")\nplot(MA1, color=color.rgb(4, 248, 216), linewidth=2, title="Middle MA")\nplot(MA2, color=color.rgb(220, 7, 248), linewidth=2, title="Long MA")\n\n'

class SMGoldenCrossKeltnerChannelTrendFollowingStrategyccdea0(PinePortBase, IStrategy):
    source_id = "SM_ccdea09a7624c549"
    source_file = '黄金交叉凯尔特通道趋势跟踪策略Golden-Cross-Keltner-Channel-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 21, 'Entrymult': 1, 'profit_mult': 4, 'exit_mult': -1, 'ma_type': 'SMA', 'long_entry_condition': True, 'short_entry_condition': True, 'MAShort': 50, 'MALong': 200, 'long_exit_condition1_enabled': True, 'long_exit_condition2_enabled': True, 'short_exit_condition1_enabled': True, 'short_exit_condition2_enabled': True, 'take_profit_enabled': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 7
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
