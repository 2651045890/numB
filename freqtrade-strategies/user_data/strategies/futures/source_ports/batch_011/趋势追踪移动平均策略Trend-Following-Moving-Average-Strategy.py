"""batch_011 port of 趋势追踪移动平均策略Trend-Following-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-30 00:00:00\nend: 2024-02-29 00:00:00\nperiod: 5h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Wallstwizard10\n\n//@version=4\nstrategy("Estrategia de Trading", overlay=true)\n\n// Definir las EMA y SMA\nema50 = ema(close, 50)\nsma100 = sma(close, 100)\n\n// Definir el RSI\nrsiLength = input(14, title="RSI Length")\noverbought = input(70, title="Overbought Level")\noversold = input(30, title="Oversold Level")\nrsi = rsi(close, rsiLength)\n\n// Condiciones de Compra\nbuyCondition = crossover(ema50, sma100) // EMA de 50 cruza SMA de 100 hacia arriba\n\n// Condiciones de Venta\nsellCondition = crossunder(ema50, sma100) // EMA de 50 cruza SMA de 100 hacia abajo\n\n// Salida de Operaciones\nexitBuyCondition = rsi >= overbought // RSI en niveles de sobrecompra\nexitSellCondition = rsi <= oversold // RSI en niveles de sobreventa\n\n// Lógica de Trading\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n    \nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n    \nif (exitBuyCondition)\n    strategy.close("Buy")\n    \nif (exitSellCondition)\n    strategy.close("Sell")'

class SM9AC5934CADC889EB(PinePortBase, IStrategy):
    source_id = "SM_9ac5934cadc889eb"
    source_file = '趋势追踪移动平均策略Trend-Following-Moving-Average-Strategy.md'
    timeframe = '5h'
    can_short = True
    source_defaults = {'rsiLength': 14, 'overbought': 70, 'oversold': 30}
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
