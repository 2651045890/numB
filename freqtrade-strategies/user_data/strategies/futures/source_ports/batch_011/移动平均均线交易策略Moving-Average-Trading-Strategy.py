"""batch_011 port of 移动平均均线交易策略Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-26 00:00:00\nend: 2024-02-25 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia MA - mejor", overlay=true)\n\n// Parámetros de la estrategia\ninitialCapital = 1000  // Inversión inicial\nriskPerTrade = 0.02  // Riesgo por operación (2% del capital por operación)\nlengthMA = 14  // Período de la media móvil\npipValue = 20 / 10  // Valor de un pip (30 euros / 10 pips)\n\n// Apalancamiento\nleverage = 10\n\n// Cálculo de la media móvil en el marco temporal de 30 minutos\nma = request.security(syminfo.tickerid, "30", ta.sma(close, lengthMA))\n\n// Condiciones de Entrada en Sobreventa\nentryCondition = close < ma * 0.99  // Ejemplo: 1% por debajo de la MA\n\n// Lógica de entrada y salida\nif entryCondition\n    riskAmount = initialCapital * riskPerTrade  // Cantidad de euros a arriesgar por operación\n    size = 1  // Tamaño de la posición con apalancamiento\n    strategy.entry("Long", strategy.long, qty=size)\n    stopLossPrice = close - (10 * pipValue / size)\n    takeProfitPrice = close + (60 * pipValue / size)\n    strategy.exit("Exit Long", "Long", stop=stopLossPrice, limit=takeProfitPrice)\n\n// Gráficos\nplot(ma, color=color.blue, title="Media Móvil")\nplotshape(series=entryCondition, title="Entrada en Sobreventa", location=location.belowbar, color=color.green, style=shape.labelup, text="↑ Compra")\n'

class SMA82AF5E71EE3E4A9(PinePortBase, IStrategy):
    source_id = "SM_a82af5e71ee3e4a9"
    source_file = '移动平均均线交易策略Moving-Average-Trading-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
