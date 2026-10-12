"""batch_011 port of 超级均线与Upperband交叉策略-Super-Moving-Average-and-Upperband-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-05-11 00:00:00\nend: 2024-05-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estratégia de Cruzamento de Bandas", overlay=true)\n\n// Entradas\nfactor = input(0.001, title="Factor")\nlength = input(20, title="Length")\n\n// Cálculo da Upperband\nUpperband = high * (1 + 2 * ((((high - low) / ((high + low) / 2)) * 1000) * factor))\n\n// Condição de Compra\nbuy_condition = close > ta.ema(close, 3)\n\n// Variável para controlar se a compra foi feita\nvar bought = false\n\n// Sinal de compra\nbuy_signal = (close[1] <= ta.sma(Upperband, length)[1]) and (close > ta.sma(Upperband, length)) and buy_condition\n\n// Sinal de venda\nsell_signal = close < ta.ema(close, 3) and bought\n\n// Atualizar o status de compra\nif buy_signal\n    bought := true\n    strategy.entry("Compra", strategy.long)\nelse if sell_signal\n    bought := false\n    strategy.close("Compra")\n\n// Plotagem dos sinais de compra e venda no gráfico\nplotshape(series=buy_signal, title="Compra", color=color.green, style=shape.triangleup, location=location.belowbar)\nplotshape(series=sell_signal, title="Venda", color=color.red, style=shape.triangledown, location=location.abovebar)'

class SM52ADF414A115E15A(PinePortBase, IStrategy):
    source_id = "SM_52adf414a115e15a"
    source_file = '超级均线与Upperband交叉策略-Super-Moving-Average-and-Upperband-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'factor': 0.001, 'length': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
