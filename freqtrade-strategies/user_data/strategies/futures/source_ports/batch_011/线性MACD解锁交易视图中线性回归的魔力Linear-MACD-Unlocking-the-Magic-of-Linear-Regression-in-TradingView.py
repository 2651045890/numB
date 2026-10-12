"""batch_011 port of 线性MACD解锁交易视图中线性回归的魔力Linear-MACD-Unlocking-the-Magic-of-Linear-Regression-in-TradingView.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-07 00:00:00\nend: 2023-12-14 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © stocktechbot\n\n//@version=5\nstrategy("Linear On MACD", overlay=true, margin_long=100, margin_short=100)\n\n\n\nfast_length = input(title="Fast Length", defval=12)\nslow_length = input(title="Slow Length", defval=26)\ntolerance = input.string(title="Risk tolerance", defval = "LOW", options=["LOW", "HIGH"])\n\nchng = 0\nobv = ta.cum(math.sign(ta.change(close)) * volume)\nif close < close[1] and (open < close)\n    chng := 1\nelse if close > close[1]\n    chng := 1\nelse\n    chng := -1\nobvalt = ta.cum(math.sign(chng) * volume)\n//src = input(title="Source", defval=close)\nsrc = obvalt\nsignal_length = input.int(title="Signal Smoothing",  minval = 1, maxval = 50, defval = 9)\nsma_source = input.string(title="Oscillator MA Type",  defval="EMA", options=["SMA", "EMA"])\nsma_signal = input.string(title="Signal Line MA Type", defval="EMA", options=["SMA", "EMA"])\n\n// Calculating\nfast_ma = sma_source == "SMA" ? ta.sma(src, fast_length) : ta.ema(src, fast_length)\nslow_ma = sma_source == "SMA" ? ta.sma(src, slow_length) : ta.ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal == "SMA" ? ta.sma(macd, signal_length) : ta.ema(macd, signal_length)\nhist = macd - signal\n//hline(0, "Zero Line", color=color.new(#787B86, 50))\n//plot(hist, title="Histogram", style=plot.style_columns, color=(hist>=0 ? (hist[1] < hist ? col_grow_above : col_fall_above) : (hist[1] < hist ? col_grow_below : col_fall_below)))\n//plot(macd, title="MACD", color=col_macd)\n//plot(signal, title="Signal", color=col_signal)\n[macdLine, signalLine, histLine] = ta.macd(close, 12, 26, 9)\n\n//Linear Regression\n\nvol = volume\n\n// Function to calculate linear regression\nlinregs(y, x, len) =>\n    ybar = math.sum(y, len)/len\n    xbar = math.sum(x, len)/len\n    b = math.sum((x - xbar)*(y - ybar),len)/math.sum((x - xbar)*(x - xbar),len)\n    a = ybar - b*xbar\n    [a, b]\n\n// Historical stock price data\nprice = close\n\n// Length of linear regression\nlen = input(defval = 21, title = \'Lookback\')\n\n// Calculate linear regression for stock price based on volume\n[a, b] = linregs(price, vol, len)\n\n// Predicted stock price based on volume\npredicted_price = a + b*vol\n\n// Check if predicted price is between open and close\nis_between = open < predicted_price and predicted_price < close\n\n\n// Plot predicted stock price\nplot(predicted_price, color=color.rgb(218, 27, 132), linewidth=2, title="Predicted Stock Price")\nplot(ta.vwma(predicted_price,len), color=color.rgb(199, 43, 64), linewidth=2, title="Predicted Stock Price")\n\n//BUY Signal\nlincrossunder = close > predicted_price\nmacdrise = ta.rising(macd,2)\n//macdvollong = ta.crossover(macd, signal)\n//macdlong = ta.crossover(macdLine, signalLine)\nmacdvollong = macd > signal\nmacdlong = macdLine > signalLine\nlongCondition=false\nif macdlong and macdvollong and is_between and ta.rising(predicted_price,1)\n    longCondition := true\n\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n//Sell Signal\nlincrossover = close < predicted_price\nmacdfall = ta.falling(macd,1)\nmacdsell = macd < signal\nshortCondition = false\nrisklevel = predicted_price\nif (tolerance == "HIGH")\n    risklevel := ta.vwma(predicted_price,len)\n\n\nif macdfall and macdsell and (macdLine < signalLine) and (close < risklevel)\n    shortCondition := true\n\n\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)\n'

class SMA71A59208BF9CAD1(PinePortBase, IStrategy):
    source_id = "SM_a71a59208bf9cad1"
    source_file = '线性MACD解锁交易视图中线性回归的魔力Linear-MACD-Unlocking-the-Magic-of-Linear-Regression-in-TradingView.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'fast_length': 12, 'slow_length': 26, 'tolerance': 'LOW', 'signal_length': 9, 'sma_source': 'EMA', 'sma_signal': 'EMA', 'len': 21}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
