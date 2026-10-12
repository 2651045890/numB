"""batch_012 port of 高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-02 00:00:00\nend: 2025-04-01 00:00:00\nperiod: 3d\nbasePeriod: 3d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SuperTrend STRATEGY w/ TP & SL", overlay=true)\n\n// === Girdiler ===\natrPeriod = input.int(10, title="ATR Period")\nmult = input.float(3.0, title="ATR Multiplier")\nsrc = input.source(hl2, title="Kaynak")\ntpPerc = input.float(2.5, title="Take Profit (%)")\nslPerc = input.float(1.0, title="Stop Loss (%)")\nentryOffsetPerc = input.float(0.2, title="Giriş Noktası Yüzdesel Geriden (%)")\n\n// === ATR ve SuperTrend Hesabı ===\natr = ta.atr(atrPeriod)\nupperBand = src - mult * atr\nlowerBand = src + mult * atr\n\nprevUpper = nz(upperBand[1], upperBand)\nprevLower = nz(lowerBand[1], lowerBand)\n\nupperBand := close[1] > prevUpper ? math.max(upperBand, prevUpper) : upperBand\nlowerBand := close[1] < prevLower ? math.min(lowerBand, prevLower) : lowerBand\n\nvar trend = 1\ntrend := close > prevLower ? 1 : close < prevUpper ? -1 : nz(trend[1], 1)\n\nbuySignal = trend == 1 and trend[1] == -1\nsellSignal = trend == -1 and trend[1] == 1\n\n// === Giriş Noktası Takibi ===\nvar float lastBuyPrice = na\nvar float lastSellPrice = na\nvar int lastBuyBarIndex = na\nvar int lastSellBarIndex = na\nvar bool buyEntryPlotted = false\nvar bool sellEntryPlotted = false\n\nif buySignal\n    lastBuyPrice := close * (1 - entryOffsetPerc / 100)\n    lastBuyBarIndex := bar_index\n    buyEntryPlotted := false\n\nif sellSignal\n    lastSellPrice := close * (1 + entryOffsetPerc / 100)\n    lastSellBarIndex := bar_index\n    sellEntryPlotted := false\n\n// === TP ve SL Hesapları ===\nlong_tp = lastBuyPrice * (1 + tpPerc / 100)\nlong_sl = lastBuyPrice * (1 - slPerc / 100)\nshort_tp = lastSellPrice * (1 - tpPerc / 100)\nshort_sl = lastSellPrice * (1 + slPerc / 100)\n\n// === TP / SL Temasları (yalnızca işlemden sonra ilk gelen hedef) ===\nhitLongTP = false\nhitLongSL = false\nhitShortTP = false\nhitShortSL = false\n\n// === Giriş Etiketleri ===\nvar label buyLabel = na\nvar label sellLabel = na\n\nif not na(lastBuyPrice) and not buyEntryPlotted and close <= lastBuyPrice and bar_index > lastBuyBarIndex\n    buyLabel := label.new(x=bar_index, y=low, text="Giriş", style=label.style_label_up, color=color.fuchsia, textcolor=color.white)\n    buyEntryPlotted := true\n    lastBuyBarIndex := bar_index\n\nif not na(lastSellPrice) and not sellEntryPlotted and close >= lastSellPrice and bar_index > lastSellBarIndex\n    sellLabel := label.new(x=bar_index, y=high, text="Giriş", style=label.style_label_down, color=color.fuchsia, textcolor=color.white)\n    sellEntryPlotted := true\n    lastSellBarIndex := bar_index\n\nif not na(lastBuyPrice) and buyEntryPlotted and bar_index > lastBuyBarIndex\n    if high >= long_tp\n        hitLongTP := true\n        lastBuyPrice := na\n    else if low <= long_sl\n        hitLongSL := true\n        lastBuyPrice := na\n\nif not na(lastSellPrice) and sellEntryPlotted and bar_index > lastSellBarIndex\n    if low <= short_tp\n        hitShortTP := true\n        lastSellPrice := na\n    else if high >= short_sl\n        hitShortSL := true\n        lastSellPrice := na\n\n// === Strateji Girişleri ===\nif buySignal\n    strategy.entry("BUY", strategy.long)\nif sellSignal\n    strategy.entry("SELL", strategy.short)\n\n// === SuperTrend Plot ===\nupPlot = plot(trend == 1 ? upperBand : na, title="Up Trend", style=plot.style_linebr, linewidth=2, color=color.green)\ndnPlot = plot(trend == -1 ? lowerBand : na, title="Down Trend", style=plot.style_linebr, linewidth=2, color=color.red)\n\n// === TP & SL Plot ===\nplotshape(hitLongTP, location=location.abovebar, style=shape.labeldown, color=color.green, text="TP", textcolor=color.white, title="TP Long")\nplotshape(hitLongSL, location=location.abovebar, style=shape.labeldown, color=color.red, text="Stop", textcolor=color.white, title="SL Long")\nplotshape(hitShortTP, location=location.belowbar, style=shape.labelup, color=color.green, text="TP", textcolor=color.white, title="TP Short")\nplotshape(hitShortSL, location=location.belowbar, style=shape.labelup, color=color.red, text="Stop", textcolor=color.white, title="SL Short")\n\n'

class SMSuperTrendAdvancedMultifunctionalSuperTrendTrendFollowi3a3353(PinePortBase, IStrategy):
    source_id = "SM_3a335374f535c98c"
    source_file = '高级多功能SuperTrend趋势跟踪策略与自动止盈止损系统-Advanced-Multi-functional-SuperTrend-Trend-Following-Strategy-with-Automated-Take-Profit-and-Stop-Loss-System.md'
    timeframe = '3d'
    can_short = True
    source_defaults = {'atrPeriod': 10, 'mult': 3.0, 'src': 'hl2', 'tpPerc': 2.5, 'slPerc': 1.0, 'entryOffsetPerc': 0.2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
