"""batch_011 port of 突破交易策略Volatility-Breakout-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-29 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n\n//@version=5\nstrategy("Volatility Breakout Strategy [Angel Algo]", overlay = true)\n\n// Inputs\nlength = input(title="Length", defval=20)\n\n// Calculate the average true range (ATR)\natr = ta.atr(length)\n\n// Plot the ATR on the chart\nplot(atr, color=color.blue, linewidth=2, title="ATR")\n\n// Calculate the upper and lower breakouts\nupper_breakout = high + atr\nlower_breakout = low - atr\n\n// Plot the upper and lower breakouts on the chart\nul = plot(upper_breakout[1], color = color.new(color.green, 100), linewidth=2, title="Upper Breakout Level")\nll = plot(lower_breakout[1], color = color.new(color.red, 100), linewidth=2, title="Lower Breakout Level")\n\n// Create the signals\nlong_entry = ta.crossover(close, upper_breakout[1]) and barstate.isconfirmed\nshort_entry = ta.crossunder(close, lower_breakout[1]) and barstate.isconfirmed\n\nactive_signal_color =ta.barssince(long_entry) < ta.barssince(short_entry) ? \n   color.new(color.green,85) : color.new(color.red,85)\n\n// Plot the signals on the chart\nplotshape(long_entry and ta.barssince(long_entry[1]) > ta.barssince(short_entry[1]), location=location.belowbar, style=shape.triangleup, \n   color=color.green, size=size.normal, text = "Bullish breakout", textcolor = color.green)\nplotshape(short_entry and ta.barssince(long_entry[1]) < ta.barssince(short_entry[1]), location=location.abovebar, style=shape.triangledown, \n   color=color.red, size=size.normal,text = "Bearish breakout",  textcolor = color.red)\n\n// Fill the space between the upper and lower levels with the color that indicates the latest signal direction\nfill(ul,ll, color=active_signal_color)   \n\nlong_condition = long_entry and strategy.position_size <= 0 and barstate.isconfirmed\nshort_condition = short_entry and strategy.position_size >= 0 and barstate.isconfirmed\n\nif long_condition\n    strategy.entry("Volatility Breakout Long", strategy.long)\n\n\nif short_condition\n    strategy.entry("Volatility Breakout Short", strategy.short)\n'

class SMFAE31218AD70C28F(PinePortBase, IStrategy):
    source_id = "SM_fae31218ad70c28f"
    source_file = '突破交易策略Volatility-Breakout-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
