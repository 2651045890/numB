"""batch_011 port of 趋势追踪型短线交易策略Trend-Tracking-Short-term-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-27 00:00:00\nend: 2023-12-29 23:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © mariocastel\n\n//@version=5\nstrategy("Wave Rider", overlay=true, initial_capital = 100000)\n\nsession = input(defval = "1400-1500", title = "Session Time")\nt = not na(time(timeframe.period,session))\nRR = input.float(1.5, "Risk to reward", step=0.5)\nvar bool movetoBE = input(false, "Move to Break Even")\nBE = input.float(1, "Break Even at", step=0.5)\n\nvwap_mult = 0.001 * input(3, "VWAP Multiplier")\naboveVWAP = ta.vwap(close) * (1 + vwap_mult)\nbelowVWAP = ta.vwap(close) * (1 - vwap_mult)\nsym = input("BTC_USDT:swap", "VWAP Source")\n\nQQQaboveVWAP = request.security(sym, "3", aboveVWAP)\nQQQbelowVWAP = request.security(sym, "3", belowVWAP)\nQQQclose = request.security(sym, "3", close)\n\nema20 = ta.ema(close, 20)\nema50 = ta.ema(close, 50)\nema60 = ta.ema(close, 60)\nema9 = ta.ema(close, 9)\n\nopentrades = strategy.opentrades > 0\n\naboveEMA = close > ema60\nbelowEMA = close < ema60\n\nuptrend = aboveEMA and aboveEMA[1] and aboveEMA[2] and aboveEMA[3] and aboveEMA[4] and aboveEMA[5] and aboveEMA[6] and aboveEMA[7] and aboveEMA[8] and aboveEMA[9] and aboveEMA[10] and aboveEMA[11] and aboveEMA[12] and aboveEMA[13] and aboveEMA[14] and aboveEMA[15] and aboveEMA[16] and aboveEMA[17] and aboveEMA[18] and aboveEMA[19] and aboveEMA[20] and aboveEMA[21] and aboveEMA[22] and aboveEMA[23] and aboveEMA[24] and aboveEMA[25] and aboveEMA[26] and aboveEMA[27] and aboveEMA[28] and aboveEMA[29]\ndowntrend = belowEMA and belowEMA[1] and belowEMA[2] and belowEMA[3] and belowEMA[4] and belowEMA[5] and belowEMA[6] and belowEMA[7] and belowEMA[8] and belowEMA[9] and belowEMA[10] and belowEMA[11] and belowEMA[12] and belowEMA[13] and belowEMA[14] and belowEMA[15] and belowEMA[16] and belowEMA[17] and belowEMA[18] and belowEMA[19] and belowEMA[20] and belowEMA[21] and belowEMA[22] and belowEMA[23] and belowEMA[24] and belowEMA[25] and belowEMA[26] and belowEMA[27] and belowEMA[28] and belowEMA[29]\n\nbuy = (low < ema20 and low > ema50 and close > ema9) and QQQclose > QQQaboveVWAP  or (low[1] < ema20 and low[1] > ema50 and close > ema9) and QQQclose > QQQaboveVWAP and uptrend\nsell = (high > ema20 and high < ema50 and close < ema9) and QQQclose < QQQbelowVWAP  or (high[1] > ema20 and high[1] < ema50 and close < ema9) and QQQclose < QQQbelowVWAP and downtrend\n\nvar float entry = na\nvar float sl = na\nvar float qty = na\nvar float tp = na\nvar float be = na\n\nif ema20 > ema50 and ema9 > ema20 \n    if buy and not opentrades and t and uptrend\n        alert("Wave Rider Setup")\n        entry := close\n        sl := ema50\n        qty := 1000/(close - sl) * 1\n        if close - sl > syminfo.mintick*300\n            tp := close + ((close - sl)*1)\n        else \n            tp := close + ((close - sl)*RR)\n        be := close + ((close - sl)*BE)\n        strategy.entry("Buy", strategy.long, qty=qty)\n        strategy.exit("Close Buy", "Buy",qty=qty, stop=sl, limit=tp)\n\nif ema20 < ema50 and ema9 < ema20 \n    if sell and not opentrades and t and downtrend\n        alert("Wave Rider Setup")\n        entry := close\n        sl := ema50\n        qty := 1000/(sl - close) * 1\n        if sl - close > syminfo.mintick*300\n            tp := close - ((sl - close)*1)\n        else\n            tp := close - ((sl - close)*RR)\n        be := close - ((sl - close)*BE)\n        strategy.entry("Sell", strategy.short, qty=qty)\n        strategy.exit("Close Sell", "Sell", qty=qty, stop=sl, limit=tp)\n\n// Adjust BEs\nif movetoBE == true\n    if strategy.position_size > 0\n        if high >= be\n            sl := entry\n            strategy.cancel("Close Buy")\n            strategy.exit("Close Buy", "Buy", qty=qty, stop=sl, limit=tp)   \n    if strategy.position_size < 0\n        if low <= be\n            sl := entry\n            strategy.cancel("Close Sell")  \n            strategy.exit("Close Sell", "Sell", qty=qty, stop=sl, limit=tp)  \n\n\nEoD_time = timestamp(year, month, dayofmonth, 15, 58, 00)\nEoD = time == EoD_time\nif EoD\n    strategy.close_all()\n\nbarcolor(color=buy ? color.rgb(191, 255, 131): na)\nbarcolor(color=sell ? color.rgb(255, 149, 149): na)\nema20plot = plot(ema20, color=color.rgb(168, 131, 131, 55))\nema50plot = plot(ema50, color=color.black)\nfill(ema20plot, ema50plot, color=color.rgb(168, 131, 131, 85))\nplot(ema9, color=color.red)\nplot(ema60, color=color.purple)\nplot(QQQaboveVWAP)\nplot(QQQbelowVWAP)\nplotshape(uptrend, style=shape.triangleup, location=location.belowbar, color=color.black)\nplotshape(downtrend, style=shape.triangledown, location=location.abovebar, color=color.black)\n'

class SM6462243F4371A13B(PinePortBase, IStrategy):
    source_id = "SM_6462243f4371a13b"
    source_file = '趋势追踪型短线交易策略Trend-Tracking-Short-term-Trading-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'session': '1400-1500', 'RR': 1.5, 'movetoBE': False, 'BE': 1, 'sym': 'BTC_USDT:swap'}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'broker_state', 'exit_order', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
