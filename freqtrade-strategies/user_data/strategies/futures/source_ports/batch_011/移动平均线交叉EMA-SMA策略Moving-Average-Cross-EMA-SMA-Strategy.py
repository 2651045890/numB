"""batch_011 port of 移动平均线交叉EMA-SMA策略Moving-Average-Cross-EMA-SMA-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-26 00:00:00\nend: 2023-09-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="Moving Average Cross EMA SMA", overlay=true, initial_capital=10000, currency=\'USD\',default_qty_type=strategy.percent_of_equity,default_qty_value=100)\n// Based on strategy by lsills @ https://www.tradingview.com/script/oI8loEZ8-Moving-Average-Cross-Strategy/\n// Strategy has several logic alternatives - comment out the undesired logic sections below, only 1 logic section can be active\n\n\n// === GENERAL INPUTS ===\n// short Ema\nmaFastSource   = input(defval = close, title = "Fast EMA Source")\nmaFastLength   = input(defval = 13, title = "Fast EMA Period", minval = 1)\n// long Sma\nmaSlowSource   = input(defval = close, title = "Slow SMA Source")\nmaSlowLength   = input(defval = 30, title = "Slow SMA Period", minval = 1)\n// longer Sma\nmaSlowerSource   = input(defval = close, title = "Slower SMA Source")\nmaSlowerLength   = input(defval = 30, title = "Slower SMA Period", minval = 1)\n\n\n\n// === SERIES SETUP ===\n/// a couple of ma\'s..\nmaFast = ema(maFastSource, maFastLength)\nmaSlow = sma(maSlowSource, maSlowLength)\nmaSlower = vwma(maSlowerSource, maSlowerLength)\nrsi = rsi(maSlowerSource, maSlowerLength)\n\n// === PLOTTING ===\nfast = plot(maFast, title = "Fast MA", color = red, linewidth = 2, style = line, transp = 30)\nslow = plot(maSlow, title = "Slow MA", color = green, linewidth = 2, style = line, transp = 30)\nslower = plot(maSlower, title = "Slower MA", color = teal, linewidth = 2, style = line, transp = 30)\n\n\n// === LOGIC === Basic - simply switches from long to short and vice-versa with each fast-slow MA cross\nenterLong = maFast> maSlow\nexitLong = maSlow> maFast\n\n\n// === LOGIC === Complex 1 - switches from long to short and vice-versa with each fast-slow MA cross but additional conditions must be met\n//enterLong = variance(maFast,maSlowLength) < 0.6 and close[0] > maFast and crossover(maFast, maSlow) and 1.1* maSlow > maSlower and rsi>rsi[2]\n//exitLong = variance(maFast,maSlowLength) < 0.6 and close[0] < maSlow and crossover(maSlow, maFast) and maSlow/1.1 < maSlower and rsi<rsi[2]\n\n// === LOGIC === Complex 2- switches from long to short and vice-versa with each fast-slow MA cross but additional conditions must be met\n//enterLong = maFast> maSlow and 1.1* maSlow > maSlower and rsi>rsi[1] and close > close[3] //and close > close[2]\n//exitLong = maSlow> maFast and maSlow/1.1 < maSlower and rsi<rsi[1] and close < close[3] // and close < close[2]\n\n\n// Entry //\nstrategy.entry(id="Long Entry", long=true, when=enterLong)\nstrategy.entry(id="Short Entry", long=false, when=exitLong)\n\n// === FILL ====\n\nfill(fast, slow, color = maFast > maSlow ? green : red)'

class SM123AB40660CAF861(PinePortBase, IStrategy):
    source_id = "SM_123ab40660caf861"
    source_file = '移动平均线交叉EMA-SMA策略Moving-Average-Cross-EMA-SMA-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'maFastLength': 13, 'maSlowLength': 30, 'maSlowerLength': 30}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
