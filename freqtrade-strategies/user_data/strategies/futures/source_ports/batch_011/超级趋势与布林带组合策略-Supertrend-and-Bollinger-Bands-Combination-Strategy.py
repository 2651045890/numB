"""batch_011 port of 超级趋势与布林带组合策略-Supertrend-and-Bollinger-Bands-Combination-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-21 00:00:00\nend: 2024-03-28 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © sabhiv27\n\n//@version=4\nstrategy("Supertrend & Bollinger Bands Strategy", shorttitle="ST_BB_Strategy", overlay=true)\n\n// Input options\nfactor = input(3, title="Supertrend Factor")\nlength = input(10, title="ATR Length")\nbollinger_length = input(20, title="Bollinger Bands Length")\nbollinger_deviation = input(2, title="Bollinger Bands Deviation")\n\n// Calculate True Range for Supertrend\ntruerange = rma(tr, length)\n\n// Calculate Supertrend\nvar float up_trend = na\nvar float dn_trend = na\nvar float trend = na\nup_signal = hl2 - (factor * truerange)\ndn_signal = hl2 + (factor * truerange)\nup_trend := close[1] > up_trend[1] ? max(up_signal, up_trend[1]) : up_signal\ndn_trend := close[1] < dn_trend[1] ? min(dn_signal, dn_trend[1]) : dn_signal\ntrend := close > dn_trend ? 1 : close < up_trend ? -1 : nz(trend[1], 1)\n\n// Calculate Bollinger Bands\nbasis = sma(close, bollinger_length)\ndev = stdev(close, bollinger_length)\nupper_band = basis + bollinger_deviation * dev\nlower_band = basis - bollinger_deviation * dev\n\n// Entry conditions\nlong_condition = crossover(close, up_trend) and close < lower_band\nshort_condition = crossunder(close, dn_trend) and close > upper_band\n\n// Exit conditions\nexit_long_condition = crossover(close, dn_trend)\nexit_short_condition = crossunder(close, up_trend)\n\n// Plot Supertrend\nplot(trend == 1 ? up_trend : dn_trend, color=trend == 1 ? color.green : color.red, linewidth=2)\n\n// Plot Bollinger Bands\nplot(upper_band, color=color.blue)\nplot(lower_band, color=color.blue)\n\n// Generate buy and sell signals\nstrategy.entry("Long", strategy.long, when=long_condition)\nstrategy.entry("Short", strategy.short, when=short_condition)\nstrategy.close("Long", when=exit_long_condition)\nstrategy.close("Short", when=exit_short_condition)'

class SM299FD7A10A254824(PinePortBase, IStrategy):
    source_id = "SM_299fd7a10a254824"
    source_file = '超级趋势与布林带组合策略-Supertrend-and-Bollinger-Bands-Combination-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'factor': 3, 'length': 10, 'bollinger_length': 20, 'bollinger_deviation': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
