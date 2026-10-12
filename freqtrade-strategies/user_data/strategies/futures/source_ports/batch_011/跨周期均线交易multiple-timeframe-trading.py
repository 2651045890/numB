"""batch_011 port of 跨周期均线交易multiple-timeframe-trading.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2021-05-04 00:00:00\nend: 2022-05-03 23:59:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Bitfinex","currency":"BTC_USD"}]\n*/\nstrategy("multiple timeframe trading")\n\nexpr = ta.ema(close, 5)\nhVal = request.security(syminfo.tickerid, \'60\', expr)\n\nplot(expr, timeframe.period)\nplot(hVal, \'1hour\')\n\n// 5 hour vs 5 days\nif hVal > expr\n    strategy.entry("long", strategy.long)\nelse\n    strategy.entry("short", strategy.short)\n'

class SM728AB37423E60BCF(PinePortBase, IStrategy):
    source_id = "SM_728ab37423e60bcf"
    source_file = '跨周期均线交易multiple-timeframe-trading.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
