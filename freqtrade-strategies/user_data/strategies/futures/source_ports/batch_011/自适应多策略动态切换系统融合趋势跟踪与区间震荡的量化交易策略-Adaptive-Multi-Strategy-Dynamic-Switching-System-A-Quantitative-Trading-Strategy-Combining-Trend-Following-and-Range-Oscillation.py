"""batch_011 port of 自适应多策略动态切换系统融合趋势跟踪与区间震荡的量化交易策略-Adaptive-Multi-Strategy-Dynamic-Switching-System-A-Quantitative-Trading-Strategy-Combining-Trend-Following-and-Range-Oscillation.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-17 00:00:00\nend: 2025-01-16 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=6\nstrategy("Supply & Demand Test 1 - Enhanced", overlay=true)\n\n// Inputs\nma_length = input.int(50, title="50-period Moving Average Length", minval=1)\nma_length_fast = input.int(20, title="20-period Moving Average Length", minval=1)\nbb_length = input.int(20, title="Bollinger Bands Length", minval=1)\nbb_std_dev = input.float(2.0, title="Bollinger Bands Std Dev", step=0.1)\nrsi_length = input.int(14, title="RSI Length", minval=1)\nstop_loss_percent = input.float(0.02, title="Stop Loss Percent", step=0.001, minval=0.001)\ntake_profit_trend = input.float(0.06, title="Take Profit Percent (Trend)", step=0.001, minval=0.001)\ntake_profit_range = input.float(0.04, title="Take Profit Percent (Range)", step=0.001, minval=0.001)\n\n// Moving Averages\nma_slow = ta.sma(close, ma_length)\nma_fast = ta.sma(close, ma_length_fast)\n\n// Bollinger Bands\nbb_basis = ta.sma(close, bb_length)\nbb_dev = ta.stdev(close, bb_length)\nbb_upper = bb_basis + bb_std_dev * bb_dev\nbb_lower = bb_basis - bb_std_dev * bb_dev\n\n// RSI\nrsi = ta.rsi(close, rsi_length)\n\n// Market Conditions\nis_trending_up = close > ma_slow\nis_trending_down = close < ma_slow\nis_range_bound = not (is_trending_up or is_trending_down)\n\n// Entry Conditions\nlong_trend_entry = is_trending_up and close >= ma_slow * 1.02\nshort_trend_entry = is_trending_down and close <= ma_slow * 0.98\nlong_ma_crossover = ta.crossover(ma_fast, ma_slow)\nshort_ma_crossover = ta.crossunder(ma_fast, ma_slow)\nlong_range_entry = is_range_bound and close <= bb_lower * 0.97\nshort_range_entry = is_range_bound and close >= bb_upper * 1.03\nlong_rsi_entry = is_range_bound and rsi < 30\nshort_rsi_entry = is_range_bound and rsi > 70\n\n// Entry and Exit Logic\nif long_trend_entry\n    strategy.entry("Long Trend", strategy.long)\n    strategy.exit("Exit Long Trend", from_entry="Long Trend", stop=close * (1 - stop_loss_percent), limit=close * (1 + take_profit_trend))\n    alert("Entered Long Trend", alert.freq_once_per_bar)\n\nif short_trend_entry\n    strategy.entry("Short Trend", strategy.short)\n    strategy.exit("Exit Short Trend", from_entry="Short Trend", stop=close * (1 + stop_loss_percent), limit=close * (1 - take_profit_trend))\n    alert("Entered Short Trend", alert.freq_once_per_bar)\n\nif long_ma_crossover\n    strategy.entry("Long MA Crossover", strategy.long)\n    strategy.exit("Exit Long MA Crossover", from_entry="Long MA Crossover", stop=close * (1 - stop_loss_percent), limit=close * (1 + take_profit_trend))\n    alert("Entered Long MA Crossover", alert.freq_once_per_bar)\n\nif short_ma_crossover\n    strategy.entry("Short MA Crossover", strategy.short)\n    strategy.exit("Exit Short MA Crossover", from_entry="Short MA Crossover", stop=close * (1 + stop_loss_percent), limit=close * (1 - take_profit_trend))\n    alert("Entered Short MA Crossover", alert.freq_once_per_bar)\n\nif long_range_entry\n    strategy.entry("Long Range", strategy.long)\n    strategy.exit("Exit Long Range", from_entry="Long Range", stop=close * (1 - stop_loss_percent), limit=close * (1 + take_profit_range))\n    alert("Entered Long Range", alert.freq_once_per_bar)\n\nif short_range_entry\n    strategy.entry("Short Range", strategy.short)\n    strategy.exit("Exit Short Range", from_entry="Short Range", stop=close * (1 + stop_loss_percent), limit=close * (1 - take_profit_range))\n    alert("Entered Short Range", alert.freq_once_per_bar)\n\nif long_rsi_entry\n    strategy.entry("Long RSI", strategy.long)\n    strategy.exit("Exit Long RSI", from_entry="Long RSI", stop=close * (1 - stop_loss_percent), limit=close * (1 + take_profit_range))\n    alert("Entered Long RSI", alert.freq_once_per_bar)\n\nif short_rsi_entry\n    strategy.entry("Short RSI", strategy.short)\n    strategy.exit("Exit Short RSI", from_entry="Short RSI", stop=close * (1 + stop_loss_percent), limit=close * (1 - take_profit_range))\n    alert("Entered Short RSI", alert.freq_once_per_bar)\n\n// Plotting\nplot(ma_slow, color=color.blue, title="50-period MA")\nplot(ma_fast, color=color.orange, title="20-period MA")\nplot(bb_upper, color=color.red, title="Bollinger Upper")\nplot(bb_lower, color=color.green, title="Bollinger Lower")\nplot(bb_basis, color=color.gray, title="Bollinger Basis")\nhline(70, "Overbought (RSI)", color=color.red, linestyle=hline.style_dotted)\nhline(30, "Oversold (RSI)", color=color.green, linestyle=hline.style_dotted)\n'

class SMD59CE9D7919B157B(PinePortBase, IStrategy):
    source_id = "SM_d59ce9d7919b157b"
    source_file = '自适应多策略动态切换系统融合趋势跟踪与区间震荡的量化交易策略-Adaptive-Multi-Strategy-Dynamic-Switching-System-A-Quantitative-Trading-Strategy-Combining-Trend-Following-and-Range-Oscillation.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'ma_length': 50, 'ma_length_fast': 20, 'bb_length': 20, 'bb_std_dev': 2.0, 'rsi_length': 14, 'stop_loss_percent': 0.02, 'take_profit_trend': 0.06, 'take_profit_range': 0.04}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
