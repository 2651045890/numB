"""batch_012 port of 采用双移动均线交易策略Dual-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-18 00:00:00\nend: 2024-02-17 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © technicalTruff99446\n\n//@version=4\nstrategy("AhmetMSA", overlay=true, initial_capital = 10000, commission_value = 0.002, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0, calc_on_order_fills = true)\n//2. DEĞERDEN SONRA GEÇMİŞ HESAPLAMA DEĞERİ, KOMİSYON ORANI, PARANIN TAMAMI, DEĞERLERİ EKLEMDİ\n\nemaShPD = input (title="EMA KISA PERİYOT", defval=9, minval=1)\nemaLngPD = input (title="EMA UZUN PERİYOT", defval=21, minval=1)\n\n//input   DEĞİŞKEN DEĞER ATAMA\n\nema1 = ema (close,emaShPD)\nema2 = ema (close,emaLngPD)\n\n//EMALAR ARASINI BOYAMA upTrend downTrend\nupTrend   = plot (ema1, color=#4DFF00, linewidth=2, title= "EMA KISA", transp=0)\ndownTrend = plot (ema2, color=#FF0C00, linewidth=3, title= "EMA UZUN", transp=0)\n//linewidth ÇİZGİ KALINLIĞI\n//title     İSİM VERME\n\n//BACKTESTİN BAŞLANGIÇ TARİHİNİ BELİRLEME\nyearin = input(2024, title = "Backtest Başlangıç Tarihi")\n//longCondition = crossover(ema1, ema2)\n//shortCondition = crossover(ema2, ema1)\nbuy = crossover(ema1, ema2) and yearin >= year\nsell = crossover(ema2, ema1) and yearin >= year\n//ta.crossunder  KESİŞİM KODU\n\n//Barları BOYAMA\nbarbuy  = ema1 >= ema2\nbarsell = ema2 <  ema1\n\n\n\n\n//AL SAT AŞK KUTUCUKLU EKRANA YAZMA\nplotshape(buy, title = "AL AŞK", text = \'AL AŞK\', style = shape.labelup, location = location.belowbar, color= color.green,   textcolor = color.white, transp = 0, size = size.tiny)\nplotshape(sell, title = "SAT AŞK", text = \'SAT AŞK\', style = shape.labeldown, location = location.abovebar, color= color.red,   textcolor = color.white, transp = 0, size = size.tiny)\n\n//Barları BOYAMA KOŞULU\nbarcolor(barbuy? #4DFF00: barsell? #FF0C00: #FF0C00)\n\n\nfill(upTrend, downTrend, color = ema1 >= ema2?#4DFF00 : #FF0C00, transp = 80, title = "bgcolor")\n\n//longCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))\n//shortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))\n//14 GÜNLÜĞÜN KAPANIŞDEĞERİNİN 28 GÜNLÜK KAPANIŞ DEĞERİNİ KESMESİ KOŞULU\n\n\n\nif (buy)\n    strategy.entry("AL AŞK", strategy.long)\n\n\nif (sell)\n    strategy.entry("SAT AŞK", strategy.short)\n\n'

class SMDualMovingAverageTradingStrategy2e5d50(PinePortBase, IStrategy):
    source_id = "SM_2e5d50ee435ef328"
    source_file = '采用双移动均线交易策略Dual-Moving-Average-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'emaShPD': 9, 'emaLngPD': 21, 'yearin': 2024}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.002
    source_pyramiding = 0
    source_initial_capital = 10000
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
