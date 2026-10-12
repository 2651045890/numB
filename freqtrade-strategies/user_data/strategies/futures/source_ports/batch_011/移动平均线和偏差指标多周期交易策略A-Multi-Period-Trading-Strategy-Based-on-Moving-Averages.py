"""batch_011 port of 移动平均线和偏差指标多周期交易策略A-Multi-Period-Trading-Strategy-Based-on-Moving-Averages.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//\n//@author Alorse\n//@version=4\nstrategy("MACD + BB + RSI [Alorse]", shorttitle="BB + MACD + RSI [Alorse]", overlay=true, pyramiding=0, currency=currency.USD, default_qty_type=strategy.percent_of_equity, initial_capital=1000, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.01) \n\ntxtVer = "1.0.1"\nversion = input(title="Version", type=input.string, defval=txtVer, options=[txtVer], tooltip="This is informational only, nothing will change.")\nsrc = input(title="Source", type=input.source, defval=close)\n\n// MACD\nfast_length = input(title="Fast Length", type=input.integer, defval=12, group="MACD")\nslow_length = input(title="Slow Length", type=input.integer, defval=26, group="MACD")\nsignal_length = input(title="Signal Smoothing", type=input.integer, minval = 1, maxval = 50, defval = 9, group="MACD")\nsma_source = input(title="Oscillator MA Type", type=input.string, defval="EMA", options=["SMA", "EMA"], group="MACD")\nsma_signal = input(title="Signal Line MA Type", type=input.string, defval="EMA", options=["SMA", "EMA"], group="MACD")\nfast_ma = sma_source == "SMA" ? sma(src, fast_length) : ema(src, fast_length)\nslow_ma = sma_source == "SMA" ? sma(src, slow_length) : ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal == "SMA" ? sma(macd, signal_length) : ema(macd, signal_length)\n\n// Bollinger Bands\nbbGroup = "Bollindger Bands"\nlength = input(20, title="Length", group=bbGroup)\nmult = input(2.0, title="StdDev", minval=0.001, maxval=5, group=bbGroup)\n\nbasis = sma(src, length)\ndev = mult * stdev(src, length)\nupper = basis + dev\nlower = basis - dev\n\n// RSI\nrsiGroup = "RSI"\nlenRSI = input(14, title="Length", minval=1, group=rsiGroup)\n// lessThan = input(50, title="Less than", minval=1 , maxval=100, group=rsiGroup)\nRSI = rsi(src, lenRSI)\n\n// Strategy Conditions\nbuy = crossover(macd, signal) and RSI < 50 and close < basis\nsell = RSI > 70 and close > upper\n\n\n// Stop Loss\nslGroup = "Stop Loss"\nuseSL = input(false, title="╔══════\u2004\u2004\u2005Enable\u2004\u2004\u2005══════╗", group=slGroup, tooltip="If you are using this strategy for Scalping or Futures market, we do not recommend using Stop Loss.")\nSLbased = input(title="Based on", type=input.string, defval="Percent", options=["ATR", "Percent"], group=slGroup, tooltip="ATR: Average True Range\\nPercent: eg. 5%.")\nmultiATR = input(10.0, title="ATR\u2004\u2004\u2005Mult", type=input.float, group=slGroup, inline="atr")\nlengthATR = input(14, title="Length", type=input.integer, group=slGroup, inline="atr")\nSLPercent = input(10, title="Percent", type=input.float, group=slGroup) * 0.01\n\nlongStop = 0.0\nshortStop = 0.0\n\nif SLbased == "ATR"\n    longStop := valuewhen(buy, low, 0) - (valuewhen(buy, rma(tr(true), lengthATR), 0) * multiATR)\n    longStopPrev = nz(longStop[1], longStop)\n    longStop := close[1] > longStopPrev ? max(longStop, longStopPrev) : longStop\n\n    shortStop := (valuewhen(sell, rma(tr(true), lengthATR), 0) * multiATR) + valuewhen(sell, high, 0)\n    shortStopPrev = nz(shortStop[1], shortStop)\n    shortStop := close[1] > shortStopPrev ? max(shortStop, shortStopPrev) : shortStop\nif SLbased == "Percent"\n    longStop  := strategy.position_avg_price * (1 - SLPercent)\n    shortStop := strategy.position_avg_price * (1 + SLPercent)\n\nstrategy.entry("Long", true, when=buy)\nstrategy.close("Long", when=sell, comment="Exit")\n\nif useSL\n    strategy.exit("Stop Loss", "Long", stop=longStop)\n'

class SMB4E5EE5B196A853A(PinePortBase, IStrategy):
    source_id = "SM_b4e5ee5b196a853a"
    source_file = '移动平均线和偏差指标多周期交易策略A-Multi-Period-Trading-Strategy-Based-on-Moving-Averages.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fast_length': 12, 'slow_length': 26, 'signal_length': 9, 'sma_source': 'EMA', 'sma_signal': 'EMA', 'length': 20, 'mult': 2.0, 'lenRSI': 14, 'useSL': False, 'SLbased': 'Percent', 'multiATR': 10.0, 'lengthATR': 14, 'SLPercent': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 1000
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
