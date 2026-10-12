"""batch_011 port of 艾略特波浪理论4-9脉冲波自动检测交易策略-Elliott-Wave-Theory-4-9-Impulse-Wave-Automatic-Detection-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-04-20 00:00:00\nend: 2024-04-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Smollet\n\n//@version=5\nstrategy("LW: 4-9 indicator", overlay = true)\n\nconsclos = input.int(3, "Consecutive close")\ndaysago = input.int(9, "Days ago")\n\n\nvar int long_cc = 0\nvar int short_cc = 0\n\nlong_cc := 1\nshort_cc := 1\n\nfor i = 1 to consclos\n    long_cc := close[i-1] > close[i] ? long_cc*1 : long_cc*0\n    short_cc := close[i-1] < close[i] ? short_cc*1 : short_cc*0\n\nlong_daysago = close > close[daysago]\nshort_daysago = close < close[daysago]\n\n\n\nlong = long_cc ==1 and long_daysago\nshort = short_cc ==1 and short_daysago\n\n\nplotshape(long, style=shape.triangleup, location=location.belowbar, color=color.green)\nplotshape(short, style=shape.triangledown, location=location.abovebar, color=color.red)\n\n\n\n//Strategy code\nif long and strategy.position_size <= 0\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long SL", "Long", stop = low)\n\nif short and strategy.position_size >= 0\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short SL", "Short", stop = high)\n'

class SM85CAACFF5881BD9B(PinePortBase, IStrategy):
    source_id = "SM_85caacff5881bd9b"
    source_file = '艾略特波浪理论4-9脉冲波自动检测交易策略-Elliott-Wave-Theory-4-9-Impulse-Wave-Automatic-Detection-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'consclos': 3, 'daysago': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['loop', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
