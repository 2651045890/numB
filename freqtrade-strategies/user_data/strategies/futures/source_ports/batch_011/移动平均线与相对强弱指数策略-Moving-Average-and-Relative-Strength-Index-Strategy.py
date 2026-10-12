"""batch_011 port of 移动平均线与相对强弱指数策略-Moving-Average-and-Relative-Strength-Index-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-05-05 00:00:00\nend: 2024-05-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © giancarlo_meneguetti\n\n//@version=5\nstrategy("GM.MA.RSI.Stra", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Configurações para Médias Móveis\nema_short_length = input(9, title="EMA.9")\nema_long_length = input(21, title="EMA.21")\n\nema_short = ta.ema(close, ema_short_length)\nema_long = ta.ema(close, ema_long_length)\n\n// Configurações para RSI\nrsi_length = input(14, title="RSI.14")\nrsi_upper_threshold = input(70, title="RSI>70")\nrsi_lower_threshold = input(30, title="RSI<30")\n\nrsi = ta.rsi(close, rsi_length)\n\n// Sinais de Compra e Venda\n// Sinal de Compra quando a EMA curta cruza acima da EMA longa e o RSI está acima do limite inferior\nbuy_signal = ta.crossover(ema_short, ema_long) and rsi > rsi_lower_threshold\n\n// Sinal de Venda quando a EMA curta cruza abaixo da EMA longa ou o RSI está acima do limite superior\nsell_signal = ta.crossunder(ema_short, ema_long) or rsi > rsi_upper_threshold\n\n// Geração de Alertas\nalertcondition(buy_signal, title="Sinal de Compra", message="A EMA curta cruzou acima da EMA longa e o RSI está acima do limite inferior. Considere comprar.")\nalertcondition(sell_signal, title="Sinal de Venda", message="A EMA curta cruzou abaixo da EMA longa ou o RSI está acima do limite superior. Considere vender.")\n\n// Execução da Estratégia\nif buy_signal\n    strategy.entry("Compra", strategy.long)\n\nif sell_signal\n    strategy.close("Venda")\n'

class SM14AECD55FD19EC76(PinePortBase, IStrategy):
    source_id = "SM_14aecd55fd19ec76"
    source_file = '移动平均线与相对强弱指数策略-Moving-Average-and-Relative-Strength-Index-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'ema_short_length': 9, 'ema_long_length': 21, 'rsi_length': 14, 'rsi_upper_threshold': 70, 'rsi_lower_threshold': 30}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
