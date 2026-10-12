"""batch_011 port of 纯Stochastic多头交易策略Pure-Stochastic-Long-Only-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-11 00:00:00\nend: 2023-09-12 14:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version= 4\n// see for original idea:  http://www.enricomalverti.com/2016/12/stocastico/\n// https://sauciusfinance.altervista.org\nstrategy(title="Pure Stochastic long only", overlay = false, max_bars_back=500)\n\n// INPUTS & calculations\nlength = input(10, minval=1)\nOverBought = input(80, minval = 50, step = 10)\nOverSold = input(20, minval = 10, step = 5)\nsmoothK = input(7, minval=1)\nsmoothD = input(4, minval=1)\nk = sma(stoch(close, high, low, length), smoothK)\nd = sma(k, smoothD)\n// We keep EMA 7 (n period of stochastic /2) as target price\nemaperiodf = input(5, minval = 1)\nemaf = ema(close,emaperiodf)\nentryl = k > d and k <= OverSold and close >= high[1]\n/// Entry\nstrategy.entry("Long", true, when = entryl)\n\nmiddle = (OverBought+OverSold)/2\nclose1= crossunder(close,emaf)// **close under EMA fast**\nclose2= k < d and k > middle\nclose3 = (k >= OverBought)\n// exits.\nstrategy.close("Long", when = close1, comment="stop Ema Fast")\nstrategy.close("Long", when = close2, comment ="cross k&d")\nstrategy.close("Long", when = close3, comment = "high value of K")\n\n\nplot(k, color=#0000FF,  linewidth= 2, title="k Stoch")\nplot(d, color=#787B86, linewidth= 1, title="d stoch signal")\nplot(OverBought)\nplot(OverSold)'

class SM0D18E2BBBF9CE733(PinePortBase, IStrategy):
    source_id = "SM_0d18e2bbbf9ce733"
    source_file = '纯Stochastic多头交易策略Pure-Stochastic-Long-Only-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'length': 10, 'OverBought': 80, 'OverSold': 20, 'smoothK': 7, 'smoothD': 4, 'emaperiodf': 5}
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
