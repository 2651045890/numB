"""batch_011 port of 趋势追踪型云图动量背离策略-Trend-Following-Cloud-Momentum-Divergence-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-10 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Ichimoku + RSI + MACD Strategy", overlay=true)\n\n// Ichimoku Cloud parameters\ntenkanPeriod = 9\nkijunPeriod = 26\nsenkouSpanBPeriod = 52\ndisplacement = 26\n\n// RSI parameters\nrsiLength = 14\nrsiOverbought = 70\nrsiOversold = 30\n\n// MACD parameters\n[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)\n\n// Ichimoku calculations\ntenkanSen = (ta.highest(high, tenkanPeriod) + ta.lowest(low, tenkanPeriod)) / 2\nkijunSen = (ta.highest(high, kijunPeriod) + ta.lowest(low, kijunPeriod)) / 2\nsenkouSpanA = (tenkanSen + kijunSen) / 2\nsenkouSpanB = (ta.highest(high, senkouSpanBPeriod) + ta.lowest(low, senkouSpanBPeriod)) / 2\nchikouSpan = close[displacement]\n\n// Plotting Ichimoku Cloud\nplot(tenkanSen, color=color.red, title="Tenkan-sen")\nplot(kijunSen, color=color.blue, title="Kijun-sen")\nplot(senkouSpanA[displacement], color=color.green, title="Senkou Span A")\nplot(senkouSpanB[displacement], color=color.red, title="Senkou Span B")\nfill(plot(senkouSpanA[displacement]), plot(senkouSpanB[displacement]), color=color.new(color.green, 90), title="Cloud")\n\n// RSI calculation\nrsi = ta.rsi(close, rsiLength)\n\n// Long entry condition\nlongCondition = (close > senkouSpanA) and (close > senkouSpanB) and (rsi > rsiOversold) and (ta.crossover(macdLine, signalLine))\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short entry condition\nshortCondition = (close < senkouSpanA) and (close < senkouSpanB) and (rsi < rsiOverbought) and (ta.crossunder(macdLine, signalLine))\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Exit conditions\nif (ta.crossunder(macdLine, signalLine) and strategy.position_size > 0)\n    strategy.close("Long")\n\nif (ta.crossover(macdLine, signalLine) and strategy.position_size < 0)\n    strategy.close("Short")\n\n// Plot RSI\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.green)\nplot(rsi, color=color.blue, title="RSI")'

class SM50631C3593919568(PinePortBase, IStrategy):
    source_id = "SM_50631c3593919568"
    source_file = '趋势追踪型云图动量背离策略-Trend-Following-Cloud-Momentum-Divergence-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
