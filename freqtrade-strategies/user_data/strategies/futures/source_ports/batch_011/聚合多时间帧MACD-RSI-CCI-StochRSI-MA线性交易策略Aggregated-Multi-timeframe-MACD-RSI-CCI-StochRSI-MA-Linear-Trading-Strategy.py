"""batch_011 port of 聚合多时间帧MACD-RSI-CCI-StochRSI-MA线性交易策略Aggregated-Multi-timeframe-MACD-RSI-CCI-StochRSI-MA-Linear-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-15 00:00:00\nend: 2024-01-17 06:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("MACD RSI CCI StochRSI MA Strategy", shorttitle="MRCSSMA", overlay=true)\n\n// MACD göstergesi\nfastLength = input(12, title="Fast Length")\nslowLength = input(26, title="Slow Length")\nsignalLength = input(9, title="Signal Length")\n[macdLine, signalLine, _] = macd(close, fastLength, slowLength, signalLength)\n\n// RSI göstergesi\nrsiLength = input(14, title="RSI Length")\nrsiLevel = input(70, title="RSI Overbought Level")\nrsiValue = rsi(close, rsiLength)\n\n// CCI göstergesi\ncciLength = input(14, title="CCI Length")\ncciLevel = input(100, title="CCI Overbought Level")\ncciValue = cci(close, cciLength)\n\n// Stochastic Oscillator göstergesi\nstochLength = input(14, title="Stoch Length")\nstochK = input(3, title="Stoch K")\nstochD = input(3, title="Stoch D")\nstochValue = stoch(close, high, low, stochLength)\nstochDValue = sma(stochValue, stochD)\n\n// 200 günlük hareketli ortalama\nma200 = sma(close, 200)\n\n// Alış ve Satış Sinyalleri\nbuySignal = crossover(macdLine, signalLine) and rsiValue < rsiLevel and cciValue < cciLevel and stochValue > stochDValue and close > ma200\nsellSignal = crossunder(macdLine, signalLine) and rsiValue > (100 - rsiLevel) and cciValue > (100 - cciLevel) and stochValue < stochDValue and close < ma200\n\n// Ticaret stratejisi uygula\nstrategy.entry("Buy", strategy.long, when = buySignal)\nstrategy.close("Buy", when = sellSignal)\nstrategy.entry("Sell", strategy.short, when = sellSignal)\nstrategy.close("Sell", when = buySignal)\n\n// Göstergeleri çiz\nhline(rsiLevel, "RSI Overbought", color=color.red)\nhline(100 - rsiLevel, "RSI Oversold", color=color.green)\nhline(cciLevel, "CCI Overbought", color=color.red)\nhline(100 - cciLevel, "CCI Oversold", color=color.green)\n\n// 200 günlük hareketli ortalama çiz\nplot(ma200, color=color.blue, title="200-day MA")\n\n// Grafik üzerinde sinyal okları çiz\nplotshape(series=buySignal, title="Buy Signal", color=color.green, style=shape.triangleup, location=location.belowbar, size=size.small)\nplotshape(series=sellSignal, title="Sell Signal", color=color.red, style=shape.triangledown, location=location.abovebar, size=size.small)\n'

class SM99914A3262010318(PinePortBase, IStrategy):
    source_id = "SM_99914a3262010318"
    source_file = '聚合多时间帧MACD-RSI-CCI-StochRSI-MA线性交易策略Aggregated-Multi-timeframe-MACD-RSI-CCI-StochRSI-MA-Linear-Trading-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9, 'rsiLength': 14, 'rsiLevel': 70, 'cciLength': 14, 'cciLevel': 100, 'stochLength': 14, 'stochK': 3, 'stochD': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
