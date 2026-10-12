"""batch_011 port of 趋势追踪型EMA突破策略Trend-Tracking-EMA-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-11 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © the_daily_trader\n\n//@version=5\n// ---------------------        Start of Code        ---------------------\nstrategy("Swing Trades Validator", overlay=true, margin_long=100, pyramiding = 0)\n\n// Indicator Display Checks\nTakeProfitPercent       = input.float(title="Profit Target %", defval=10, minval=1, step=0.05)\nStopLossPercent         = input.float(title="Stop Loss %", defval=10, minval=1, step=0.05)\npullbackchoice          = input.bool(false, "Relaxed Entry Rules")\n\n// EMAs\nemaH            = ta.ema(close, 8)\nemaHyest        = ta.ema(close[1], 8)\nemaHyest1       = ta.ema(close[2], 8)\nemaHyest2       = ta.ema(close[3], 8)\nemaL            = ta.ema(close, 21)\nemaLyest        = ta.ema(close[1], 21)\nemaLyest1       = ta.ema(close[2], 21)\nemaLyest2       = ta.ema(close[3], 21)\nemaf            = ta.ema(close, 50)\nemath           = ta.ema(close, 200)\nemathhigh       = ta.ema(high, 200)\nemathlow        = ta.ema(low, 200)\nemaslowmonthly  = request.security(syminfo.tickerid, "M", emaL) // Monthly 21ema\nemafastmonthly  = request.security(syminfo.tickerid, "M", emaH) // Monthly 8ema\nemaslowweekly   = request.security(syminfo.tickerid, "W", emaL) // Weekly 21ema\nemafastweekly   = request.security(syminfo.tickerid, "W", emaH) // Weekly 8ema\nemaslowdaily    = request.security(syminfo.tickerid, "D", emaL) // Daily 21ema\nemafastdaily    = request.security(syminfo.tickerid, "D", emaH) // Daily 8ema\nemafdaily       = request.security(syminfo.tickerid, "D", emaf) // Daily 50ema\nemathdaily      = request.security(syminfo.tickerid, "D", emath) // Daily ema\nemathdailyhigh  = request.security(syminfo.tickerid, "D", emathhigh) // Daily ema High\nemathdailylow   = request.security(syminfo.tickerid, "D", emathlow) // Daily ema Low\nema21yest       = request.security(syminfo.tickerid, "D", emaLyest) // Daily 21ema 1 day ago\nema21yest1      = request.security(syminfo.tickerid, "D", emaLyest1) // Daily 21ema 2 days ago\nema21yest2      = request.security(syminfo.tickerid, "D", emaLyest2) // Daily 21ema 3 days ago\nema8yest        = request.security(syminfo.tickerid, "D", emaHyest) // Daily 8ema 1 day ago\nema8yest1       = request.security(syminfo.tickerid, "D", emaHyest1) // Daily 8ema 2 days ago\nema8yest2       = request.security(syminfo.tickerid, "D", emaHyest2) // Daily 8ema 3 days ago\n\n\n// Prices\nmonthopen       = request.security(syminfo.tickerid, \'M\', open, barmerge.gaps_off, barmerge.lookahead_on)\nmonthclose      = request.security(syminfo.tickerid, \'M\', close, barmerge.gaps_off, barmerge.lookahead_on)\nweekopen        = request.security(syminfo.tickerid, \'W\', open, barmerge.gaps_off, barmerge.lookahead_on)\nweekclose       = request.security(syminfo.tickerid, \'W\', close, barmerge.gaps_off, barmerge.lookahead_on)\ndayopen         = request.security(syminfo.tickerid, \'D\', open, barmerge.gaps_off, barmerge.lookahead_on)\ndayclose        = request.security(syminfo.tickerid, \'D\', close, barmerge.gaps_off, barmerge.lookahead_on)\nthreedayhigh    = request.security(syminfo.tickerid, \'D\', high[3], barmerge.gaps_off, barmerge.lookahead_on)\ntwodayhigh      = request.security(syminfo.tickerid, \'D\', high[2], barmerge.gaps_off, barmerge.lookahead_on)\nyesthigh        = request.security(syminfo.tickerid, \'D\', high[1], barmerge.gaps_off, barmerge.lookahead_on)\nyestlow         = request.security(syminfo.tickerid, \'D\', low[1], barmerge.gaps_off, barmerge.lookahead_on)\n\n// Conditions \nmonthlybullish          = emafastmonthly > emaslowmonthly\nmonthlybullishprice     = close > emafastmonthly\nmonthlybullishcandle    = monthclose > monthopen\nweeklybullish           = emafastweekly > emaslowweekly\nweeklybullishprice      = close > emafastweekly\nweeklybullishcandle     = weekclose > weekopen\ndailybullish1           = emafdaily > emathdaily\ndailybullish2           = emafastdaily > emaslowdaily\ndailybullishprice       = close > emafastdaily\ndailybullishcandle      = dayclose > dayopen\nringlow                 = yestlow <= ema8yest\naggropullback           = twodayhigh < threedayhigh\npullback                = (pullbackchoice ? aggropullback : 0)\npullbackfailure         = dayclose > yesthigh and yesthigh < twodayhigh or pullback\nemasetup                = ema8yest > ema21yest and ema8yest1 > ema21yest1 and ema8yest2 > ema21yest2\n\n// Target Profit and Stop Loss Inputs\n// Input parameters can be found at the beginning of the code\nProfitTarget        = (close * (TakeProfitPercent / 100)) / syminfo.mintick\nStopLoss            = (close * (StopLossPercent / 100)) / syminfo.mintick\n\nlongCondition = monthlybullish and monthlybullishprice and weeklybullish and weeklybullishprice and dailybullish1 and dailybullish2 and dailybullishprice and monthlybullishcandle and weeklybullishcandle and dailybullishcandle and ringlow and pullbackfailure and emasetup\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit ("Exit", "Long", profit = ProfitTarget, loss = StopLoss)\n    // strategy.close("Long", qty_percent = 100)\n\n\n// -----------xxxxxxxxxxx-------------    End of Code     -----------xxxxxxxxxxx---------------'

class SM09AF0334F2B2F301(PinePortBase, IStrategy):
    source_id = "SM_09af0334f2b2f301"
    source_file = '趋势追踪型EMA突破策略Trend-Tracking-EMA-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'TakeProfitPercent': 10, 'StopLossPercent': 10, 'pullbackchoice': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
