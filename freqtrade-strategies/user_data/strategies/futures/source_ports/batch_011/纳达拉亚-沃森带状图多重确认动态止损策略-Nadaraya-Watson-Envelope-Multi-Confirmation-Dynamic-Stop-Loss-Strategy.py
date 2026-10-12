"""batch_011 port of 纳达拉亚-沃森带状图多重确认动态止损策略-Nadaraya-Watson-Envelope-Multi-Confirmation-Dynamic-Stop-Loss-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-18 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Nadaraya-Watson Envelope with Multi-Confirmation and Dynamic Stop-Loss", overlay=true)\n\n// Input parameters\nh = input.float(7.2, "Bandwidth", minval=0)\nmult = input.float(2.1, minval=0)\nsrc = input(close, "Source")\n\n// ADX and DI Input Parameters\nadxLength = input.int(14, "ADX Length")\nadxThreshold = input.float(25, "ADX Threshold")\nadxSmoothing = input.int(14, "ADX Smoothing")\n\n// Calculate ADX and DI\n[dmiPlus, dmiMinus, adx] = ta.dmi(adxLength, adxSmoothing)\nstrongTrendUp = dmiPlus > dmiMinus and adx > adxThreshold\nstrongTrendDown = dmiMinus > dmiPlus and adx > adxThreshold\n\n// Nadaraya-Watson Envelope Calculation\ngauss(x, h) =>\n    math.exp(-(math.pow(x, 2) / (h * h * 2)))\n\ncoefs = array.new_float(0)\nden = 0.0\n\nfor i = 0 to 100\n    w = gauss(i, h)\n    array.push(coefs, w)\n\nden := array.sum(coefs)\n\nout = 0.0\nfor i = 0 to 100\n    out += src[i] * array.get(coefs, i)\nout /= den\nmae = ta.sma(math.abs(src - out), 100) * mult\n\nupper = ta.sma(out + mae, 10)\nlower = ta.sma(out - mae, 10)\n\n// Confirmations\nbreakoutUp = ta.crossover(src, upper)\nbreakoutDown = ta.crossunder(src, lower)\n\n// Original RSI period and thresholds\nrsiPeriod = input.int(14, "RSI Period")\nrsi = ta.rsi(src, rsiPeriod)\nmomentumUp = rsi > 70 and adx > adxThreshold\nmomentumDown = rsi < 30 and adx > adxThreshold\n\n// // Plot ADX-based Trend Confirmation Lines\n// if (strongTrendUp)\n//     line.new(bar_index, low, bar_index + 1, low, color=color.new(color.blue, 50), width=2, style=line.style_dashed)\n\n// if (strongTrendDown)\n//     line.new(bar_index, high, bar_index + 1, high, color=color.new(color.red, 50), width=2, style=line.style_dashed)\n\n// Plot Breakout Confirmation Dots\nplotshape(series=breakoutUp, style=shape.circle, location=location.abovebar, color=color.blue, size=size.tiny, title="Breakout Up")\nplotshape(series=breakoutDown, style=shape.circle, location=location.belowbar, color=color.orange, size=size.tiny, title="Breakout Down")\n\n// Plot Momentum Confirmation Arrows\nplotshape(series=momentumUp, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.tiny, title="Momentum Up")\nplotshape(series=momentumDown, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.tiny, title="Momentum Down")\n\n// Strategy Entry and Exit\nvar float stopLossLevel = na\nvar float highestPrice = na\n\npotentialBuy = strongTrendUp and breakoutUp\npotentialSell = strongTrendDown and breakoutDown\nmomentumConfirmUp = potentialBuy and momentumUp\nmomentumConfirmDown = potentialSell and momentumDown\n\nif (momentumConfirmUp)\n    strategy.entry("Buy", strategy.long)\n    stopLossLevel := close * 0.90\n    highestPrice := close\n\nif (momentumConfirmDown)\n    strategy.entry("Sell", strategy.short)\n    stopLossLevel := close * 1.10\n    highestPrice := close\n\nif (strategy.position_size > 0)\n    highestPrice := math.max(highestPrice, close)\n    stopLossLevel := math.max(highestPrice * 0.85, close * 0.90)\n\nif (strategy.position_size < 0)\n    highestPrice := math.min(highestPrice, close)\n    stopLossLevel := math.min(highestPrice * 1.15, close * 1.10)\n\n// Close position if stop loss is hit\nif (strategy.position_size > 0 and close < stopLossLevel)\n    strategy.close("Buy")\n\nif (strategy.position_size < 0 and close > stopLossLevel)\n    strategy.close("Sell")\n'

class SM8E932559600E2BDE(PinePortBase, IStrategy):
    source_id = "SM_8e932559600e2bde"
    source_file = '纳达拉亚-沃森带状图多重确认动态止损策略-Nadaraya-Watson-Envelope-Multi-Confirmation-Dynamic-Stop-Loss-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'h': 7.2, 'mult': 2.1, 'adxLength': 14, 'adxThreshold': 25, 'adxSmoothing': 14, 'rsiPeriod': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'array', 'loop', 'broker_state', 'tuple', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
