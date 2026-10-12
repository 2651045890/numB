"""batch_011 port of 简单趋势跟随策略Simple-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-29 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Trend Following", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 10)\n\nmaxIdLossPcnt = input(1, "Max Intraday Loss(%)", type=float)\nentryLong = false\nentryShort = false\n\n// strategy.risk.max_intraday_loss(maxIdLossPcnt, strategy.percent_of_equity)\n\nif (close > highest(high[1], 20))\n    strategy.entry("Long fast", strategy.long)\n    entryLong = true\n    \n\nif (close < lowest(low[1], 20))\n    strategy.entry("Short fast", strategy.short)\n    entryShort = true\n    \nif (close > highest(high[1], 55))\n    strategy.entry("Long slow", strategy.long)\n    entryLong = true\n\nif (close < lowest(low[1], 55))\n    strategy.entry("Short slow", strategy.short)\n    entryShort = true\n\nlen1 = input(21, minval=1, title="21 SMA")\nsrc1 = input(close, title="21 SMA")\nout1 = sma(src1, len1)\nplot(out1, title="21 SMA", color= white)\n\nlen2 = input(50, minval=1, title="50 SMA")\nsrc2 = input(close, title="50 SMA")\nout2 = sma(src2, len2)\nplot(out2, title="50 SMA", color= blue)\n\nlen3 = input(100, minval=1, title="100 SMA")\nsrc3 = input(close, title="100 SMA")\nout3 = sma(src3, len3)\nplot(out3, title="100 SMA", color= orange)\n\nlen4 = input(200, minval=1, title="200 SMA")\nsrc4 = input(close, title="200 SMA")\nout4 = sma(src4, len4)\nplot(out4, title="200 SMA", color= green)\n\n'

class SM754EDCBE6A807464(PinePortBase, IStrategy):
    source_id = "SM_754edcbe6a807464"
    source_file = '简单趋势跟随策略Simple-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maxIdLossPcnt': 1, 'len1': 21, 'len2': 50, 'len3': 100, 'len4': 200}
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
