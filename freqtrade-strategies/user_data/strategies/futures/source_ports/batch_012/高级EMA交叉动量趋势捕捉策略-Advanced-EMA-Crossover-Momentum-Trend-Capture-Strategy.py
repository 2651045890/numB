"""batch_012 port of 高级EMA交叉动量趋势捕捉策略-Advanced-EMA-Crossover-Momentum-Trend-Capture-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-14 00:00:00\nend: 2025-03-12 08:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © fatihcan\n\n//@version=6\nstrategy("EMA Scalping - No Stop Loss", overlay=true, commission_type=strategy.commission.percent, commission_value=0.1)\n\n// User Inputs\nemaLen = input.int(13, "EMA Length", minval=1, tooltip="Balanced reaction")\nadxLen = input.int(14, "ADX Length", minval=1)\nadxThreshold = input.int(30, "ADX Threshold", minval=0, maxval=100, tooltip="Strong trend confirmation")\natrLength = input.int(14, "ATR Length", minval=1)\natrProfitMultiplier = input.float(1.5, "Profit ATR Multiplier", minval=0.1, step=0.1, tooltip="Profitable exit")\nvolumeMALen = input.int(5, "Volume MA Length", minval=1)\nvolumeThreshold = input.float(1.5, "Volume Multiplier", minval=1.0, step=0.1)\n\n// Calculations\nemaValue = ta.ema(close, emaLen)\nbuySignal = ta.crossover(close, emaValue)\nsellSignal = ta.crossunder(close, emaValue)\n\n[diPlus, diMinus, adx] = ta.dmi(adxLen, adxLen)\nstrongTrend = adx > adxThreshold\n\nvolumeMA = ta.sma(volume, volumeMALen)\nvolumeSpike = volume > volumeMA * volumeThreshold\n\natr = ta.atr(atrLength)\n\n// Strong Confirmation Filter: A candle must close in the same direction after the crossover\nbuyConfirm = buySignal and close > open  // Buy signal + green candle\nsellConfirm = sellSignal and close < open  // Sell signal + red candle\n\nvar float longProfitTarget = na\nvar float shortProfitTarget = na\n\n// Position Status Check\ninLong = strategy.position_size > 0\ninShort = strategy.position_size < 0\n\n// Buy and Sell Signals\nif (buyConfirm and strongTrend and volumeSpike and not inShort)\n    longProfitTarget := close + (atr * atrProfitMultiplier)\n    strategy.entry("Long", strategy.long)\n\nif (sellConfirm and strongTrend and volumeSpike and not inLong)\n    shortProfitTarget := close - (atr * atrProfitMultiplier)\n    strategy.entry("Short", strategy.short)\n\n// Exit Conditions (Profit Target Only)\nif (inLong)\n    if (high >= longProfitTarget)\n        strategy.close("Long", comment="Profit Target")\n\nif (inShort)\n    if (low <= shortProfitTarget)\n        strategy.close("Short", comment="Profit Target")\n\n// Visualization\nplot(emaValue, "EMA", color=color.blue, linewidth=2)\nplotshape(buyConfirm and strongTrend and volumeSpike and not inShort, title="Buy", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.tiny, text="BUY")\nplotshape(sellConfirm and strongTrend and volumeSpike and not inLong, title="Sell", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.tiny, text="SELL")\nplot(longProfitTarget, "Long Profit Target", color=color.green, style=plot.style_cross, linewidth=1, trackprice=true)\nplot(shortProfitTarget, "Short Profit Target", color=color.red, style=plot.style_cross, linewidth=1, trackprice=true)\n\n// Alerts\nalertcondition(buyConfirm and strongTrend and volumeSpike and not inShort, title="Buy Signal", message="Buy signal - Strong bullish trend!")\nalertcondition(sellConfirm and strongTrend and volumeSpike and not inLong, title="Sell Signal", message="Sell signal - Strong bearish trend!")\nalertcondition(high >= longProfitTarget, title="Take Profit Long", message="Long profit target reached!")\nalertcondition(low <= shortProfitTarget, title="Take Profit Short", message="Short profit target reached!")\n\n'

class SMEMAAdvancedEMACrossoverMomentumTrendCaptureStrategy0578e3(PinePortBase, IStrategy):
    source_id = "SM_0578e3beef825edf"
    source_file = '高级EMA交叉动量趋势捕捉策略-Advanced-EMA-Crossover-Momentum-Trend-Capture-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'emaLen': 13, 'adxLen': 14, 'adxThreshold': 30, 'atrLength': 14, 'atrProfitMultiplier': 1.5, 'volumeMALen': 5, 'volumeThreshold': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
