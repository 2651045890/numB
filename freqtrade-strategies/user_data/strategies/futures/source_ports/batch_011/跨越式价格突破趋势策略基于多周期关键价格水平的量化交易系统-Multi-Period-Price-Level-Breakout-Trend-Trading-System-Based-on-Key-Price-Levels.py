"""batch_011 port of 跨越式价格突破趋势策略基于多周期关键价格水平的量化交易系统-Multi-Period-Price-Level-Breakout-Trend-Trading-System-Based-on-Key-Price-Levels.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-06 00:00:00\nend: 2025-01-04 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © tradingbauhaus\n\n//@version=6\nstrategy("HOD/LOD/PMH/PML/PDH/PDL Strategy by tradingbauhaus ", shorttitle="HOD/LOD Strategy", overlay=true)\n\n// Daily high and low\ndailyhigh = request.security(syminfo.tickerid, \'D\', high)\ndailylow = request.security(syminfo.tickerid, \'D\', low)\n\n// Previous day high and low\nvar float previousdayhigh = na\nvar float previousdaylow = na\nhigh1 = request.security(syminfo.tickerid, \'D\', high[1])\nlow1 = request.security(syminfo.tickerid, \'D\', low[1])\nhigh0 = request.security(syminfo.tickerid, \'D\', high[0])\nlow0 = request.security(syminfo.tickerid, \'D\', low[0])\n\n// Yesterday high and low\nif (hour == 9 and minute > 30) or hour > 10\n    previousdayhigh := high1\n    previousdaylow := low1\nelse\n    previousdayhigh := high0\n    previousdaylow := low0\n\n// Premarket high and low\nt = time("1440", "0000-0930") // 1440 is the number of minutes in a whole day.\nis_first = na(t[1]) and not na(t) or t[1] < t\nending_hour = 9\nending_minute = 30\n\nvar float pm_high = na\nvar float pm_low = na\n\nif is_first and barstate.isnew and ((hour < ending_hour or hour >= 16) or (hour == ending_hour and minute < ending_minute))\n    pm_high := high\n    pm_low := low\nelse \n    pm_high := pm_high[1]\n    pm_low := pm_low[1]\n\nif high > pm_high and ((hour < ending_hour or hour >= 16) or (hour == ending_hour and minute < ending_minute))\n    pm_high := high\n    \nif low < pm_low and ((hour < ending_hour or hour >= 16) or (hour == ending_hour and minute < ending_minute))\n    pm_low := low\n\n// Plotting levels\nplot(dailyhigh, style=plot.style_line, title="Daily high", color=color.white, linewidth=1, trackprice=true)\nplot(dailylow, style=plot.style_line, title="Daily low", color=color.purple, linewidth=1, trackprice=true)\nplot(previousdayhigh, style=plot.style_line, title="Previous Day high", color=color.orange, linewidth=1, trackprice=true)\nplot(previousdaylow, style=plot.style_line, title="Previous Day low", color=color.blue, linewidth=1, trackprice=true)\nplot(pm_high, style=plot.style_line, title="Premarket high", color=color.green, linewidth=1, trackprice=true)\nplot(pm_low, style=plot.style_line, title="Premarket low", color=color.red, linewidth=1, trackprice=true)\n\n// Strategy logic\n// Long entry: Price crosses above PMH or PDH\nif (ta.crossover(close, pm_high) or ta.crossover(close, previousdayhigh)) and strategy.opentrades == 0\n    strategy.entry("Long", strategy.long)\n\n// Short entry: Price crosses below PML or PDL\nif (ta.crossunder(close, pm_low) or ta.crossunder(close, previousdaylow)) and strategy.opentrades == 0\n    strategy.entry("Short", strategy.short)\n\n// Exit long: Price reaches HOD\nif strategy.position_size > 0 and ta.crossover(close, dailyhigh)\n    strategy.close("Long")\n\n// Exit short: Price reaches LOD\nif strategy.position_size < 0 and ta.crossunder(close, dailylow)\n    strategy.close("Short")'

class SM95F283BCA5D1CCF9(PinePortBase, IStrategy):
    source_id = "SM_95f283bca5d1ccf9"
    source_file = '跨越式价格突破趋势策略基于多周期关键价格水平的量化交易系统-Multi-Period-Price-Level-Breakout-Trend-Trading-System-Based-on-Key-Price-Levels.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
