"""batch_011 port of 趋势跟踪EMA和RSI策略Trend-Following-EMA-and-RSI-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-26 00:00:00\nend: 2023-09-25 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n//@author Alorse\n\n//@version=5\n// strategy(title=\'Tendency EMA + RSI [Alorse]\', shorttitle=\'Tendece EMA + RSI [Alorse]\', overlay=true, pyramiding=0, currency=currency.USD, default_qty_type=strategy.percent_of_equity, initial_capital=1000, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.01)\n\n// Bollinger Bands\nlen = input.int(14, minval=1, title=\'Length\', group=\'RSI\')\nsrc = input.source(close, \'Source\', group=\'RSI\')\nrsi = ta.rsi(src, len)\n\n// Moving Averages\nlen_a = input.int(10, minval=1, title=\'EMA A\u2004Length\', group=\'Moving Averages\')\nout_a = ta.ema(close, len_a)\nplot(out_a, title=\'EMA A\', color=color.purple)\n\nlen_b = input.int(20, minval=1, title=\'EMA B\u2004Length\', group=\'Moving Averages\')\nout_b = ta.ema(close, len_b)\nplot(out_b, title=\'EMA B\', color=color.orange)\n\nlen_c = input.int(100, minval=1, title=\'EMA C\u2004Length\', group=\'Moving Averages\')\nout_c = ta.ema(close, len_c)\nplot(out_c, title=\'EMA B\', color=color.green)\n\n// Strategy Conditions\nstratGroup = \'Strategy\'\nshowLong = input.bool(true, title=\'Long entries\', group=stratGroup)\nshowShort = input.bool(false, title=\'Short entries\', group=stratGroup)\ncloseAfterXBars = input.bool(true, title=\'Close after X # bars\', tooltip=\'If trade is in profit\', group=stratGroup)\nxBars = input.int(24, title=\'# bars\')\n\nentryLong = ta.crossover(out_a, out_b) and out_a > out_c and close > open\nexitLong = rsi > 70\n\nentryShort = ta.crossunder(out_a, out_b) and out_a < out_c and close < open\nexitShort = rsi < 30\n\n\nbought = strategy.opentrades[0] == 1 and strategy.position_size[0] > strategy.position_size[1]\nentry_price = ta.valuewhen(bought, open, 0)\nvar int nPastBars = 0\nif strategy.position_size > 0\n    nPastBars := nPastBars + 1\n    nPastBars\nif strategy.position_size == 0\n    nPastBars := 0\n    nPastBars\nif closeAfterXBars\n    exitLong := nPastBars >= xBars and close > entry_price ? true : exitLong\n    exitLong\n    exitShort := nPastBars >= xBars and close < entry_price ? true : exitShort\n    exitShort\n\n// Long Entry\nstrategy.entry(\'Long\', strategy.long, when=entryLong and showLong)\nstrategy.close(\'Long\', when=exitLong)\n\n// Short Entry\nstrategy.entry(\'Short\', strategy.short, when=entryShort and showShort)\nstrategy.close(\'Short\', when=exitShort)\n\n'

class SM3C59C945DEF9C1E2(PinePortBase, IStrategy):
    source_id = "SM_3c59c945def9c1e2"
    source_file = '趋势跟踪EMA和RSI策略Trend-Following-EMA-and-RSI-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'len': 14, 'len_a': 10, 'len_b': 20, 'len_c': 100, 'showLong': True, 'showShort': False, 'closeAfterXBars': True, 'xBars': 24}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
