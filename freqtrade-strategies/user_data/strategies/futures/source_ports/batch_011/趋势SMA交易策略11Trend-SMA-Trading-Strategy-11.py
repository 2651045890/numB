"""batch_011 port of 趋势SMA交易策略11Trend-SMA-Trading-Strategy-11.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-22 00:00:00\nend: 2023-09-21 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Noro\'s Trend SMA Strategy v1.1", shorttitle = "Trend SMA str 1.1", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value=100.0, pyramiding=0)\n\nfastlen = input(5, "fast SMA Period")\nslowlen = input(15, "slow SMA Period")\nonly = input(false, "Only long?")\n\nfastsma = ema(close, fastlen)\nslowsma = ema(close, slowlen)\n\ntrend = low > slowsma ? 1 : high < slowsma ? -1 : trend[1]\n\nup = trend == 1 and low < fastsma and close < open ? 1 : 0\ndn = trend == -1 and high > fastsma and close > open ? 1 : 0\n\nplot(fastsma, color = red, title = "Fast SMA")\nplot(slowsma, color = blue, title = "Slow SMA")\n\nlongCondition = up == 1\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nshortCondition = dn == 1\nif (shortCondition)\n    strategy.entry("Short", strategy.short, only == true ? 0 : na)'

class SMB01792F1FB484082(PinePortBase, IStrategy):
    source_id = "SM_b01792f1fb484082"
    source_file = '趋势SMA交易策略11Trend-SMA-Trading-Strategy-11.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'fastlen': 5, 'slowlen': 15, 'only': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
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
