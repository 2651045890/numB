"""batch_012 port of 量化交易价格突破策略Quantitative-Trading-Price-Breakthrough-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-15 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=5\nstrategy(title="Scalping Trading System Crypto and Stocks", overlay=true)\nsrc = input(low, title="Source")\n\n//sma and ema\nlen = input.int(25, minval=1, title="Length SMA" , group="Moving Averages")\nlen2 = input.int(200, minval=1, title="Length EMA", group="Moving Averages")\n\nout = ta.sma(src, len)\nout2 = ta.ema(src, len2)\n\n\n//keltner\nlengthk = input.int(10, minval=1, title="Length Keltner Channel",group="Keltner")\nmult = input(2.0, "Multiplier",group="Keltner")\nBandsStyle = input.string("Average True Range", options = ["Average True Range", "True Range", "Range"], title="Bands Style",group="Keltner")\natrlength = input(14, "ATR Length",group="Keltner")\n\nma = ta.sma(src, lengthk)\nrangema = BandsStyle == "True Range" ? ta.tr(true) : BandsStyle == "Average True Range" ? ta.atr(atrlength) : ta.rma(high - low, lengthk)\nupper = ma + rangema * mult\nlower = ma - rangema * mult\n\n//stoch\nperiodK = input.int(10, title="%K Length", minval=1,group="Stochastic")\nsmoothK = input.int(1, title="%K Smoothing", minval=1,group="Stochastic")\nperiodD = input.int(1, title="%D Smoothing", minval=1,group="Stochastic")\nk = ta.sma(ta.stoch(close, high, low, periodK), smoothK)\nd = ta.sma(k, periodD)\n\n//macd 1\nfast_length = input(title="Fast Length MACD", defval=4,group="MACD Fast")\nslow_length = input(title="Slow Length MACD", defval=34,group="MACD Fast")\nsignal_length = input.int(title="Signal Smoothing MACD",  minval = 1, maxval = 50, defval = 5,group="MACD Fast")\nsma_source = input.string(title="Oscillator MA Type MACD",  defval="EMA", options=["SMA", "EMA"],group="MACD Fast")\nsma_signal = input.string(title="Signal Line MA Type MACD", defval="EMA", options=["SMA", "EMA"],group="MACD Fast")\n\nfast_ma = sma_source == "SMA" ? ta.sma(src, fast_length) : ta.ema(src, fast_length)\nslow_ma = sma_source == "SMA" ? ta.sma(src, slow_length) : ta.ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal == "SMA" ? ta.sma(macd, signal_length) : ta.ema(macd, signal_length)\nhist = macd - signal\n\n\n\n\nlong= close > out and close < upper and close > lower and hist < 0 and k < 50 and close > out2 \n\nshort= close < out and close < upper and close > lower and hist > 0 and k > 50 and close < out2 \n\nstrategy.entry("long",strategy.long,when= long)\n\nstrategy.entry("short",strategy.short,when=short)\n\n'

class SMQuantitativeTradingPriceBreakthroughStrategy680d46(PinePortBase, IStrategy):
    source_id = "SM_680d4630a8e5dea5"
    source_file = '量化交易价格突破策略Quantitative-Trading-Price-Breakthrough-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'src': 'low', 'len': 25, 'len2': 200, 'lengthk': 10, 'mult': 2.0, 'BandsStyle': 'Average True Range', 'atrlength': 14, 'periodK': 10, 'smoothK': 1, 'periodD': 1, 'fast_length': 4, 'slow_length': 34, 'signal_length': 5, 'sma_source': 'EMA', 'sma_signal': 'EMA'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
