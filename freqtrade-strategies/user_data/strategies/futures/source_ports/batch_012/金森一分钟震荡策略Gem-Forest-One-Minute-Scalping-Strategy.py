"""batch_012 port of 金森一分钟震荡策略Gem-Forest-One-Minute-Scalping-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Gem Forest 1 Dakika Scalp", overlay=true)\n\nsource = close\natrlen = input.int(14, "ATR Period")\nmult = input.float(1, "ATR Multi", step=0.1)\nsmoothing = input.string(title="ATR Smoothing", defval="WMA", options=["RMA", "SMA", "EMA", "WMA"])\n\nma_function(source, atrlen) => \n    if smoothing == "RMA"\n        ta.rma(source, atrlen)\n    else\n        if smoothing == "SMA"\n            ta.sma(source, atrlen)\n        else\n            if smoothing == "EMA"\n                ta.ema(source, atrlen)\n            else\n                ta.wma(source, atrlen)\n\natr_slen = ma_function(ta.tr(true), atrlen)\nupper_band = atr_slen * mult + close\nlower_band = close - atr_slen * mult\n\nShortEMAlen = input.int(21, "Fast EMA")\nLongEMAlen = input.int(65, "Slow EMA")\nshortSMA = ta.ema(close, ShortEMAlen)\nlongSMA = ta.ema(close, LongEMAlen)\nRSILen1 = input.int(25, "Fast RSI Length")\nRSILen2 = input.int(100, "Slow RSI Length")\nrsi1 = ta.rsi(close, RSILen1)\nrsi2 = ta.rsi(close, RSILen2)\natr = ta.atr(atrlen)\n\nRSILong = rsi1 > rsi2\nRSIShort = rsi1 < rsi2\n\nlongCondition = open < lower_band\nshortCondition = open > upper_band\nGoldenLong = ta.crossover(shortSMA,longSMA)\nGoldenshort = ta.crossover(longSMA,shortSMA)\n\nplotshape(shortCondition, title="Sell Label", text="Sell", location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.white, transp=0)\nplotshape(longCondition, title="Buy Label", text="Buy", location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.white, transp=0)\nplotshape(Goldenshort, title="Golden Sell Label", text="Golden Crossover Short", location=location.abovebar, style=shape.labeldown, size=size.tiny, color=color.blue, textcolor=color.white, transp=0)\nplotshape(GoldenLong, title="Golden Buy Label", text="Golden Crossover Long", location=location.belowbar, style=shape.labelup, size=size.tiny, color=color.yellow, textcolor=color.white, transp=0)\n\nif (longCondition)\n    stopLoss = low - atr * 2\n    takeProfit = high + atr * 5\n    strategy.entry("long", strategy.long, when = RSILong)\n\nif (shortCondition)\n    stopLoss = high + atr * 2\n    takeProfit = low - atr * 5\n    strategy.entry("short", strategy.short, when = RSIShort)\n\nplot(upper_band)\nplot(lower_band)\nplot(shortSMA, color = color.red)\nplot(longSMA, color = color.yellow)\n\n'

class SMGemForestOneMinuteScalpingStrategy8ae72c(PinePortBase, IStrategy):
    source_id = "SM_8ae72cf861b8d2b0"
    source_file = '金森一分钟震荡策略Gem-Forest-One-Minute-Scalping-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrlen': 14, 'mult': 1, 'smoothing': 'WMA', 'ShortEMAlen': 21, 'LongEMAlen': 65, 'RSILen1': 25, 'RSILen2': 100}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
