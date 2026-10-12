"""batch_011 port of 超级趋势追踪策略SuperTrend-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-24 00:00:00\nend: 2023-09-23 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("QuantNomad - SuperTrend - TSLA - 1m", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n// INPUTS //\nst_mult   = input(3,   title = \'SuperTrend Multiplier\', minval = 0, maxval = 100, step = 0.01)\nst_period = input(120, title = \'SuperTrend Period\',     minval = 1)\n\n// CALCULATIONS //\nup_lev = hl2 - (st_mult * atr(st_period))\ndn_lev = hl2 + (st_mult * atr(st_period))\n\nup_trend   = 0.0\nup_trend   := close[1] > up_trend[1]   ? max(up_lev, up_trend[1])   : up_lev\n\ndown_trend = 0.0\ndown_trend := close[1] < down_trend[1] ? min(dn_lev, down_trend[1]) : dn_lev\n\n// Calculate trend var\ntrend = 0\ntrend := close > down_trend[1] ? 1: close < up_trend[1] ? -1 : nz(trend[1], 1)\n\n// Calculate SuperTrend Line\nst_line = trend ==1 ? up_trend : down_trend\n\n// Plotting\nplot(st_line, color = trend == 1 ? color.green : color.red , style = plot.style_line, linewidth = 2, title = "SuperTrend")\n\nplotshape(crossover( close, st_line), location = location.belowbar, color = color.green)\nplotshape(crossunder(close, st_line), location = location.abovebar, color = color.red)\n\n// Strategy with "when"\n//strategy.entry("long",  true,  when = crossover( close, down_trend[1]))\n//strategy.entry("short", false, when = crossunder(close, up_trend[1]))\n\n// Strategy with stop orders\nstrategy.entry("long",  true,  stop = down_trend[1])\nstrategy.entry("short", false, stop = up_trend[1])'

class SM0D731758B7ECE647(PinePortBase, IStrategy):
    source_id = "SM_0d731758b7ece647"
    source_file = '超级趋势追踪策略SuperTrend-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'st_mult': 3, 'st_period': 120}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
