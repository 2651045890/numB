"""batch_011 port of 趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2024-12-19 00:00:00\nperiod: 4d\nbasePeriod: 4d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover Strategy with 15 SMA Trend", overlay=true, margin_long=100, margin_short=100)\n\n// Calculate Indicators\nsma15 = ta.sma(close, 15)\nema9 = ta.ema(close, 9)\nema21 = ta.ema(close, 21)\n\n// Trend Detection\nuptrend = close > sma15\ndowntrend = close < sma15\n\n// Crossover Conditions\ngoldenCross = ta.crossover(ema9, ema21)\ndeathCross = ta.crossunder(ema9, ema21)\n\n// Candle Conditions\ntwoBullish = (close > open) and (close[1] > open[1])\nbearishCandle = (close < open)\n\n// Entry Conditions\nlongCondition = goldenCross and uptrend and twoBullish and (ema9 > sma15) and (ema21 > sma15)\nshortCondition = deathCross and downtrend and bearishCandle and (ema9 < sma15) and (ema21 < sma15)\n\n// Risk Management\nvar float longStop = na\nvar float longTarget = na\nvar float shortStop = na\nvar float shortTarget = na\n\nif longCondition\n    longStop := low\n    longTarget := close + 4*(close - longStop)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long Exit", "Long", stop=longStop, limit=longTarget)\n\nif shortCondition\n    shortStop := high\n    shortTarget := close - 4*(shortStop - close)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short Exit", "Short", stop=shortStop, limit=shortTarget)\n\n// Visual Elements\nplot(sma15, "15 SMA", color=color.orange)\nplot(ema9, "9 EMA", color=color.blue)\nplot(ema21, "21 EMA", color=color.red)\n\n// Plot trading levels\nplot(longCondition ? longStop : na, "Long Stop", color=color.red, style=plot.style_linebr)\nplot(longCondition ? longTarget : na, "Long Target", color=color.green, style=plot.style_linebr)\nplot(shortCondition ? shortStop : na, "Short Stop", color=color.red, style=plot.style_linebr)\nplot(shortCondition ? shortTarget : na, "Short Target", color=color.green, style=plot.style_linebr)\n\n// Signal Markers\nplotshape(longCondition, "Buy", shape.triangleup, location.belowbar, color=color.green, size=size.small)\nplotshape(shortCondition, "Sell", shape.triangledown, location.abovebar, color=color.red, size=size.small)'

class SM2889A1689097D5BB(PinePortBase, IStrategy):
    source_id = "SM_2889a1689097d5bb"
    source_file = '趋势跟踪型双均线交叉策略结合SMA趋势过滤系统-Trend-Following-Dual-EMA-Crossover-Strategy-with-SMA-Trend-Filtering-System.md'
    timeframe = '4d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
