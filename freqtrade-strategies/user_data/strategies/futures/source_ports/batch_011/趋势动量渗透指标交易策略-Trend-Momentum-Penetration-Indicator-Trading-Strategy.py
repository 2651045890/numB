"""batch_011 port of 趋势动量渗透指标交易策略-Trend-Momentum-Penetration-Indicator-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-25 00:00:00\nend: 2025-04-23 08:00:00\nperiod: 3d\nbasePeriod: 3d\nexchanges: [{"eid":"Futures_Binance","currency":"DOGE_USDT"}]\n*/\n\n// This Pine Script® code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © avi\n\n//@version=5\nstrategy("AVI - S13", overlay=true, initial_capital=10000, default_qty_type=strategy.fixed)\n\n// Get daily-level values\ndailyATR      = request.security(syminfo.tickerid, "D", ta.atr(10))\ndailyEMA10    = request.security(syminfo.tickerid, "D", ta.ema(close, 10))\ndailyEMA50    = request.security(syminfo.tickerid, "D", ta.ema(close, 50))\ndailyEMA100   = request.security(syminfo.tickerid, "D", ta.ema(close, 100))\ndailyClose    = request.security(syminfo.tickerid, "D", close)\ndailyOpen     = request.security(syminfo.tickerid, "D", open)\ndailyVol      = request.security(syminfo.tickerid, "D", volume)\ndailyVolEMA12 = request.security(syminfo.tickerid, "D", ta.ema(volume, 12))\n\nema_plus_atr   = dailyEMA10 + dailyATR\nema_minus_atr  = dailyEMA10 - dailyATR\nema_plus_atr1  = dailyEMA10 + dailyATR * 3\n\n// Entry conditions\nconditionema    = dailyEMA50 > dailyEMA100\nconditionatr    = dailyClose > ema_plus_atr\nconditioncandel = dailyClose > dailyOpen\nconditionvol    = dailyVol > dailyVolEMA12\nentryCondition  = conditionema and conditionatr and conditioncandel and conditionvol\n\nbgcolor(entryCondition ? color.new(#26e600, 90) : na)\nplotshape(entryCondition, location=location.belowbar, style=shape.labelup, color=color.green, size=size.tiny, title="Entry")\n\n// Trade management variables\nvar bool inTrade = false\nvar float entryPrice = na\nvar float stopLossPrice = na\nvar float takeProfitPrice = na\nvar int entryBar = na\n\n// Entry logic\nif entryCondition and not inTrade and timeframe.isdaily\n    stopLossPrice := ema_minus_atr\n    takeProfitPrice := ema_plus_atr1\n    riskPerShare = math.abs(dailyClose - stopLossPrice)\n    riskAmount = strategy.equity * 0.02\n    sharesCount = riskPerShare > 0 ? math.floor(riskAmount / riskPerShare) : 0\n\n    if sharesCount > 0\n        strategy.entry("Long", strategy.long, qty=sharesCount)\n        entryPrice := dailyClose\n        inTrade := true\n        entryBar := bar_index\n\n// Exit logic\nif inTrade\n    if low <= stopLossPrice\n        strategy.close("Long", comment="SL")\n        inTrade := false\n    else if high >= takeProfitPrice\n        strategy.close("Long", comment="TP")\n        inTrade := false\n\n// Draw horizontal lines for SL and TP during the trade\nplot(inTrade ? stopLossPrice : na, title="Stop Loss", color=color.red, linewidth=1, style=plot.style_linebr)\nplot(inTrade ? takeProfitPrice : na, title="Take Profit", color=color.green, linewidth=1, style=plot.style_linebr)\n'

class SM95D48B30A3FDF125(PinePortBase, IStrategy):
    source_id = "SM_95d48b30a3fdf125"
    source_file = '趋势动量渗透指标交易策略-Trend-Momentum-Penetration-Indicator-Trading-Strategy.md'
    timeframe = '3d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'broker_state', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
