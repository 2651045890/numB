"""batch_011 port of 结合布林带与RSI的自适应震荡趋势交易策略-Adaptive-Oscillation-Trend-Trading-Strategy-with-Bollinger-Bands-and-RSI-Integration.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-01 00:00:00\nend: 2024-10-31 23:59:59\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("[ETH] Optimized Trend Strategy", shorttitle="Lorenzo-SuperScalping", overlay=true, pyramiding=3, initial_capital=100000, currency=currency.USD)\n\n// === Input Parameters === //\ntrade_size = input.float(1.0, title="Trade Size (ETH)")\nrsi_length = input.int(14, minval=1, title="RSI Length")\nbb_length = input.int(20, minval=1, title="Bollinger Bands Length")\nbb_mult = input.float(2.0, title="Bollinger Bands Multiplier")\nmacd_fast = input.int(12, minval=1, title="MACD Fast Length")\nmacd_slow = input.int(26, minval=1, title="MACD Slow Length")\nmacd_signal = input.int(9, minval=1, title="MACD Signal Length")\n\n// === Indicators === //\n// RSI\nrsi = ta.rsi(close, rsi_length)\n\n// Bollinger Bands\nbasis = ta.sma(close, bb_length)\ndev = ta.stdev(close, bb_length) * bb_mult\nupper_band = basis + dev\nlower_band = basis - dev\nplot(basis, color=color.blue, title="BB Basis")\nplot(upper_band, color=color.red, title="BB Upper")\nplot(lower_band, color=color.green, title="BB Lower")\n\n// MACD\n[macd_line, signal_line, _] = ta.macd(close, macd_fast, macd_slow, macd_signal)\nmacd_cross_up = ta.crossover(macd_line, signal_line)\nmacd_cross_down = ta.crossunder(macd_line, signal_line)\n\n// === Signal Control Variables === //\nvar bool last_signal_buy = na\nvar int last_trade_bar = na\n\n// === Buy Signal Condition === //\n// - RSI below 45\n// - Price near or below the lower Bollinger Band\n// - MACD crossover\nbuy_signal = (rsi < 45 and close < lower_band * 1.02 and macd_cross_up)\n\n// === Sell Signal Condition === //\n// - RSI above 55\n// - Price near or above the upper Bollinger Band\n// - MACD crossunder\nsell_signal = (rsi > 55 and close > upper_band * 0.98 and macd_cross_down)\n\n// Ensure enough bars between trades\nmin_bars_between_trades = input.int(15, title="Minimum Bars Between Trades")\ntime_elapsed = na(last_trade_bar) or (bar_index - last_trade_bar) >= min_bars_between_trades\n\n// === Execute Trades with Conditions === //\ncan_buy = buy_signal and (na(last_signal_buy) or not last_signal_buy) and time_elapsed\ncan_sell = sell_signal and (not na(last_signal_buy) and last_signal_buy) and time_elapsed\n\nif (can_buy)\n    // Close any existing short position before opening a long\n    if strategy.position_size < 0\n        strategy.close("Short")\n\n    strategy.entry("Long", strategy.long, qty=trade_size)\n    last_signal_buy := true\n    last_trade_bar := bar_index\n\nif (can_sell)\n    // Close any existing long position and open a short position\n    if strategy.position_size > 0\n        strategy.close("Long")\n\n    strategy.entry("Short", strategy.short, qty=trade_size)\n    last_signal_buy := false\n    last_trade_bar := bar_index\n\n// === Plot Buy and Sell Signals === //\nplotshape(series=can_buy, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=can_sell, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// === RSI Levels for Visualization === //\nhline(45, "RSI Buy Level", color=color.green, linewidth=1, linestyle=hline.style_dotted)\nhline(55, "RSI Sell Level", color=color.red, linewidth=1, linestyle=hline.style_dotted)\n\n// Plot the RSI for reference\nplot(rsi, title="RSI", color=color.purple)'

class SM088E8E9DB8B9D9C0(PinePortBase, IStrategy):
    source_id = "SM_088e8e9db8b9d9c0"
    source_file = '结合布林带与RSI的自适应震荡趋势交易策略-Adaptive-Oscillation-Trend-Trading-Strategy-with-Bollinger-Bands-and-RSI-Integration.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'trade_size': 1.0, 'rsi_length': 14, 'bb_length': 20, 'bb_mult': 2.0, 'macd_fast': 12, 'macd_slow': 26, 'macd_signal': 9, 'min_bars_between_trades': 15}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 3
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
