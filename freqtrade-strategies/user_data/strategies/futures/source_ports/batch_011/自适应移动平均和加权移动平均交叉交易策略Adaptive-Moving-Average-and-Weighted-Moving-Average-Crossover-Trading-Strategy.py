"""batch_011 port of 自适应移动平均和加权移动平均交叉交易策略Adaptive-Moving-Average-and-Weighted-Moving-Average-Crossover-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © SDTA\n\n//@version=5\nstrategy("AIOMA-WMA Strategy", overlay=true)\n\n// Parametreler\naioma_length = input(14, "AIOMA Length")\nwma_length = input(21, "WMA Length")\n\n// AIOMA hesaplama\nlength1 = aioma_length\nema1 = ta.ema(close, length1)\nlength2 = aioma_length\nema2 = ta.ema(ema1, length2)\nlength3 = aioma_length\nema3 = ta.ema(ema2, length3)\nlength4 = aioma_length\nema4 = ta.ema(ema3, length4)\naioma = ta.ema(ema4, aioma_length)\n\n// WMA hesaplama\nwma = ta.wma(close, wma_length)\n\n// Kesişim kontrolü\ncross_up = ta.crossover(wma, aioma)\ncross_down = ta.crossunder(wma, aioma)\n\n// İşlem fonksiyonu\nenterTrade(dir, price, signalText, color) =>\n    if dir\n        strategy.entry("Enter", strategy.long)\n        label.new(x = bar_index, y = price, text = signalText, color = color, textcolor = color, style = label.style_label_up, size = size.small, tooltip = "Entry Signal")\n    else if not dir\n        strategy.entry("Exit", strategy.short)\n        label.new(x = bar_index, y = price, text = signalText, color = color, textcolor = color, style = label.style_label_down, size = size.small, tooltip = "Exit Signal")\n\n// Long pozisyon girişi\nif cross_up\n    enterTrade(true, low, "Buy Signal", color.green)\n\n// Short pozisyon girişi\nif cross_down\n    enterTrade(false, high, "Sell Signal", color.red)\n\n// Pozisyon kapatma\nif cross_up and strategy.position_size > 0\n    strategy.close("Enter")\nif cross_down and strategy.position_size < 0\n    strategy.close("Exit")\n\n// Grafiğe plot\nplot(aioma, color=color.blue, linewidth=2, title="AIOMA")\nplot(wma, color=color.red, linewidth=2, title="WMA")\n'

class SMEE8E7B138D914B12(PinePortBase, IStrategy):
    source_id = "SM_ee8e7b138d914b12"
    source_file = '自适应移动平均和加权移动平均交叉交易策略Adaptive-Moving-Average-and-Weighted-Moving-Average-Crossover-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'aioma_length': 14, 'wma_length': 21}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
