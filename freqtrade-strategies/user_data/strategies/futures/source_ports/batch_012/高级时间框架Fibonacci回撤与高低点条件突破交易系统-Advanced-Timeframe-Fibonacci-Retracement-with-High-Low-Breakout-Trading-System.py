"""batch_012 port of 高级时间框架Fibonacci回撤与高低点条件突破交易系统-Advanced-Timeframe-Fibonacci-Retracement-with-High-Low-Breakout-Trading-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fibonacci Levels Strategy with High/Low Criteria", overlay = true)\n\n// Kullanıcıdan yüksek zaman dilimini ve mum bilgilerini al\ntimeframe = input.timeframe(defval = "D", title = "Higher Time Frame")\ncurrentlast = input.string(defval = "Last", title = "Current or Last HTF Candle", options = ["Current", "Last"])\n\n// Kullanıcıdan en düşük ve en yüksek fiyat bakış sürelerini al\nlowestLookback = input(20, "Lowest Price Lookback", tooltip="The strategy will BUY when the price crosses over the lowest it has been in the last X amount of bars")\nhighestLookback = input(10, "Highest Price Lookback", tooltip="If Take-Profit is not checked, the strategy will SELL when the price crosses under the highest it has been in the last X amount of bars")\n\n// Fibonacci seviyeleri ayarları\nlevel0 = input.float(defval = 0.000, title = "Level 0")\nlevel1 = input.float(defval = 0.236, title = "Level 1")\nlevel2 = input.float(defval = 0.382, title = "Level 2")\nlevel3 = input.float(defval = 0.500, title = "Level 3")\nlevel4 = input.float(defval = 0.618, title = "Level 4")\nlevel5 = input.float(defval = 0.786, title = "Level 5")\nlevel100 = input.float(defval = 1.000, title = "Level 100")\n\n// HTF mumlarını hesapla\nnewbar = ta.change(time(timeframe)) != 0 \nvar float htfhigh = high\nvar float htflow = low\nvar float htfopen = open\nfloat htfclose = close\nvar counter = 0\n\nif newbar\n    htfhigh := high\n    htflow := low\n    htfopen := open\n    counter := 0\nelse\n    htfhigh := math.max(htfhigh, high)\n    htflow := math.min(htflow, low)\n    counter += 1\n\nvar float open_ = na\nvar float high_ = na\nvar float low_ = na\nvar float close_ = na\nif currentlast == "Last" and newbar\n    open_ := htfopen[1]\n    high_ := htfhigh[1]\n    low_ := htflow[1]\n    close_ := htfclose[1]\nelse if currentlast == "Current"\n    open_ := htfopen\n    high_ := htfhigh\n    low_ := htflow\n    close_ := htfclose\n\n// Fibonacci seviyelerini hesapla\nvar float[] fibLevels = array.new_float(6)\narray.set(fibLevels, 0, open_ + (high_ - low_) * level0)\narray.set(fibLevels, 1, open_ + (high_ - low_) * level1)\narray.set(fibLevels, 2, open_ + (high_ - low_) * level2)\narray.set(fibLevels, 3, open_ + (high_ - low_) * level3)\narray.set(fibLevels, 4, open_ + (high_ - low_) * level4)\narray.set(fibLevels, 5, open_ + (high_ - low_) * level5)\n\n// Fibonacci seviyelerini grafik üzerine çiz\nplot(array.get(fibLevels, 0), color=color.new(color.blue, 75), title="Fibonacci Level 0")\nplot(array.get(fibLevels, 1), color=color.new(color.green, 75), title="Fibonacci Level 1")\nplot(array.get(fibLevels, 2), color=color.new(color.red, 75), title="Fibonacci Level 2")\nplot(array.get(fibLevels, 3), color=color.new(color.orange, 75), title="Fibonacci Level 3")\nplot(array.get(fibLevels, 4), color=color.new(color.teal, 75), title="Fibonacci Level 4")\nplot(array.get(fibLevels, 5), color=color.new(color.navy, 75), title="Fibonacci Level 5")\n\n// En düşük ve en yüksek fiyat kriterlerini hesapla\nlowcriteria = ta.lowest(low, lowestLookback)[1]\nhighcriteria = ta.highest(high, highestLookback)[1]\n\nplot(highcriteria, color=color.green, title="Highest Price Criteria")\nplot(lowcriteria, color=color.red, title="Lowest Price Criteria")\n\n// Fibonacci seviyeleri ile ticaret sinyalleri oluştur\nlongCondition = close > lowcriteria and close > array.get(fibLevels, 3) // En düşük kriterin ve Fibonacci seviyesinin üstüne çıkarsa alım\nshortCondition = close < highcriteria and close < array.get(fibLevels, 3) // En yüksek kriterin ve Fibonacci seviyesinin altına düşerse satış\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n'

class SMFibonacciAdvancedTimeframeFibonacciRetracementwithHighL0695f1(PinePortBase, IStrategy):
    source_id = "SM_0695f1c9151eac17"
    source_file = '高级时间框架Fibonacci回撤与高低点条件突破交易系统-Advanced-Timeframe-Fibonacci-Retracement-with-High-Low-Breakout-Trading-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'timeframe': 'D', 'currentlast': 'Last', 'lowestLookback': 20, 'highestLookback': 10, 'level0': 0.0, 'level1': 0.236, 'level2': 0.382, 'level3': 0.5, 'level4': 0.618, 'level5': 0.786, 'level100': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Array/matrix operations are present and are not parity-certified by the generic adapter.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
