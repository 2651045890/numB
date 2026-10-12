"""batch_011 port of 移动平均线交叉策略Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-13 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n// strategy("MavCrossover v2", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n// Revision:        1\n// Author:          @ToS_MavericK\n\n// === INPUT SMA ===\nfastMA  = input(defval = 13,  title = "FastMA", minval = 1, step = 1)\nslowMA  = input(defval = 144,  title = "SlowMA", minval = 1, step = 1)\nType    = input(defval = 1,  title = "Type (1 = SMA, 2 = EMA)", minval = 1, maxval = 2, step = 1)\nSlowMAIsFactor = input(false)\n\nslowMA := SlowMAIsFactor == true ? round(fastMA * slowMA) : slowMA\n\n// === INPUT BACKTEST RANGE ===\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromYear  = input(defval = 2018, title = "From Year", minval = 2012)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToYear    = input(defval = 2020, title = "To Year", minval = 2012)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nwindow()  => true // create function "within window of time"\n\n// === MA SETUP ===\nfast = Type == 1 ? sma(close, fastMA) : ema(close, fastMA)\nslow = Type == 1 ? sma(close, slowMA) : ema(close, slowMA)\n\n// === EXECUTION ===\nstrategy.entry("L", strategy.long, when = crossover(fast, slow) and window())   // buy long when "within window of time" AND crossover\nstrategy.close("L", when = crossunder(fast, slow) or time > finish)             // sell long when window ends OR crossunder         \n\nplot(fast, title = \'FastMA\', color = yellow, linewidth = 2, style = line)  // plot FastMA\nplot(slow, title = \'SlowMA\', color = aqua, linewidth = 2, style = line)    // plot SlowMA'

class SM159D0CBC98B6EC43(PinePortBase, IStrategy):
    source_id = "SM_159d0cbc98b6ec43"
    source_file = '移动平均线交叉策略Moving-Average-Crossover-Strategy.md'
    timeframe = '30m'
    can_short = False
    source_defaults = {'fastMA': 13, 'slowMA': 144, 'Type': 1, 'SlowMAIsFactor': False, 'FromDay': 1, 'FromMonth': 1, 'FromYear': 2018, 'ToDay': 1, 'ToMonth': 1, 'ToYear': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
