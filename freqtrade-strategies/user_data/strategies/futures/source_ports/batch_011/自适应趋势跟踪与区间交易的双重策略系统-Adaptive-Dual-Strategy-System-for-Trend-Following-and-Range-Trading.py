"""batch_011 port of 自适应趋势跟踪与区间交易的双重策略系统-Adaptive-Dual-Strategy-System-for-Trend-Following-and-Range-Trading.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-09-01 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("Trend vs Range Trading - Fully Fixed for v6", overlay=true)\n\n// ? Moving Averages (SMA 50 & 200)\nsma50 = ta.sma(close, 50)\nsma200 = ta.sma(close, 200)\n\n// ? Proper ADX Calculation (With Corrected ta.dmi() Parameters)\ndmiLength = 14\nadxSmoothing = 14\n[dmiPlus, dmiMinus, adx] = ta.dmi(dmiLength, adxSmoothing)\n\n// ? Bollinger Bands Calculation (Fixed for v6)\nbb_length = 20\nbb_mult = 2.0\nbb_basis = ta.sma(close, bb_length)\nbb_dev = ta.stdev(close, bb_length)\nbb_upper = bb_basis + (bb_mult * bb_dev)\nbb_lower = bb_basis - (bb_mult * bb_dev)\n\n// ? Additional Indicators (RSI & MACD)\nrsi = ta.rsi(close, 14)\n[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)\n\n// ? ATR for Stop Loss & Take Profit\natr = ta.atr(14)\nstop_loss_mult = 1.5  // Stop Loss Multiplier\ntake_profit_mult = 3.0  // Take Profit Multiplier\n\n// ? Trend vs Range Market Detection\nis_trending = adx > 25\n\n// ? Trend Following Strategy (SMA Cross & Confirmation)\nlong_condition_trend = is_trending and ta.crossover(sma50, sma200) and rsi > 50 and macdLine > signalLine\nshort_condition_trend = is_trending and ta.crossunder(sma50, sma200) and rsi < 50 and macdLine < signalLine\n\n// ? Range Trading Strategy (Bollinger Bands & RSI Confirmation)\nlong_condition_range = not is_trending and ta.crossover(close, bb_lower) and rsi < 40\nshort_condition_range = not is_trending and ta.crossunder(close, bb_upper) and rsi > 60\n\n// ? Stop Loss & Take Profit Calculations\nlong_stop_loss = close - (atr * stop_loss_mult)\nlong_take_profit = close + (atr * take_profit_mult)\nshort_stop_loss = close + (atr * stop_loss_mult)\nshort_take_profit = close - (atr * take_profit_mult)\n\n// ? Execute Trades (With Stop Loss & Take Profit)\nif long_condition_trend\n    strategy.entry("Long_Trend", strategy.long)\n    strategy.exit("Exit_Long_Trend", from_entry="Long_Trend", stop=long_stop_loss, limit=long_take_profit)\n\nif short_condition_trend\n    strategy.entry("Short_Trend", strategy.short)\n    strategy.exit("Exit_Short_Trend", from_entry="Short_Trend", stop=short_stop_loss, limit=short_take_profit)\n\nif long_condition_range\n    strategy.entry("Long_Range", strategy.long)\n    strategy.exit("Exit_Long_Range", from_entry="Long_Range", stop=long_stop_loss, limit=long_take_profit)\n\nif short_condition_range\n    strategy.entry("Short_Range", strategy.short)\n    strategy.exit("Exit_Short_Range", from_entry="Short_Range", stop=short_stop_loss, limit=short_take_profit)\n\n// ? Visual Indicators & Background Color (Trend vs Range)\nbgcolor(is_trending ? color.green : color.blue)\n\n// ? Plot Moving Averages & Bollinger Bands\nplot(sma50, color=color.blue, title="SMA 50")\nplot(sma200, color=color.red, title="SMA 200")\nplot(bb_upper, color=color.green, title="BB Upper")\nplot(bb_lower, color=color.orange, title="BB Lower")\n'

class SM10208AC2B84C8BA4(PinePortBase, IStrategy):
    source_id = "SM_10208ac2b84c8ba4"
    source_file = '自适应趋势跟踪与区间交易的双重策略系统-Adaptive-Dual-Strategy-System-for-Trend-Following-and-Range-Trading.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['tuple', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
