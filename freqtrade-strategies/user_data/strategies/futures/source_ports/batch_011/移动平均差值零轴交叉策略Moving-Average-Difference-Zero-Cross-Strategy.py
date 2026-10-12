"""batch_011 port of 移动平均差值零轴交叉策略Moving-Average-Difference-Zero-Cross-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-19 00:00:00\nend: 2024-01-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title = "Estratégia diferença menor preço de 8")\n\n// Configuração da Média Móvel\nemaPeriod = 8\n\nema= ema(close, emaPeriod)\nema1= ema(close[1], emaPeriod)\nlowestEMA = lowest(ema, 8)\n\n// Calcula a diferença entre o preço e a média móvel\ndiff = close - ema\ndiff1 = close[1] - ema1\ndiffLow = ema - lowestEMA\n\n//Condições\ndiffZero = diff < 0\ndiffUnder = diff < diffLow\ndiffUm = diff > 0\nLow0 = diffLow == 0\n\n\n\n\n// Sinais de entrada\nbuy_signal = diffUnder and crossover(diff, diff1) \nsell_signal = diffUm and diffUnder and crossunder(diff, diff1)\n\n// Executa as operações de compra/venda\nif buy_signal\n    strategy.entry("Buy", strategy.long)\nif sell_signal\n    strategy.exit("Buy")\n\n// Plota as linhas\nplot(0, title="Linha Zero", color=color.gray)\nplot(diff, title="Diferença", color=color.blue, linewidth=2)\n\nplot(diffLow, title="Diferença", color=color.red, linewidth=2)\n'

class SMC8C2FE97CBC861AE(PinePortBase, IStrategy):
    source_id = "SM_c8c2fe97cbc861ae"
    source_file = '移动平均差值零轴交叉策略Moving-Average-Difference-Zero-Cross-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
