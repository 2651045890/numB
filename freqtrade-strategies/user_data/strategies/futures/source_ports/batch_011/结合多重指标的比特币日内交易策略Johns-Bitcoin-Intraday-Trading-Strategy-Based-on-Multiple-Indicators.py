"""batch_011 port of 结合多重指标的比特币日内交易策略Johns-Bitcoin-Intraday-Trading-Strategy-Based-on-Multiple-Indicators.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-29 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n//@version=5\nstrategy(\'John Day Stop Loss\', overlay=false, pyramiding=1, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, currency=\'USD\', precision=2)\nstrategy.risk.allow_entry_in(strategy.direction.long) \n\nfrom_day = input.int(defval=1, title=\'From Day\', minval=1)\nfrom_month = input.int(defval=1, title=\'From Month\', minval=1)\nfrom_year = input.int(defval=2021, title=\'From Year\', minval=2020)\nto_day = input.int(defval=1, title=\'To Day\', minval=1)\nto_month = input.int(defval=1, title=\'To Month\', minval=1)\nto_year = input.int(defval=2025, title=\'To Year\', minval=2020)\n\ntime_cond = time > timestamp(from_year, from_month, from_day, 00, 00) and time < timestamp(to_year, to_month, to_day, 00, 00)\n//time_cond = true\n\n//Stop Loss\nlongProfitPerc = input.float(title="Stop Loss Profit (%)", defval=2.1) / 100\nlongExitPrice  = strategy.position_avg_price * (1 - longProfitPerc)\n\n//RSI - yellow\nup = ta.rma(math.max(ta.change(close), 0), 14)\ndown = ta.rma(-math.min(ta.change(close), 0), 14)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\nplot(rsi, "RSI", color=#00FFFF)\nbuy_rsi = true // rsi < 40\nsell_rsi = true //rsi > 70\n\n//MFI - cyan\nmf = ta.mfi(hlc3, 14)\nplot(mf, "MF", color=#FFFF00)\nbuy_mfi = mf < input.int(defval=23, title=\'Max MF\', minval=1)\nsell_mfi = mf > input.int(defval=80, title=\'Min MF\', minval=1)\n\n//Stoch RSI\nOverBought_StochRSI = input(80)\nOverSold_StochRSI = input(34)\nsmoothK = input.int(3, "K", minval=1)\nsmoothD = input.int(2, "D", minval=1)\nlengthRSI = input.int(14, "RSI Length", minval=1)\nlengthStoch = input.int(14, "Stochastic Length", minval=1)\nsrcRSI = input(close, title="RSI Source")\nrsi1 = ta.rsi(srcRSI, lengthRSI)\nkStochRSI = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)\nd = ta.sma(kStochRSI, smoothD)\nco = ta.crossover(kStochRSI,d)\ncu = ta.crossunder(kStochRSI,d)\n\nbuy_stochRSI = co and kStochRSI < OverSold_StochRSI\nsell_stochRSI = cu and kStochRSI > OverBought_StochRSI\n\nplot(kStochRSI, "K", color=#2962FF)\nplot(d, "D", color=#FF6D00)\nh0 = hline(OverBought_StochRSI, "Upper Band", color=#787B86)\nh1 = hline(OverSold_StochRSI, "Lower Band", color=#787B86)\nfill(h0, h1, color=color.rgb(33, 150, 243, 90), title="Background")\n\n//MACD\n// Getting inputs\nfast_length = input(title="Fast Length", defval=12)\nslow_length = input(title="Slow Length", defval=26)\nsrc = input(title="Source", defval=close)\nsignal_length = input.int(title="Signal Smoothing",  minval = 1, maxval = 50, defval = 9)\nsma_source = input.string(title="Oscillator MA Type",  defval="EMA", options=["SMA", "EMA"])\nsma_signal = input.string(title="Signal Line MA Type", defval="EMA", options=["SMA", "EMA"])\n// Plot colors\n//col_macd = input(#2962FF, "MACD Line\u2003\u2004", group="Color Settings", inline="MACD")\n//col_signal = input(#FF6D00, "Signal Line\u2003\u2006", group="Color Settings", inline="Signal")\n//col_grow_above = input(#26A69A, "Above\u2004\u2004\u2005Grow", group="Histogram", inline="Above")\n//col_fall_above = input(#B2DFDB, "Fall", group="Histogram", inline="Above")\n//col_grow_below = input(#FFCDD2, "Below\u2003Grow", group="Histogram", inline="Below")\n//col_fall_below = input(#FF5252, "Fall", group="Histogram", inline="Below")\n// Calculating\nfast_ma = sma_source == "SMA" ? ta.sma(src, fast_length) : ta.ema(src, fast_length)\nslow_ma = sma_source == "SMA" ? ta.sma(src, slow_length) : ta.ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal == "SMA" ? ta.sma(macd, signal_length) : ta.ema(macd, signal_length)\nhist = macd - signal\nbuy_MACD = macd < signal and hist < 0 \nsell_MACD = macd > signal and hist > 0 \n\n//buy_MACD = true \n//sell_MACD = true\n\n//plot(hist, title="Histogram", style=plot.style_columns, color=(hist>=0 ? (hist[1] < hist ? col_grow_above : col_fall_above) : (hist[1] < hist ? col_grow_below : col_fall_below)))\n//plot(macd, title="MACD", color=col_macd)\n//plot(signal, title="Signal", color=col_signal)\n\nsessionColor = color(na)\nif time_cond\n\n    if (not na(kStochRSI) and not na(d))\n        cmt = str.tostring(close)\n    \tif (buy_stochRSI and buy_MACD and buy_mfi and buy_rsi)\n    \t\tstrategy.entry("BUY", strategy.long, comment=\'BUY @ \' + cmt)\n    \t\tif longProfitPerc != 0\n    \t\t    strategy.exit(id="x", stop=longExitPrice, comment=\'EXIT @ \' + str.tostring(longExitPrice))\n        \tsessionColor := input.color(#0000FF, "buy") //red\n    \tif (sell_stochRSI and sell_MACD and sell_mfi and sell_rsi)\n    \t\tstrategy.entry("SELL", strategy.short, comment=\'SELL @ \' + cmt)\n    \t\tsessionColor := input.color(#FF0000, "sell") //green\n    \t\nbgcolor(sessionColor)'

class SM41451F503E435C1C(PinePortBase, IStrategy):
    source_id = "SM_41451f503e435c1c"
    source_file = '结合多重指标的比特币日内交易策略Johns-Bitcoin-Intraday-Trading-Strategy-Based-on-Multiple-Indicators.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'from_day': 1, 'from_month': 1, 'from_year': 2021, 'to_day': 1, 'to_month': 1, 'to_year': 2025, 'longProfitPerc': 2.1, 'OverBought_StochRSI': 80, 'OverSold_StochRSI': 34, 'smoothK': 3, 'smoothD': 2, 'lengthRSI': 14, 'lengthStoch': 14, 'fast_length': 12, 'slow_length': 26, 'signal_length': 9, 'sma_source': 'EMA', 'sma_signal': 'EMA'}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
