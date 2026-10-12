"""batch_011 port of 超短期动量突破交易策略SSL-Channel-Breakout-Strategy-with-Trailing-Stop-Loss.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-24 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("SSL Channel Cross with Trailing Stop and Stop Loss", overlay=true)\n\nperiod = input(title="Period", defval=10)\nlen = input(title="Length", defval=10)\nsmaHigh = sma(high, len)\nsmaLow = sma(low, len)\n\nHlv = 0\nHlv := close > smaHigh ? 1 : close < smaLow ? -1 : Hlv[1]\n\nsslDown = Hlv < 0 ? smaHigh : smaLow\nsslUp = Hlv < 0 ? smaLow : smaHigh\n\nplot(sslDown, linewidth=2, color=color.red)\nplot(sslUp, linewidth=2, color=color.lime)\n\nlongCondition = crossover(sslUp, sslDown)\nshortCondition = crossunder(sslUp, sslDown)\n\n// Define el tamaño del trailing stop en puntos (ajusta según tu preferencia)\ntrailingStopSize = input(title="Trailing Stop Size (in Points)", defval=10)\n\nvar float trailingStopPrice = na\nvar float stopLossPrice = na\n\nif (longCondition)\n    // Si se cumple la condición de compra, configura la posición larga, el trailing stop y el stop loss\n    strategy.entry("Long", strategy.long)\n    trailingStopPrice := low - trailingStopSize\n    stopLossPrice := sslDown\n\nif (shortCondition)\n    // Si se cumple la condición de venta corta, configura la posición corta, el trailing stop y el stop loss\n    strategy.entry("Short", strategy.short)\n    trailingStopPrice := high + trailingStopSize\n    stopLossPrice := sslUp\n\n// Calcula el trailing stop\nif (strategy.position_size > 0)\n    trailingStopPrice := max(trailingStopPrice, stopLossPrice)\n    if (close < trailingStopPrice)\n        strategy.close("ExitLong", comment="Trailing Stop Long")\n\nif (strategy.position_size < 0)\n    trailingStopPrice := min(trailingStopPrice, stopLossPrice)\n    if (close > trailingStopPrice)\n        strategy.close("ExitShort", comment="Trailing Stop Short")\n'

class SM175F09F203A48C3D(PinePortBase, IStrategy):
    source_id = "SM_175f09f203a48c3d"
    source_file = '超短期动量突破交易策略SSL-Channel-Breakout-Strategy-with-Trailing-Stop-Loss.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'period': 10, 'len': 10, 'trailingStopSize': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
