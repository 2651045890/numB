"""batch_011 port of 超级趋势策略SuperTrend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-12 00:00:00\nend: 2023-10-12 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// strategy("SuperTrend Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=1000)\n\nLongOnly = input(title="Long Only ?", type=input.bool, defval=true)\nlength = input(title="ATR Period", type=input.integer, defval=22)\nmult = input(title="ATR Multiplier", type=input.float, step=0.1, defval=3.0)\nshowLabels = input(title="Show Buy/Sell Labels ?", type=input.bool, defval=true)\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n\n// From Date Inputs\nfromDay = input(defval=1, title="From Day", minval=1, maxval=31)\nfromMonth = input(defval=1, title="From Month", minval=1, maxval=12)\nfromYear = input(defval=2019, title="From Year", minval=1970)\n\n// To Date Inputs\ntoDay = input(defval=1, title="To Day", minval=1, maxval=31)\ntoMonth = input(defval=1, title="To Month", minval=1, maxval=12)\ntoYear = input(defval=2020, title="To Year", minval=1970)\n\n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n\n////////////////////////////////////////////////////////////////////////////////\n\n\natr = mult * atr(length)\n\nlongStop = hl2 - atr\nlongStopPrev = nz(longStop[1], longStop)\nlongStop := close[1] > longStopPrev ? max(longStop, longStopPrev) : longStop\n\nshortStop = hl2 + atr\nshortStopPrev = nz(shortStop[1], shortStop)\nshortStop := close[1] < shortStopPrev ? min(shortStop, shortStopPrev) : shortStop\n\ndir = 1\ndir := nz(dir[1], dir)\ndir := dir == -1 and close > shortStopPrev ? 1 : \n   dir == 1 and close < longStopPrev ? -1 : dir\n\nlongColor = color.green\nshortColor = color.red\n\n\nplot(dir == 1 ? longStop : na, title="Long Stop", style=plot.style_linebr, linewidth=2, color=longColor)\nbuySignal = dir == 1 and dir[1] == -1\nplotshape(buySignal ? longStop : na, title="Long Stop Start", location=location.absolute, style=shape.circle, size=size.tiny, color=longColor, transp=0)\nplotshape(buySignal and showLabels ? longStop : na, title="Buy Label", text="Buy", location=location.absolute, style=shape.labelup, size=size.tiny, color=longColor, textcolor=color.white, transp=0)\n\nplot(dir == 1 ? na : shortStop, title="Short Stop", style=plot.style_linebr, linewidth=2, color=shortColor)\nsellSignal = dir == -1 and dir[1] == 1\nplotshape(sellSignal ? shortStop : na, title="Short Stop Start", location=location.absolute, style=shape.circle, size=size.tiny, color=shortColor, transp=0)\nplotshape(sellSignal and showLabels ? shortStop : na, title="Sell Label", text="Sell", location=location.absolute, style=shape.labeldown, size=size.tiny, color=shortColor, textcolor=color.white, transp=0)\n\nif LongOnly\n    if buySignal and time_cond\n        strategy.entry("Long", strategy.long, comment="Long")\n    \n    if(sellSignal and time_cond)\n        strategy.close("Long")\nelse\n    if buySignal and time_cond\n        strategy.entry("Long", strategy.long, comment="Long")\n    else\n        strategy.cancel("Long")\n    \n    \n    if sellSignal and time_cond\n        strategy.entry("Short", strategy.short, comment="Short")\n    else\n        strategy.cancel("Short")\n\nif not time_cond\n    strategy.close_all()\n'

class SMBD5FF82E0ADD9894(PinePortBase, IStrategy):
    source_id = "SM_bd5ff82e0add9894"
    source_file = '超级趋势策略SuperTrend-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'LongOnly': True, 'length': 22, 'mult': 3.0, 'showLabels': True, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2019, 'toDay': 1, 'toMonth': 1, 'toYear': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
