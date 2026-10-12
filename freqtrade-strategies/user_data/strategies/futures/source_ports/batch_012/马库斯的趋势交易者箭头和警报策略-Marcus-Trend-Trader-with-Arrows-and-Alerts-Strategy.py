"""batch_012 port of 马库斯的趋势交易者箭头和警报策略-Marcus-Trend-Trader-with-Arrows-and-Alerts-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-23 00:00:00\nend: 2024-03-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Trend Trader by Marcus Flechas y Alertas", overlay=true)\n\n// Parámetros de las medias móviles\nlongitudRapida = input(9, "Longitud Media Rápida")\nlongitudLenta = input(21, "Longitud Media Lenta")\n\n// Cálculo de las medias móviles\nmediaRapida = ta.ema(close, longitudRapida)\nmediaLenta = ta.ema(close, longitudLenta)\n\n// Condición de compra (cruce al alza)\ncomprar = ta.crossover(mediaRapida, mediaLenta)\n\n// Condición de venta (cruce a la baja)\nvender = ta.crossunder(mediaRapida, mediaLenta)\n\n// Dibujando las flechas para las señales\nplotshape(comprar, title="Compra", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(vender, title="Venta", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n\n// Colores del Trend Trader Indicator (opcional)\ncolorTendencia = mediaRapida > mediaLenta ? color.green : color.red\nplot(mediaRapida, color=colorTendencia, title="Media Rápida")\nplot(mediaLenta, color=color.blue, title="Media Lenta")\n\n// Implementando la estrategia\nstrategy.entry("Compra", strategy.long, when=comprar)\nstrategy.close("Compra", when=vender)\n\n// Condiciones de alerta\nalertcondition(comprar, title="Alerta de Compra", message="Señal de Compra activada")\nalertcondition(vender, title="Alerta de Venta", message="Señal de Venta activada")\n\n'

class SMMarcusTrendTraderwithArrowsandAlertsStrategy585a3f(PinePortBase, IStrategy):
    source_id = "SM_585a3fb79726cf6e"
    source_file = '马库斯的趋势交易者箭头和警报策略-Marcus-Trend-Trader-with-Arrows-and-Alerts-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'longitudRapida': 9, 'longitudLenta': 21}
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
