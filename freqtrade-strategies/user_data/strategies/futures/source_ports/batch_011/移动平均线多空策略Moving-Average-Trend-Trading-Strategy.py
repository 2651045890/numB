"""batch_011 port of 移动平均线多空策略Moving-Average-Trend-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-02 00:00:00\nend: 2023-10-08 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2019\n\n//@version=4\nstrategy(title = "Noro\'s ShiftMA-multi Strategy v1.0", shorttitle = "ShiftMA-multi", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 3)\n\n//Settings\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot")\nlen = input(3, minval = 1, title = "MA Lenghs")\nsrc = input(ohlc4, title = "MA Source")\nlonglevel1 = input(-4.0, title = "Long line 1")\nlonglevel2 = input(-5.0, title = "Long line 2")\nlonglevel3 = input(-6.0, title = "Long line 3")\nneedoffset = input(true, title = "Offset")\n\n//Variables\nsize = strategy.position_size\nmult = 1 / syminfo.mintick\n\n//MA\nma = sma(src, len)\nlongline1 = round(ma * ((100 + longlevel1) / 100) * mult) / mult\nlongline2 = round(ma * ((100 + longlevel2) / 100) * mult) / mult\nlongline3 = round(ma * ((100 + longlevel3) / 100) * mult) / mult\n\n//Lines\noffset = needoffset ? 1 : 0\nplot(ma, color = color.blue)\nplot(longline1, offset = offset, color = color.lime)\nplot(longline2, offset = offset, color = color.lime)\nplot(longline3, offset = offset, color = color.lime)\n\n//Trading\nlot = 0.0\nlot := size == 0 ? strategy.equity / close * capital / 100 : lot[1]\nlots = 0.0\nif ma > 0\n    lots := round(size / lot)\n    strategy.entry("L1", strategy.long, lot, limit = longline1, when = (lots == 0))\n    lots := round(size / lot)\n    strategy.entry("L2", strategy.long, lot, limit = longline2, when = (lots <= 1))\n    lots := round(size / lot)\n    strategy.entry("L3", strategy.long, lot, limit = longline3, when = (lots <= 2))\nif size > 0\n    strategy.entry("TP", strategy.short, 0, limit = ma)\n    '

class SM4D4575FE458B01DA(PinePortBase, IStrategy):
    source_id = "SM_4d4575fe458b01da"
    source_file = '移动平均线多空策略Moving-Average-Trend-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'capital': 100, 'len': 3, 'longlevel1': -4.0, 'longlevel2': -5.0, 'longlevel3': -6.0, 'needoffset': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 3
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
