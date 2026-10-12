"""batch_011 port of 超级三指标RSI-MACD-BB动量反转策略-Super-Triple-Indicator-RSI-MACD-BB-Momentum-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-01 00:00:00\nend: 2024-05-31 23:59:59\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © lassgamer401\n\n//@version=4\nstrategy("Short DOTUSDT con Alertas", overlay=true)\n\n// Parámetros de la Estrategia\nrsiOverbought = input(70, title="RSI Overbought Level")\nmacdShort = input(12, title="MACD Short Period")\nmacdLong = input(26, title="MACD Long Period")\nmacdSignal = input(9, title="MACD Signal Period")\nstopLossPercent = input(3, title="Stop Loss Percent", type=input.float)/100\ntakeProfitPercent = input(6, title="Take Profit Percent", type=input.float)/100\n\n// Cálculo de Indicadores\nrsi = rsi(close, 14)\n[macdLine, signalLine, _] = macd(close, macdShort, macdLong, macdSignal)\n[upperBand, b, lowerBand] = bb(close, 20, 2)\n\n// Señal de Entrada Short\nisOverbought = rsi > rsiOverbought\nisMacdBearish = macdLine < signalLine\nisNearUpperBand = close > upperBand\n\nshortCondition = isOverbought and isMacdBearish and isNearUpperBand\n\n// Ejecución de la Estrategia\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    label.new(bar_index, na, "SELL", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)\n    alert("Señal de Venta: Iniciar una posición corta en DOTUSDT", alert.freq_once_per_bar)\n\n// Gestión del Riesgo\nstopLossLevel = strategy.position_avg_price * (1 + stopLossPercent)\ntakeProfitLevel = strategy.position_avg_price * (1 - takeProfitPercent)\nstrategy.exit("Take Profit/Stop Loss", "Short", stop=stopLossLevel, limit=takeProfitLevel)\n\n// Visualización de Indicadores\nplot(rsi, title="RSI", color=color.blue)\nhline(rsiOverbought, "Overbought Level", color=color.red)\nplot(macdLine, title="MACD Line", color=color.green)\nplot(signalLine, title="Signal Line", color=color.red)\nplot(upperBand, title="Upper Bollinger Band", color=color.purple)\nplot(lowerBand, title="Lower Bollinger Band", color=color.purple)\n\n// Mensajes de Alerta Visuales\nplotshape(series=shortCondition, title="Short Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")'

class SMF15DF358C920257B(PinePortBase, IStrategy):
    source_id = "SM_f15df358c920257b"
    source_file = '超级三指标RSI-MACD-BB动量反转策略-Super-Triple-Indicator-RSI-MACD-BB-Momentum-Reversal-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'rsiOverbought': 70, 'macdShort': 12, 'macdLong': 26, 'macdSignal': 9, 'stopLossPercent': 3, 'takeProfitPercent': 6}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'tuple', 'exit_order', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
