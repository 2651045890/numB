"""batch_012 port of 防跳空开仓策略Gap-Opening-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-21 00:00:00\nend: 2024-02-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estrategia de Diferencia HL y MA para Criptomonedas", shorttitle="HL MA Crypto Strategy-Ortiz", overlay=true)\n\n// Definir longitud de MA y HL\nma_length = input(20, title="Longitud MA")\nhl_length = input(3, title="Longitud HL")\nexit_below_price = input(0.98, title="Salir por debajo de precio")\n\n// Calcular MA\nma = ta.sma(close, ma_length)\n\n// Calcular HL\nhh = ta.highest(high, hl_length)\nll = ta.lowest(low, hl_length)\nhl = hh - ll\n\n// Condiciones de tendencia alcista\nbullish_trend = close > ma\n\n// Condiciones de entrada y salida\nlong_condition = close > ma and close > ma[1] and hl > ta.sma(hl, ma_length)\nshort_condition = false // No operar en tendencia bajista\nexit_condition = low < close * exit_below_price\n\n// Entrada y salida de la estrategia\nif (long_condition)\n    strategy.entry("Buy", strategy.long)\nif (short_condition)\n    strategy.entry("Sell", strategy.short)\nif (exit_condition)\n    strategy.close("Buy")\n\n// Plot de señales en el gráfico\nplotshape(long_condition, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title="Buy Signal")\nplotshape(short_condition, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title="Sell Signal")\n\n'

class SMGapOpeningStrategybc4f04(PinePortBase, IStrategy):
    source_id = "SM_bc4f043f8e927441"
    source_file = '防跳空开仓策略Gap-Opening-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'ma_length': 20, 'hl_length': 3, 'exit_below_price': 0.98}
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
