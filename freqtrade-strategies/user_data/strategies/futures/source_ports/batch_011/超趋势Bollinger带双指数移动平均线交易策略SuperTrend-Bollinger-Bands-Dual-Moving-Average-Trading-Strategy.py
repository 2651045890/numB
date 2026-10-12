"""batch_011 port of 超趋势Bollinger带双指数移动平均线交易策略SuperTrend-Bollinger-Bands-Dual-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-23 00:00:00\nend: 2024-02-22 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © zhuenrong\n\n//@version=4\nstrategy("Supertrend + DEMA + Bollinger Bands", overlay=true)\n\n// Input parameters for Supertrend\natrLength = input(title="ATR Period", type=input.integer, defval=12)\nsrc = input(hl2, title="Source")\nmultiplier = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)\nchangeATR = input(title="Change ATR Calculation Method?", type=input.bool, defval=true)\nshowSupertrend = input(title="Show Supertrend Indicator?", type=input.bool, defval=true)\n\n// Input parameters for DEMA\ndemaLength = input(200, title="DEMA Period")\nshowDEMA = input(title="Show DEMA Indicator?", type=input.bool, defval=true)\n\n// Calculate ATR for Supertrend\natr2 = sma(tr, atrLength)\natr = changeATR ? atr(atrLength) : atr2\n\n// Calculate Supertrend\nup = src - (multiplier * atr)\nup1 = nz(up[1], up)\nup := close[1] > up1 ? max(up, up1) : up\n\ndn = src + (multiplier * atr)\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? min(dn, dn1) : dn\n\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\n\n// Plot Supertrend\nupPlot = plot(showSupertrend ? (trend == 1 ? up : na) : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))\nbuySignal = trend == 1 and trend[1] == -1\nplotshape(buySignal ? up : na, title="UpTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.green, 0))\nplotshape(buySignal ? up : na, title="Buy", text="Buy", location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))\n\ndnPlot = plot(showSupertrend ? (trend == 1 ? na : dn) : na, title="Down Trend", style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))\nsellSignal = trend == -1 and trend[1] == 1\nplotshape(sellSignal ? dn : na, title="DownTrend Begins", location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.red, 0))\nplotshape(sellSignal ? dn : na, title="Sell", text="Sell", location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))\n\nmPlot = plot(ohlc4, title="", style=plot.style_circles, linewidth=0)\n\nlongFillColor = (trend == 1 ? color.new(color.green, 80) : color.new(color.white, 0))\nshortFillColor = (trend == -1 ? color.new(color.red, 80) : color.new(color.white, 0))\n\nfill(mPlot, upPlot, title="UpTrend Highlighter", color=longFillColor)\nfill(mPlot, dnPlot, title="DownTrend Highlighter", color=shortFillColor)\n\n// Alert conditions\nalertcondition(buySignal, title="Custom Supertrend Buy", message="Custom Supertrend Buy!")\nalertcondition(sellSignal, title="Custom Supertrend Sell", message="Custom Supertrend Sell!")\n\n// Calculate DEMA\nema1 = ema(close, demaLength)\ndema = 2 * ema1 - ema(ema1, demaLength)\n\n// Plot DEMA with white color\nplot(showDEMA ? dema : na, color=color.new(color.white, 0), title="DEMA", linewidth=2)\n// Add push notification on mobile if buy and sell occurred\nif (buySignal)\n    strategy.entry("Buy", strategy.long)\n    //strategy.exit("Sell")\n    //alert("Buy Signal - Supertrend")\n\nif (sellSignal)\n    strategy.entry("Sell", strategy.short)\n    //strategy.exit("Cover")\n    //alert("Sell Signal - Supertrend")\n\n\n// === Stop LOSS ===\n\nif strategy.position_size>0\n    strategy.exit("Stop Loss/Profit Long","Buy", stop=strategy.position_avg_price*100, limit=strategy.position_avg_price*1.1)\nif strategy.position_size<0\n    strategy.exit("Stop Loss/Profit Short","Sell", stop=strategy.position_avg_price*100, limit=strategy.position_avg_price*1.1)'

class SMACD979B5979D8F0D(PinePortBase, IStrategy):
    source_id = "SM_acd979b5979d8f0d"
    source_file = '超趋势Bollinger带双指数移动平均线交易策略SuperTrend-Bollinger-Bands-Dual-Moving-Average-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrLength': 12, 'multiplier': 3.0, 'changeATR': True, 'showSupertrend': True, 'demaLength': 200, 'showDEMA': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
