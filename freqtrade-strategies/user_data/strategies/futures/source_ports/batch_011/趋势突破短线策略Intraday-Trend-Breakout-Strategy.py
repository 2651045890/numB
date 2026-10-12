"""batch_011 port of 趋势突破短线策略Intraday-Trend-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Pritesh-StocksDeveloper\n\n//@version=4\nstrategy("Supertrend - Intraday", overlay=true, calc_on_every_tick = true)\n\n// ********** Strategy inputs - Start **********\n\n// Used for intraday handling\n// Session value should be from market start to the time you want to square-off \n// your intraday strategy\n// Important: The end time should be at least 2 minutes before the intraday\n// square-off time set by your broker\nvar i_marketSession = input(title="Market session", type=input.session, \n     defval="0915-1455", confirm=true)\n\nvar float i_multiplier = input(title = "Multiplier", type = input.float, \n     defval = 4, confirm=true)\n\nvar int i_atrPeriod = input(title = "ATR Period", type = input.integer, \n     defval = 14, confirm=true)\n\n// ********** Strategy inputs - End **********\n\n\n// ********** Supporting functions - Start **********\n\n// A function to check whether the bar or period is in intraday session\nbarInSession(sess) => time(timeframe.period, sess) != 0\n\n// ********** Supporting functions - End **********\n\n\n// ********** Strategy - Start **********\n\n[superTrend, dir] = supertrend(i_multiplier, i_atrPeriod)\n\ncolResistance = dir == 1 and dir == dir[1] ? color.new(color.red, 0) : color.new(color.red, 100)\ncolSupport = dir == -1 and dir == dir[1] ? color.new(color.green, 0) : color.new(color.green, 100)\n\nplot(superTrend, color = colResistance, linewidth=2)\nplot(superTrend, color = colSupport, linewidth=2)\n\n// Long/short condition\nlongCondition = close > superTrend\nshortCondition = close < superTrend\n\n// See if intraday session is active\nbool intradaySession = barInSession(i_marketSession)\n\n// Trade only if intraday session is active\n \n// Long position\n// When longCondition and intradaySession both are true\nstrategy.entry(id = "Long", long = strategy.long, \n     when = longCondition and intradaySession)\n \n// Short position\n// When shortCondition and intradaySession both are true\nstrategy.entry(id = "Short", long = strategy.short, \n     when = shortCondition and intradaySession)\n \n// Square-off position (when session is over and position is open)\nsquareOff = (not intradaySession) and (strategy.position_size != 0)\nstrategy.close_all(when = squareOff, comment = "Square-off")\n\n// ********** Strategy - End **********'

class SMA1D4AA7A5FD54E51(PinePortBase, IStrategy):
    source_id = "SM_a1d4aa7a5fd54e51"
    source_file = '趋势突破短线策略Intraday-Trend-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'i_marketSession': '0915-1455', 'i_multiplier': 4, 'i_atrPeriod': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'tuple', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
