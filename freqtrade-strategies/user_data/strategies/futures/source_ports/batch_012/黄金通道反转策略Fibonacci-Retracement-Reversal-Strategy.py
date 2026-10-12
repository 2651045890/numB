"""batch_012 port of 黄金通道反转策略Fibonacci-Retracement-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-06 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("FBS Trade", overlay=true)\n\n// Fibonacci seviyeleri\nfibonacciLevels = input(0.618, title="Fibonacci Düzeltme Seviyesi")\n\n// RSI ayarları\nrsiLength = input(14, title="RSI Periyodu")\noverboughtLevel = input(70, title="RSI Satış Sinyali Seviyesi")\noversoldLevel = input(30, title="RSI Alış Sinyali Seviyesi")\n\n// Take Profit ve Stop Loss yüzdesi\ntakeProfitPercent = input(1, title="Take Profit Yüzdesi") / 100\nstopLossPercent = input(1, title="Stop Loss Yüzdesi") / 100\n\n// Fibonacci seviyelerini hesapla\nhighFibo = high * (1 + fibonacciLevels)\nlowFibo = low * (1 - fibonacciLevels)\n\n// RSI hesaplama\nrsiValue = ta.rsi(close, rsiLength)\n\n// Alış ve satış koşulları\nbuyCondition = close > lowFibo and rsiValue < 30\nsellCondition = close < highFibo and rsiValue > overboughtLevel\n\n// Take Profit ve Stop Loss seviyeleri\ntakeProfitLong = strategy.position_avg_price * (1 + takeProfitPercent)\nstopLossLong = strategy.position_avg_price * (1 - stopLossPercent)\n\ntakeProfitShort = strategy.position_avg_price * (1 - takeProfitPercent)\nstopLossShort = strategy.position_avg_price * (1 + stopLossPercent)\n\n// Alış ve satış işlemleri\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n\n// Take Profit ve Stop Loss seviyeleri\nif (strategy.position_size > 0)\n    strategy.exit("Take Profit/Close Buy", from_entry="Buy", limit=takeProfitLong, stop=stopLossLong)\nif (strategy.position_size < 0)\n    strategy.exit("Take Profit/Close Sell", from_entry="Sell", limit=takeProfitShort, stop=stopLossShort)\n\n// Sadece mumları ve buy/sell işlemlerini göster\nplot(close, color=color.black, title="Close")\n\n// Destek ve direnç bölgeleri\nsupportLevel = input(27, title="Fibonacci Destek Seviyesi")\nresistanceLevel = input(200, title="Direnç Seviyesi")\n\nhline(supportLevel, "Fibonacci Destek Seviyesi", color=color.green)\nhline(resistanceLevel, "Direnç Seviyesi", color=color.red)\n\n// Trend çizgileri\nvar line trendLine = na\nif (ta.crossover(close, highFibo))\n    trendLine := line.new(bar_index[1], highFibo[1], bar_index, highFibo, color=color.green, width=2)\nif (ta.crossunder(close, lowFibo))\n    trendLine := line.new(bar_index[1], lowFibo[1], bar_index, lowFibo, color=color.red, width=2)\n\n// RSI ve Fibo\'yu grafiğe çizme\nhline(overboughtLevel, "RSI Satış Sinyali", color=color.red, linestyle=hline.style_dashed)\nhline(oversoldLevel, "RSI Alış Sinyali", color=color.green, linestyle=hline.style_dashed)\nplot(rsiValue, color=color.purple, title="RSI")\n\n// 15 dakikalıkta 3 mumda bir alarm\nis15MinBar = ta.change(time(\'15\'), 1)\nif (is15MinBar % 3 == 0)\n    alert("15 dakikalıkta 3 mum geçti.")\n\n'

class SMFibonacciRetracementReversalStrategy8f8db6(PinePortBase, IStrategy):
    source_id = "SM_8f8db6b63fbb77ae"
    source_file = '黄金通道反转策略Fibonacci-Retracement-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fibonacciLevels': 0.618, 'rsiLength': 14, 'overboughtLevel': 70, 'oversoldLevel': 30, 'supportLevel': 27, 'resistanceLevel': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
