"""batch_012 port of 高低突破策略结合Alpha趋势和移动平均线过滤-High-Low-Breakout-Strategy-with-Alpha-Trend-and-Moving-Average-Filter.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-25 00:00:00\nend: 2024-07-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("TRMUS", overlay=true)\n\n// Kullanıcının ayarlayabileceği mum sayısı\nlength = input.int(20, minval=1, title="Number of Bars")\n\n// Stop Loss ve Take Profit seviyeleri\nstopLossPerc = input.float(2.0, title="Stop Loss %", minval=0.0) / 100.0\ntakeProfitPerc = input.float(4.0, title="Take Profit %", minval=0.0) / 100.0\n\n// Trend filtresi için hareketli ortalama\nmaLength = input.int(50, minval=1, title="Moving Average Length")\nma = ta.sma(close, maLength)\n\n// ATR ve Alpha Trend parametreleri\nlengthATR = input.int(14, minval=1, title="ATR Length")\nmultiplier = input.float(1.5, minval=0.1, step=0.1, title="Multiplier")\n\n// ATR hesaplaması\natr = ta.atr(lengthATR)\n\n// Alpha Trend hesaplaması\nupperLevel = close + (multiplier * atr)\nlowerLevel = close - (multiplier * atr)\n\nvar float alphaTrend = na\nalphaTrend := na(alphaTrend[1]) ? close : (close > lowerLevel[1] ? math.max(alphaTrend[1], lowerLevel) : close < upperLevel[1] ? math.min(alphaTrend[1], upperLevel) : alphaTrend[1])\n\n// Son belirlenen mumun en yüksek ve en düşük kapanış fiyatlarını hesaplayalım\nhighestClose = ta.highest(close, length)\nlowestClose = ta.lowest(close, length)\n\n// Alım ve satım sinyalleri\nbuySignal = close > highestClose[1] and close[1] <= highestClose[1] and close > ma and close > alphaTrend\nsellSignal = close < lowestClose[1] and close[1] >= lowestClose[1] and close < ma and close < alphaTrend\n\n// Alım işlemi\nif (buySignal)\n    strategy.entry("Buy", strategy.long, stop=close * (1 - stopLossPerc), limit=close * (1 + takeProfitPerc))\n\n// Satım işlemi\nif (sellSignal)\n    strategy.entry("Sell", strategy.short, stop=close * (1 + stopLossPerc), limit=close * (1 - takeProfitPerc))\n\n// Grafik üzerine göstergeler ekleyelim\nplot(highestClose, color=color.green, linewidth=2, title="Highest Close")\nplot(lowestClose, color=color.red, linewidth=2, title="Lowest Close")\nplot(ma, color=color.blue, linewidth=2, title="Moving Average")\nplot(alphaTrend, color=color.orange, linewidth=2, title="Alpha Trend")\n\n// Alım ve satım sinyalleri için işaretleyiciler ekleyelim\nplotshape(series=buySignal, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal", text="BUY")\nplotshape(series=sellSignal, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal", text="SELL")\n\n'

class SMAlphaHighLowBreakoutStrategywithAlphaTrendandMovingAver6f0560(PinePortBase, IStrategy):
    source_id = "SM_6f056025ec151cb3"
    source_file = '高低突破策略结合Alpha趋势和移动平均线过滤-High-Low-Breakout-Strategy-with-Alpha-Trend-and-Moving-Average-Filter.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'maLength': 50, 'lengthATR': 14, 'multiplier': 1.5}
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
