"""batch_012 port of 高级MACD均线交叉交易策略结合自适应风险管理-Advanced-MACD-Crossover-Trading-Strategy-with-Adaptive-Risk-Management.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-04 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia MACD", overlay=true)\n\n// Parámetros entrada\ndireccion = input.string("ambas", "Dirección de operaciones", options=["larga", "corta", "ambas"])\nvelas_sl = input.int(3, "Velas para calcular Stop Loss", minval=1)\nratio = input.float(1.5, "Ratio Beneficio:Riesgo", minval=0.5)\nrapida = input.int(12, "Periodo Media Rápida")\nlenta = input.int(26, "Periodo Media Lenta")\nsenal = input.int(9, "Periodo Señal")\n\n// Calcular MACD\n[macdLinea, senalLinea, histograma] = ta.macd(close, rapida, lenta, senal)\n\n// Señales\nsenal_larga = ta.crossover(macdLinea, senalLinea) and histograma > 0\nsenal_corta = ta.crossunder(macdLinea, senalLinea) and histograma < 0\n\n// Gestión de riesgo\ncalcular_sl_largo() => ta.lowest(low, velas_sl)\ncalcular_sl_corto() => ta.highest(high, velas_sl)\n\ncalcular_tp(entrada, sl, es_larga) =>\n    distancia = math.abs(entrada - sl)\n    es_larga ? entrada + (distancia * ratio) : entrada - (distancia * ratio)\n\n// Operaciones\nsl_largo = calcular_sl_largo()\nsl_corto = calcular_sl_corto()\n\nif (direccion != "corta" and senal_larga and strategy.position_size == 0)\n    entrada = close\n    tp = calcular_tp(entrada, sl_largo, true)\n    strategy.entry("Larga", strategy.long)\n    strategy.exit("Salida Larga", "Larga", stop=sl_largo, limit=tp)\n\nif (direccion != "larga" and senal_corta and strategy.position_size == 0)\n    entrada = close\n    tp = calcular_tp(entrada, sl_corto, false)\n    strategy.entry("Corta", strategy.short)\n    strategy.exit("Salida Corta", "Corta", stop=sl_corto, limit=tp)\n\n// Visualización\nplotshape(senal_larga and direccion != "corta", "Compra", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.normal)\nplotshape(senal_corta and direccion != "larga", "Venta", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.normal)\n'

class SMMACDAdvancedMACDCrossoverTradingStrategywithAdaptiveRis373380(PinePortBase, IStrategy):
    source_id = "SM_37338072c65415e0"
    source_file = '高级MACD均线交叉交易策略结合自适应风险管理-Advanced-MACD-Crossover-Trading-Strategy-with-Adaptive-Risk-Management.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'direccion': 'ambas', 'velas_sl': 3, 'ratio': 1.5, 'rapida': 12, 'lenta': 26, 'senal': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
