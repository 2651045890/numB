"""batch_011 port of 经典双均线交叉策略Classic-Dual-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-26 00:00:00\nend: 2023-10-26 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n// strategy("Stochastic Strategy of BiznesFilosof", shorttitle="SS of BiznesFilosof", overlay=false, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=20, commission_type=strategy.commission.percent, commission_value=0.15, pyramiding=0)\n\n//Period\nstartY = input(title="Start Year", defval = 2011)\nstartM = input(title="Start Month", defval = 1, minval = 1, maxval = 12)\nstartD = input(title="Start Day", defval = 1, minval = 1, maxval = 31)\nfinishY = input(title="Finish Year", defval = 2050)\nfinishM = input(title="Finish Month", defval = 12, minval = 1, maxval = 12)\nfinishD = input(title="Finish Day", defval = 31, minval = 1, maxval = 31)\n//finish = input(2019, 02, 28, 00, 00)\ntimestart = timestamp(startY, startM, startD, 00, 00)\ntimefinish = timestamp(finishY, finishM, finishD, 23, 59)\nwindow = true // Lenghth strategy\n\nlength1 = input(21, minval=1), smoothK1 = input(3, minval=1), smoothD1 = input(3, minval=1)\n//length2 = input(5, minval=1), smoothK2 = input(1, minval=1), smoothD2 = input(1, minval=1)\ninh0 = input(title="Bottom Line", defval = 14, minval=0), inh1 = input(title="Upper Line", defval = 86, minval=0)\n\nk1 = sma(stoch(close, high, low, length1), smoothK1)\nd1 = sma(k1, smoothD1)\nplot(k1, color=blue)\nplot(d1, color=red)\n//k2 = sma(stoch(close, high, low, length2), smoothK2)\n//d2 = sma(k2, smoothD2)\n//plot(k2, color=orange)\n\nh1 = hline(inh1)\nh0 = hline(inh0)\nfill(h0, h1, color = aqua, transp=90)\n\n//open\nstrategy.entry("LongEntryID", strategy.long, comment="LONG", when = crossover(k1, d1) and crossover(k1, inh0) and window)\nstrategy.entry("ShortEntryID", strategy.short, comment="SHORT", when = crossunder(k1, d1) and crossunder(k1, inh1) and window)\n\nif crossunder(k1, d1) and crossunder(k1, inh1) and strategy.position_size > 0\n    strategy.close_all()\nif crossover(k1, d1) and crossover(k1, inh0) and strategy.position_size < 0\n    strategy.close_all()\n  \n    \n'

class SMF278520C1E8C9FFC(PinePortBase, IStrategy):
    source_id = "SM_f278520c1e8c9ffc"
    source_file = '经典双均线交叉策略Classic-Dual-Moving-Average-Crossover-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'startY': 2011, 'startM': 1, 'startD': 1, 'finishY': 2050, 'finishM': 12, 'finishD': 31, 'length1': 21, 'inh0': 14}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20
    source_commission_percent = 0.15
    source_pyramiding = 0
    source_initial_capital = 10000
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
