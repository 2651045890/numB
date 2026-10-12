"""batch_011 port of 超级趋势ATR策略Supertrend-ATR-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © tradez99\n\n//@version=5\nstrategy(\'Supertrend\', overlay=true, format=format.price, precision=2)\n\nPeriods = input(title=\'ATR Period\', defval=10)\nsrc = input(hl2, title=\'Source\')\nMultiplier = input.float(title=\'ATR Multiplier\', step=0.1, defval=3.0)\nchangeATR = input(title=\'Change ATR Calculation Method ?\', defval=true)\nshowsignals = input(title=\'Show Buy/Sell Signals ?\', defval=true)\nhighlighting = input(title=\'Highlighter On/Off ?\', defval=true)\natr2 = ta.sma(ta.tr, Periods)\natr = changeATR ? ta.atr(Periods) : atr2\nup = src - Multiplier * atr\nup1 = nz(up[1], up)\nup := close[1] > up1 ? math.max(up, up1) : up\ndn = src + Multiplier * atr\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? math.min(dn, dn1) : dn\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\nupPlot = plot(trend == 1 ? up : na, title=\'Up Trend\', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))\nbuySignal = trend == 1 and trend[1] == -1\nplotshape(buySignal ? up : na, title=\'UpTrend Begins\', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.green, 0))\nplotshape(buySignal and showsignals ? up : na, title=\'Buy\', text=\'Buy\', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))\ndnPlot = plot(trend == 1 ? na : dn, title=\'Down Trend\', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))\nsellSignal = trend == -1 and trend[1] == 1\nplotshape(sellSignal ? dn : na, title=\'DownTrend Begins\', location=location.absolute, style=shape.circle, size=size.tiny, color=color.new(color.red, 0))\nplotshape(sellSignal and showsignals ? dn : na, title=\'Sell\', text=\'Sell\', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))\nmPlot = plot(ohlc4, title=\'\', style=plot.style_circles, linewidth=0)\nlongFillColor = highlighting ? trend == 1 ? color.green : color.white : color.white\nshortFillColor = highlighting ? trend == -1 ? color.red : color.white : color.white\n//fill(mPlot, upPlot, title=\'UpTrend Highligter\', color=longFillColor)\n//fill(mPlot, dnPlot, title=\'DownTrend Highligter\', color=shortFillColor)\n\nmultiplier = input.float(title="ATR multiplier", defval = 1.5)\nrr           = input.float(title="Risk:Reward", defval=1.0)\nriskPerTrade = input.float(title="Risk Per Trade %", defval=1.0)\natr3 = ta.atr(14)\n\n//calculate stops and targets \nlongstop = close - (atr3 * multiplier)\nshortstop = close + (atr3 * multiplier)\nlongStopDistance  = close - longstop\nshortStopDistance = shortstop - close\nlongTarget  = close + (longStopDistance * rr)\nshortTarget = close - (shortStopDistance * rr)\n\n// Save stops & targets\nvar t_stop = 0.0\nvar t_target = 0.0\n\nlongCondition = buySignal \nif (longCondition)\n    t_stop := longstop\n    t_target := longTarget\n    positionSize = math.floor((strategy.equity * (riskPerTrade/100)) / (close - t_stop))\n    strategy.entry("Long", strategy.long, qty = positionSize)\n\nshortCondition = sellSignal \nif (shortCondition)\n    t_stop := shortstop\n    t_target := shortTarget\n    positionSize = math.floor((strategy.equity * (riskPerTrade/100)) / (t_stop - close))  \n    strategy.entry("Short", strategy.short, qty = positionSize)\n\nstrategy.exit(id="Long Exit", from_entry="Long", limit=t_target, stop=t_stop)\nstrategy.exit(id="Short Exit", from_entry="Short", limit=t_target, stop=t_stop)\n'

class SMC32163A687998C07(PinePortBase, IStrategy):
    source_id = "SM_c32163a687998c07"
    source_file = '超级趋势ATR策略Supertrend-ATR-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'Periods': 10, 'Multiplier': 3.0, 'changeATR': True, 'showsignals': True, 'highlighting': True, 'multiplier': 1.5, 'rr': 1.0, 'riskPerTrade': 1.0}
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
