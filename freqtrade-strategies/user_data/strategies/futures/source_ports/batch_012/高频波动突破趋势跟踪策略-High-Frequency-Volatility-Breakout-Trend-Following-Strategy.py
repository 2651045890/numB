"""batch_012 port of 高频波动突破趋势跟踪策略-High-Frequency-Volatility-Breakout-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-08 00:00:00\nend: 2025-02-07 00:00:00\nperiod: 4h\nbasePeriod: 4h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bollinger Bands + Moving Average Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=200)\n\n// === Vstupy ===\n// Moving Average\nmaPeriod = input.int(20, title="MA Period", minval=1)\nmaType = input.string("SMA", title="MA Type", options=["SMA", "EMA"])\n\n// Bollinger Bands\nbbPeriod = input.int(20, title="BB Period", minval=1)\nbbMultiplier = input.float(2.0, title="BB Multiplier", step=0.1)\n\n// === Výpočty Indikátorov ===\n// Moving Average\nma = maType == "SMA" ? ta.sma(close, maPeriod) : ta.ema(close, maPeriod)\n\n// Bollinger Bands\nbasis = ta.sma(close, bbPeriod)\ndev = bbMultiplier * ta.stdev(close, bbPeriod)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// === Podmienky Pre Vstupy ===\n// Nákupný signál: Cena prekonáva dolný Bollinger Band smerom nahor a cena je nad MA\nlongCondition = ta.crossover(close, lowerBB) and close > ma\n\n// Predajný signál: Cena prekonáva horný Bollinger Band smerom nadol a cena je pod MA\nshortCondition = ta.crossunder(close, upperBB) and close < ma\n\n// === Vstupné Signály ===\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// === Výstupné Podmienky ===\n// Uzavretie Long pozície pri prekonaní MA smerom nadol alebo ceny pod MA\nexitLongCondition = ta.crossunder(close, ma) or close < ma\nif (exitLongCondition)\n    strategy.close("Long")\n\n// Uzavretie Short pozície pri prekonaní MA smerom nahor alebo ceny nad MA\nexitShortCondition = ta.crossover(close, ma) or close > ma\nif (exitShortCondition)\n    strategy.close("Short")\n\n// === Vykreslenie Indikátorov na Grafe ===\n// Vykreslenie Moving Average\nplot(ma, color=color.blue, title="Moving Average")\n\n// Vykreslenie Bollinger Bands\nupperPlot = plot(upperBB, color=color.red, title="Upper BB")\nlowerPlot = plot(lowerBB, color=color.green, title="Lower BB")\nfill(upperPlot, lowerPlot, color=color.rgb(173, 216, 230, 90), title="BB Fill")\n\n// Vizualizácia Signálov\nplotshape(series=longCondition, title="Long Entry", location=location.belowbar, color=color.green, style=shape.labelup, text="Long")\nplotshape(series=shortCondition, title="Short Entry", location=location.abovebar, color=color.red, style=shape.labeldown, text="Short")\nplotshape(series=exitLongCondition, title="Long Exit", location=location.abovebar, color=color.red, style=shape.labeldown, text="Exit Long")\nplotshape(series=exitShortCondition, title="Short Exit", location=location.belowbar, color=color.green, style=shape.labelup, text="Exit Short")\n\n'

class SMHighFrequencyVolatilityBreakoutTrendFollowingStrategyda79f4(PinePortBase, IStrategy):
    source_id = "SM_da79f44c56923ca8"
    source_file = '高频波动突破趋势跟踪策略-High-Frequency-Volatility-Breakout-Trend-Following-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'maPeriod': 20, 'maType': 'SMA', 'bbPeriod': 20, 'bbMultiplier': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 200
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
