"""batch_011 port of 移动平均线与RSI综合交易策略-Moving-Average-and-RSI-Comprehensive-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-04-24 00:00:00\nend: 2024-04-29 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estratégia de Médias Móveis e RSI (por Svitorino_trade)", shorttitle="Estratégia-Médias Móveis", overlay=true)\n\nlen1 = input.int(9, minval=1, title="Length 1")\nlen2 = input.int(21, minval=1, title="Length 2")\nlen3 = input.int(25, minval=1, title="Length 3")\nlen4 = input.int(99, minval=1, title="Length 4")\nrsi_length = input.int(14, minval=1, title="RSI Length")\nrsi_oversold = input.float(30, minval=0, maxval=100, title="RSI Oversold Level")\nrsi_overbought = input.float(70, minval=0, maxval=100, title="RSI Overbought Level")\n\nsrc = input(close, title="Source")\n\nama(src, length) =>\n    sum = 0.0\n    for i = 0 to length - 1\n        sum := sum + src[i]\n    sum / length\n\navg1 = ama(src, len1)\navg2 = ama(src, len2)\navg3 = ama(src, len3)\navg4 = ama(src, len4)\n\nrsi_value = ta.rsi(src, rsi_length)\n\n// Condições de entrada e saída para períodos de 9 e 21\ncruzamento_9_21_acima = avg1 > avg2 and avg1[1] <= avg2[1]\ncruzamento_9_21_abaixo = avg1 < avg2 and avg1[1] >= avg2[1]\n\n// Condições de entrada e saída para períodos de 25 e 99\ncruzamento_25_99_acima = avg3 > avg4 and avg3[1] <= avg4[1]\ncruzamento_25_99_abaixo = avg3 < avg4 and avg3[1] >= avg4[1]\n\n// Plotando os sinais de entrada e saída\nplotshape(series=cruzamento_9_21_acima, style=shape.triangleup, color=color.green, size=size.small, location=location.belowbar)\nplotshape(series=cruzamento_9_21_abaixo, style=shape.triangledown, color=color.red, size=size.small, location=location.abovebar)\nplotshape(series=cruzamento_25_99_acima, style=shape.triangleup, color=color.green, size=size.small, location=location.belowbar)\nplotshape(series=cruzamento_25_99_abaixo, style=shape.triangledown, color=color.red, size=size.small, location=location.abovebar)\n\n// Entradas e saídas para períodos de 9 e 21\nif cruzamento_9_21_acima and rsi_value > rsi_overbought\n    strategy.entry("Venda Curta", strategy.short)\nif cruzamento_9_21_abaixo and rsi_value < rsi_oversold\n    strategy.entry("Compra Curta", strategy.long)\nif cruzamento_9_21_acima\n    strategy.close("Compra Curta")\nif cruzamento_9_21_abaixo\n    strategy.close("Venda Curta")\n\n// Entradas e saídas para períodos de 25 e 99\nif cruzamento_25_99_acima and rsi_value > rsi_overbought\n    strategy.entry("Compra Forte", strategy.long)\nif cruzamento_25_99_abaixo and rsi_value < rsi_oversold\n    strategy.entry("Venda Forte", strategy.short)\nif cruzamento_25_99_acima\n    strategy.close("Venda Forte")\nif cruzamento_25_99_abaixo\n    strategy.close("Compra Forte")\n'

class SM4C54C6DB364EE3FF(PinePortBase, IStrategy):
    source_id = "SM_4c54c6db364ee3ff"
    source_file = '移动平均线与RSI综合交易策略-Moving-Average-and-RSI-Comprehensive-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'len1': 9, 'len2': 21, 'len3': 25, 'len4': 99, 'rsi_length': 14, 'rsi_oversold': 30, 'rsi_overbought': 70}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
