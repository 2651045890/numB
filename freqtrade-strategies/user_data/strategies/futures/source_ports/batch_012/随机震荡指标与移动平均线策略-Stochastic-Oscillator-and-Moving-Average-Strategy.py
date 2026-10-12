"""batch_012 port of 随机震荡指标与移动平均线策略-Stochastic-Oscillator-and-Moving-Average-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-22 00:00:00\nend: 2024-04-29 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Pablo_2uc\n\n//@version=5\nstrategy("Estrategia Stoch + MA c/ SL", overlay=true)\n\n// Parámetros del Estocástico\nlength = input.int(14, title="Longitud Estocástico")\nsmoothK = input.int(3, title="Suavizado K")\nsmoothD = input.int(3, title="Suavizado D")\noversold = input.int(20, title="Sobreventa")\noverbought = input.int(80, title="Sobrecompra")\n\n// Parámetros de la Media Móvil\nmaLength = input.int(9, title="Longitud MA")\nmaSource = input(close, title="Fuente MA")\n\n// Capital inicial\ncapital = 500\n\n// Tamaño de posición (10% del capital)\npositionSize = 1\n\n// Stop Loss (2% del precio de entrada)\nstopLossPercent = input.int(2, title="Stop Loss (%)") / 100\n\n// Cálculo del Estocástico\nk = ta.sma(ta.stoch(close, high, low, length), smoothK)\nd = ta.sma(k, smoothD)\n\n// Cálculo de la Media Móvil\nma = ta.sma(maSource, maLength)\n\n// Condiciones de entrada en largo y corto\nlongCondition = ta.crossunder(k, oversold) and ma > ma[1]\nshortCondition = ta.crossover(k, overbought) and ma < ma[1]\n\n// Condiciones de salida\nexitLongCondition = ta.crossover(k, ma) and ma < ma[1]\nexitShortCondition = ta.crossunder(k, ma) and ma > ma[1]\n\n// Estrategia\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=positionSize)\n    strategy.exit("Exit Long", "Long", stop=close * (1 - stopLossPercent))\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=positionSize)\n    strategy.exit("Exit Short", "Short", stop=close * (1 + stopLossPercent))\n\n// Cierre de posiciones\nif (exitLongCondition)\n    strategy.close("Long")\nif (exitShortCondition)\n    strategy.close("Short")\n'

class SMStochasticOscillatorandMovingAverageStrategybc259b(PinePortBase, IStrategy):
    source_id = "SM_bc259b3f7a3836ef"
    source_file = '随机震荡指标与移动平均线策略-Stochastic-Oscillator-and-Moving-Average-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'length': 14, 'smoothK': 3, 'smoothD': 3, 'oversold': 20, 'overbought': 80, 'maLength': 9, 'maSource': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
