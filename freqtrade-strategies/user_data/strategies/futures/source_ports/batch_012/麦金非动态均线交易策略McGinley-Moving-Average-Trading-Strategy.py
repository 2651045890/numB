"""batch_012 port of 麦金非动态均线交易策略McGinley-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-07 00:00:00\nend: 2023-11-13 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © LucasZancheta\n\n//@version=4\nstrategy(shorttitle="Maguila", title="McGinley Dynamic Indicator", overlay=true)\n\n//Médias móveis\nMA1Period=input(21, title="MA1")\nMA2Period=input(42, title="MA2")\n\nMA1 = ema(close, MA1Period)\nMA2 = ema(close, MA2Period)\n\naboveAverage = MA1 >= MA2\nhunderAverage = MA2 >= MA1\n\n//Período do backtest\nstartDate = input(title="Start Date", type=input.integer, defval=28, minval=1, maxval=31)\nstartMonth = input(title="Start Month", type=input.integer, defval=5, minval=1, maxval=12)\nstartYear = input(title="Start Year", type=input.integer, defval=2019, minval=1800, maxval=2100)\n\nendDate = input(title="End Date", type=input.integer, defval=28, minval=1, maxval=31)\nendMonth = input(title="End Month", type=input.integer, defval=5, minval=1, maxval=12)\nendYear = input(title="End Year", type=input.integer, defval=2030, minval=1800, maxval=2100)\n\n//Verifica se o candle está dentro do período do backtest\ninDateRange = (time >= timestamp(syminfo.timezone, startYear, startMonth, startDate, 0, 0)) and (time < timestamp(syminfo.timezone, endYear, endMonth, endDate, 0, 0))\n\n//Número de periodos da média móvel\nperiod  = input(title="Períodos", type=input.integer, defval=20)\n//Constante K (0.6)\nk = input(title="Constante K", type=input.float, defval=0.6)\n//Preço de fechamento \nclosePrice = input(title="Preço", type=input.source, defval=close)\n\nmdi = 0.0\n\n//Fórmula de McGinley\nmdi := na(mdi[1]) ? closePrice : mdi[1] + (closePrice - mdi[1]) / max((k * period * pow(closePrice / mdi[1], 4)), 1)\n\n//Regra de coloração \nmdiColor = closePrice > mdi ? color.green : closePrice < mdi ? color.red : color.black\n\n//Inserindo as informações no gráfico    \nplot(MA1, color=color.blue, linewidth=2)\nplot(MA2, color=color.purple, linewidth=2)\n\nbarcolor(mdiColor)\n\n//Estratégia\nbuySignal = aboveAverage and closePrice > mdi and crossunder(low, MA1) and close > MA1  \nbuyLoss = closePrice < mdi and close < MA1 and close < MA2\n\nif (inDateRange)\n    strategy.entry("Compra", strategy.long, qty=1, when= buySignal)\n    strategy.exit("Gain da compra", "Compra", qty=1, profit=20)\n    strategy.close("Compra", qty=1, when= buyLoss, comment="Loss na operação")\n\nsellSignal = hunderAverage and closePrice < mdi and crossover(high, MA1) and close < MA1\nsellLoss = closePrice > mdi and close > MA1 and close > MA2\n\nif (inDateRange)\n    strategy.entry("Venda", strategy.short, qty=1, when= sellSignal)\n    strategy.exit("Gain da venda", "Venda", qty=1, profit=20)\n    strategy.close("Venda", qty=1, when= sellLoss, comment="Loss na operação")\n\nif (not inDateRange)\n    strategy.close_all()\n\n\n\n'

class SMMcGinleyMovingAverageTradingStrategy8a600f(PinePortBase, IStrategy):
    source_id = "SM_8a600fd11bdd7c8d"
    source_file = '麦金非动态均线交易策略McGinley-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'MA1Period': 21, 'MA2Period': 42, 'startDate': 28, 'startMonth': 5, 'startYear': 2019, 'endDate': 28, 'endMonth': 5, 'endYear': 2030, 'period': 20, 'k': 0.6, 'closePrice': 'close'}
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
