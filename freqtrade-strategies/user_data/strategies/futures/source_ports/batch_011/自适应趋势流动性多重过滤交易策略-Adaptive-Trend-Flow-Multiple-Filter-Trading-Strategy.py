"""batch_011 port of 自适应趋势流动性多重过滤交易策略-Adaptive-Trend-Flow-Multiple-Filter-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-29 00:00:00\nend: 2025-01-05 00:00:00\nperiod: 45m\nbasePeriod: 45m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Adaptive Trend Flow Strategy with Filters for SPX", overlay=true, max_labels_count=500, \n     initial_capital=1000, commission_type=strategy.commission.cash_per_order, commission_value=0.01, slippage=2,\n     margin_long=20, margin_short=20, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// User-defined inputs for trend logic\natr           = input.int(14, "Main Length", minval=2, group = "Find more strategies like this on pineindicators.com")\nlength        = input.int(2, "Main Length", minval=2)\nsmooth_len    = input.int(2, "Smoothing Length", minval=2)\nsensitivity   = input.float(2.0, "Sensitivity", step=0.1)\n\n// User-defined inputs for SMA filter\nuse_sma_filter = input.bool(true, "Enable SMA Filter?")\nsma_length = input.int(4, "SMA Length", minval=1)\n\n// User-defined inputs for MACD filter\nuse_macd_filter = input.bool(true, "Enable MACD Filter?")\nmacd_fast_length = input.int(2, "MACD Fast Length", minval=1)\nmacd_slow_length = input.int(7, "MACD Slow Length", minval=1)\nmacd_signal_length = input.int(2, "MACD Signal Length", minval=1)\n// User-defined inputs for leverage\nleverage_factor = input.float(4.5, "Leverage Factor", minval=1.0, step=0.1)\nid           = input("besttrader123", title= "Your TradingView username", group = "Automate this strategy with plugpine.com")\nkey           = input("nc739ja84gf", title= "Unique identifier (UID)")\nticker        = input("SPX", title= "Ticker/symbol of your broker")\nbullcolor     = #0097a7\nbearcolor     = #ff195f\nshowbars      = input.bool(true, "Color Bars?")\nshowbg        = input.bool(true, "Background Color?")\nshowsignals   = input.bool(true, "Show Signals?")\n\n\n// Trend calculation functions\ncalculate_trend_levels() =>\n    typical = hlc3\n    fast_ema = ta.ema(typical, length)\n    slow_ema = ta.ema(typical, length * 2)\n    basis = (fast_ema + slow_ema) / 2\n    vol = ta.stdev(typical, length)\n    smooth_vol = ta.ema(vol, smooth_len)\n    upper = basis + (smooth_vol * sensitivity)\n    lower = basis - (smooth_vol * sensitivity)\n    [basis, upper, lower]\n\nget_trend_state(upper, lower, basis) =>\n    var float prev_level = na\n    var int trend = 0\n    if na(prev_level)\n        trend := close > basis ? 1 : -1\n        prev_level := trend == 1 ? lower : upper\n    if trend == 1\n        if close < lower\n            trend := -1\n            prev_level := upper\n        else\n            prev_level := lower\n    else\n        if close > upper\n            trend := 1\n            prev_level := lower\n        else\n            prev_level := upper\n    [trend, prev_level]\n\n[basis, upper, lower] = calculate_trend_levels()\n[trend, level] = get_trend_state(upper, lower, basis)\n\n// SMA filter\nsma_value = ta.sma(close, sma_length)\nsma_condition = use_sma_filter ? close > sma_value : true\n\n// MACD filter\n[macd_line, signal_line, _] = ta.macd(close, macd_fast_length, macd_slow_length, macd_signal_length)\nmacd_condition = use_macd_filter ? macd_line > signal_line : true\n\n// Signal detection with filters\nlong_signal = trend == 1 and trend[1] == -1 and sma_condition and macd_condition\nshort_signal = trend == -1 and trend[1] == 1\n\n// Plotting visuals\np2 = plot(basis, color=trend == 1 ? bullcolor : bearcolor, linewidth=2)\np1 = plot(level, color=close > level ? bullcolor : bearcolor, linewidth=2, style=plot.style_linebr)\n// if showsignals and ta.crossover(close, level)\n//     label.new(bar_index, level, "▲", color=bullcolor, textcolor=chart.bg_color, style=label.style_label_upper_right)\n// if showsignals and ta.crossunder(close, level)\n//     label.new(bar_index, level, "▼", color=bearcolor, textcolor=chart.fg_color, style=label.style_label_lower_right)\n\nqty = strategy.equity / close * leverage_factor\n\n// Automated alerts\nif long_signal\n    alert(\'{"AccountID": "\' + id + \'","Key": "\' + key + \'", "symbol": "\' + ticker + \'", "action": "long", "volume": \' + str.tostring(qty) + \'}\', alert.freq_once_per_bar)\nif short_signal\n    alert(\'{"AccountID": "\' + id + \'","Key": "\' + key + \'", "symbol": "\' + ticker + \'", "action": "closelong"}\', alert.freq_once_per_bar)\n\n// Strategy entries and exits\nif long_signal\n    strategy.entry("Long", strategy.long, qty=qty)\nif short_signal\n    strategy.close("Long")\n\n// Optional SMA and MACD plot\nplot(use_sma_filter ? sma_value : na, color=color.new(color.blue, 80), title="SMA")\nplot(use_macd_filter ? macd_line : na, color=color.new(color.orange, 80), title="MACD Line")\nplot(use_macd_filter ? signal_line : na, color=color.new(color.red, 80), title="Signal Line")\n'

class SM50F0BBF3F02D3780(PinePortBase, IStrategy):
    source_id = "SM_50f0bbf3f02d3780"
    source_file = '自适应趋势流动性多重过滤交易策略-Adaptive-Trend-Flow-Multiple-Filter-Trading-Strategy.md'
    timeframe = '45m'
    can_short = False
    source_defaults = {'atr': 14, 'length': 2, 'smooth_len': 2, 'sensitivity': 2.0, 'use_sma_filter': True, 'sma_length': 4, 'use_macd_filter': True, 'macd_fast_length': 2, 'macd_slow_length': 7, 'macd_signal_length': 2, 'leverage_factor': 4.5, 'id': 'besttrader123', 'key': 'nc739ja84gf', 'ticker': 'SPX', 'showbars': True, 'showbg': True, 'showsignals': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'tuple', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
