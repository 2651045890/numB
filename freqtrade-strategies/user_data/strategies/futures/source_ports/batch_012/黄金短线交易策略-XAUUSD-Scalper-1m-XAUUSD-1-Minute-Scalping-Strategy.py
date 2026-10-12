"""batch_012 port of 黄金短线交易策略-XAUUSD-Scalper-1m-XAUUSD-1-Minute-Scalping-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-27 00:00:00\nend: 2024-03-28 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("XAUUSD Scalper 1m Revisi", overlay=true)\n\n// Menggunakan ATR untuk SL dan TP dinamis\nfloat atr = ta.atr(14)\nfloat slMultiplier = 30\nfloat tpMultiplier = 30\nfloat slPrice = atr * slMultiplier\nfloat tpPrice = atr * tpMultiplier\n\n// Menggunakan EMA untuk respons yang lebih cepat\nint shortEmaLength = 14\nint longEmaLength = 28\nemaShort = ta.ema(close, shortEmaLength)\nemaLong = ta.ema(close, longEmaLength)\n\n// Kondisi untuk entry\nlongCondition = ta.crossover(emaShort, emaLong)\nshortCondition = ta.crossunder(emaShort, emaLong)\n\n// Fungsi untuk menggambar garis stop loss dan take profit\ndrawLines(entryPrice, isLong) =>\n    slLevel = isLong ? entryPrice - slPrice : entryPrice + slPrice\n    tpLevel = isLong ? entryPrice + tpPrice : entryPrice - tpPrice\n    // line.new(bar_index, slLevel, bar_index + 1, slLevel, width=2, color=color.red)\n    // line.new(bar_index, tpLevel, bar_index + 1, tpLevel, width=2, color=color.green)\n\n// Plot panah untuk entry dan menggambar garis SL dan TP\nif (longCondition)\n    // label.new(bar_index, low, "⬆️", color=color.green, size=size.large, textcolor=color.white, style=label.style_label_up)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", "Long", loss=slPrice, profit=tpPrice)\n    drawLines(close, true)\n\nif (shortCondition)\n    // label.new(bar_index, high, "⬇️", color=color.red, size=size.large, textcolor=color.white, style=label.style_label_down)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", "Short", loss=slPrice, profit=tpPrice)\n    drawLines(close, false)\n'

class SMXAUUSDScalper1mXAUUSD1MinuteScalpingStrategybea1ce(PinePortBase, IStrategy):
    source_id = "SM_bea1ce3d41087587"
    source_file = '黄金短线交易策略-XAUUSD-Scalper-1m-XAUUSD-1-Minute-Scalping-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
