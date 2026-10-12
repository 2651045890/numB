"""batch_011 port of 趋势价格简单移动平均量化策略Simple-Moving-Average-Trend-Price-Quantitative-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-21 00:00:00\nend: 2024-02-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Trend, Momentum ve Volatilite Stratejisi", overlay=true)\n\n// Kullanıcı tarafından ayarlanabilir girdilerin panelde görüntülenmesi\ntrendPeriod = input(50, "Trend Periyodu")\nmomentumPeriod = input(14, "Momentum Periyodu")\nbbPeriod = input(20, "Bollinger Bantları Periyodu")\nbbDeviation = input(2, "Bollinger Bantları Sapması")\n\n// Fiyat hareketlerine dayalı trend göstergesi (Örneğin: Basit Hareketli Ortalama)\ntrendIndicator = sma(close, trendPeriod)\n\n// Hacim tabanlı momentum göstergesi (Örneğin: Hacim Ağırlıklı Ortalama Fiyat)\nmomentumIndicator = vwma(close, momentumPeriod)\n\n// Volatilite göstergesi (Bollinger Bantları)\n[upperBB, middleBB, lowerBB] = bb(close, bbPeriod, bbDeviation)\n\n// Alım ve satım sinyallerinin belirlenmesi\nbuySignal = crossover(close, trendIndicator) and close > upperBB\nsellSignal = crossunder(close, trendIndicator) and close < lowerBB\n\n// Alım ve satım işlemlerinin gerçekleştirilmesi\nif (buySignal)\n    strategy.entry("Buy", strategy.long)\nif (sellSignal)\n    strategy.close("Buy")\n\nif (sellSignal)\n    strategy.entry("Sell", strategy.short)\nif (buySignal)\n    strategy.close("Sell")'

class SM14DAE2022B966528(PinePortBase, IStrategy):
    source_id = "SM_14dae2022b966528"
    source_file = '趋势价格简单移动平均量化策略Simple-Moving-Average-Trend-Price-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'trendPeriod': 50, 'momentumPeriod': 14, 'bbPeriod': 20, 'bbDeviation': 2}
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
