"""batch_011 port of 趋势跟踪买入低点卖出高点策略Trend-Following-Buy-Dip-Sell-Peak-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-23 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Buy Dip Sell Rip Strategy", overlay=true)\nsource = close\nlength = input(15, minval=1)\nmult = input(1.25, minval=0.001, maxval=50)\nlongMAPeriod = input(300, minval=5)\nshortMAPeriod = input(20, minval=5)\n\nbasis = sma(source, length)\nlongMA = sma(source, longMAPeriod)\nprevLongMA = sma(close[1],longMAPeriod)\nshortMA = sma(source, shortMAPeriod)\ndev = mult * stdev(source, length)\n\nupper = basis + dev\nlower = basis - dev\n\nbuyEntry = crossover(source, lower)\nsellEntry = crossunder(source, upper)\n\nif (source > lower and source[1] < lower)\n    if (longMA < source  and shortMA>source)\n        strategy.entry("BBandLE", strategy.long, stop=lower, oca_name="BollingerBands",  comment="BBandLE")\n    else\n        strategy.close("BBandSE")\nelse\n    strategy.cancel(id="BBandLE")\n\nif (source > upper and source[1] < upper)\n    if (longMA > source  and shortMA < source)\n        strategy.entry("BBandSE", strategy.short, stop=upper, oca_name="BollingerBands",  comment="BBandSE")\n    else \n        strategy.close("BBandLE")\nelse\n    strategy.cancel(id="BBandSE")\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)\n'

class SM1655F57DC77FE0AF(PinePortBase, IStrategy):
    source_id = "SM_1655f57dc77fe0af"
    source_file = '趋势跟踪买入低点卖出高点策略Trend-Following-Buy-Dip-Sell-Peak-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'length': 15, 'mult': 1.25, 'longMAPeriod': 300, 'shortMAPeriod': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
