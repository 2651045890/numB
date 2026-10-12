"""batch_011 port of 跟踪止损反转策略Trailing-Stop-Loss-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-24 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="Trailing SL Strategy [QuantNomad]", shorttitle = "TrailingSL [QN]", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 50)\n\n////////////\n// Inputs //\n\nsl_type    = input("%", options = ["%", "ATR", "Absolute"])\n\nsl_perc    = input(4,     title = "% SL",        type = input.float)\natr_length = input(10,    title = "ATR Length")\natr_mult   = input(2,     title = "ATR Mult",    type = input.float)\nsl_absol   = input(10,    title = "Absolute SL", type = input.float)\n\n// BACKTESTING RANGE\n// From Date Inputs\nfromDay   = input(defval = 1,    title = "From Day",   minval = 1, maxval = 31)\nfromMonth = input(defval = 1,    title = "From Month", minval = 1, maxval = 12)\nfromYear  = input(defval = 2016, title = "From Year",  minval = 1970)\n \n// To Date Inputs\ntoDay   = input(defval = 1,    title = "To Day",   minval = 1, maxval = 31)\ntoMonth = input(defval = 1,    title = "To Month", minval = 1, maxval = 12)\ntoYear  = input(defval = 2100, title = "To Year",  minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate  = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear,   toMonth,   toDay,   00, 00)\n\ntime_cond = time >= startDate and time <= finishDate\n\n//////////////////\n// CALCULATIONS //\n\n// SL values\nsl_val = sl_type == "ATR"      ? atr_mult * atr(atr_length) : \n         sl_type == "Absolute" ? sl_absol : \n         close * sl_perc / 100\n         \n// Init Variables\npos         = 0\ntrailing_sl = 0.0\n\n// Signals\nlong_signal  = nz(pos[1]) !=  1 and high > nz(trailing_sl[1])\nshort_signal = nz(pos[1]) != -1 and low  < nz(trailing_sl[1]) \n\n// Calculate SL\ntrailing_sl := short_signal     ? high + sl_val : \n               long_signal      ? low  - sl_val : \n               nz(pos[1]) ==  1 ? max(low  - sl_val, nz(trailing_sl[1])) :  \n               nz(pos[1]) == -1 ? min(high + sl_val, nz(trailing_sl[1])) : \n               nz(trailing_sl[1])\n               \n// Position var               \npos := long_signal  ? 1 : short_signal ? -1 : nz(pos[1]) \n\n//////////////\n// PLOTINGS //\n\nplot(trailing_sl, linewidth = 2, color = pos == 1 ? color.green : color.red)\n\n//////////////\n// STRATEGY //\n\nif (time_cond and pos != 1)\n    strategy.entry("long",  true, stop = trailing_sl)\n  \nif (time_cond and pos != -1) \n    strategy.entry("short", false, stop = trailing_sl)'

class SM4EAB1ED92EDB844C(PinePortBase, IStrategy):
    source_id = "SM_4eab1ed92edb844c"
    source_file = '跟踪止损反转策略Trailing-Stop-Loss-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'sl_type': '%', 'sl_perc': 4, 'atr_length': 10, 'atr_mult': 2, 'sl_absol': 10, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2016, 'toDay': 1, 'toMonth': 1, 'toYear': 2100}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 50
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
