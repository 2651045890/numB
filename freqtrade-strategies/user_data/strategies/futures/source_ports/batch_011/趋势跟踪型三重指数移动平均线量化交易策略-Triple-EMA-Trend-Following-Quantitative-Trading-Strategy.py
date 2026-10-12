"""batch_011 port of 趋势跟踪型三重指数移动平均线量化交易策略-Triple-EMA-Trend-Following-Quantitative-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-28 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia de Largo con Medias Móviles", overlay=true)\n\n// Parámetros ajustables de las medias móviles\nfast_length = input.int(10, title="Período de Media Rápida", minval=3, maxval=20)\nmid_length = input.int(30, title="Período de Media Intermedia", minval=21, maxval=60)\nslow_length = input.int(130, title="Período de Media Lenta (EMA 130)", minval=130)\n\n// Calcular las medias móviles\nfast_ma = ta.ema(close, fast_length)\nmid_ma = ta.ema(close, mid_length)\nslow_ma = ta.ema(close, slow_length) // Media lenta exponencial de 130 periodos\n\n// Calcular la pendiente manualmente (restando el valor actual de la media móvil del valor de 1 barra anterior)\nslope_ma130 = slow_ma - slow_ma[1]  // Pendiente de la media lenta\nslope_mid_ma = mid_ma - mid_ma[1]   // Pendiente de la media intermedia\n\n// Condición para pendiente positiva de la media lenta\nslow_ma_trending_up = slope_ma130 > 0\n\n// Condición para pendiente positiva de la media intermedia\nmid_ma_trending_up = slope_mid_ma > 0\n\n// Condiciones para entrada en largo (Cruce de la media rápida sobre la media intermedia, solo si la media intermedia tiene pendiente positiva y la media lenta también tiene pendiente positiva)\nlong_condition = ta.crossover(fast_ma, mid_ma) and mid_ma_trending_up and slow_ma_trending_up\n\n// Condiciones para entrada adicional (Cruce de la media rápida sobre la media lenta, solo si la media lenta tiene pendiente positiva)\nadditional_long_condition = ta.crossover(fast_ma, slow_ma) and slow_ma_trending_up\n\n// Condiciones para cierre de la posición (Cruce de la media rápida por debajo de la media intermedia)\nexit_condition = ta.crossunder(fast_ma, mid_ma)\n\n// Abrir la posición si se cumplen las condiciones (incluyendo las pendientes de las medias)\nif (long_condition or additional_long_condition)\n    strategy.entry("Comprar", strategy.long)\n\n// Cerrar la posición si se cumplen las condiciones de salida\nif (exit_condition)\n    strategy.close("Comprar")\n\n// Mostrar las medias móviles en el gráfico\nplot(fast_ma, color=color.green, linewidth=1, title="EMA Rápida")\nplot(mid_ma, color=color.orange, linewidth=1, title="EMA Intermedia")\nplot(slow_ma, color=color.red, linewidth=2, title="EMA Lenta (130 Periodos)")\n'

class SM5B86B43413961088(PinePortBase, IStrategy):
    source_id = "SM_5b86b43413961088"
    source_file = '趋势跟踪型三重指数移动平均线量化交易策略-Triple-EMA-Trend-Following-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fast_length': 10, 'mid_length': 30, 'slow_length': 130}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
