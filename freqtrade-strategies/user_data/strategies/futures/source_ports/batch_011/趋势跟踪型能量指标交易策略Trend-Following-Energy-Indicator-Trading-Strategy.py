"""batch_011 port of 趋势跟踪型能量指标交易策略Trend-Following-Energy-Indicator-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-15 00:00:00\nend: 2023-11-14 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Smeared VCI Backtest", overlay=false, shorttitle="SVCI Backtest", default_qty_type = strategy.percent_of_equity, default_qty_value = 100, initial_capital = 10000, slippage = 5)\n// Smeared Variability Channel Index\n//    a variation of the VCI indicator of the same author.\n// The orange line over the lime line is bullish;\n// The lime line over the orange one is bearish.\n//\n// vitelot/yanez/Vts\n// Feb 2019\n//\nsrc = close\n\nep1 = input(5, minval=1, title="Fast EMA period")\nep2 = input(13, minval=2, title="Slow EMA period")\n\nsm = input(34, minval=1, title="Smearing period")\ntp = input(13, minval=1, title="Trigger line period")\n\nfixedSL = input(title="SL Activation", defval=300)\ntrailSL = input(title="SL Trigger", defval=1)\nfixedTP = input(title="TP Activation", defval=150)\ntrailTP = input(title="TP Trigger", defval=1)\n\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2019, title = "From Year", minval = 2017)\nToMonth   = input(defval = 6, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 19, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 2030, title = "To Year", minval = 2017)\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nstartTimeOk()  => time >= start and time <= finish ? true : false // create function "within window of time" if statement true\n\natrP = 96\n\ne1 = ema(src,ep1)\ne2 = ema(src,ep2)\n\nvci = (e1-e2)/atr(atrP)\n\nsvci = sma(vci,sm)\nt = sma(svci,tp)\n\nplot(svci, color=lime, linewidth=3, transp=0, title="Smeared VCI")\nplot(t, color=orange, linewidth=3, transp=0, title="Trigger line")\n\nhline(0, title="Reference line")\n\nlong = crossover(svci,t)\nshort = crossover(t,svci)\n\n// === STRATEGY - LONG POSITION EXECUTION ===\nstrategy.entry("Long", strategy.long, when= long and startTimeOk())\nstrategy.exit("Exit", qty_percent = 100, loss=fixedSL, trail_offset=trailTP, trail_points=fixedTP) \nstrategy.exit("Exit", when= short)\n// === STRATEGY - SHORT POSITION EXECUTION ===\nstrategy.entry("Short", strategy.short, when= short and startTimeOk())\nstrategy.exit("Exit", qty_percent = 100, loss=fixedSL, trail_offset=trailTP, trail_points=fixedTP)\nstrategy.exit("Exit", when= long)'

class SM96292CF38A3DF5B4(PinePortBase, IStrategy):
    source_id = "SM_96292cf38a3df5b4"
    source_file = '趋势跟踪型能量指标交易策略Trend-Following-Energy-Indicator-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'ep1': 5, 'ep2': 13, 'sm': 34, 'tp': 13, 'fixedSL': 300, 'trailSL': 1, 'fixedTP': 150, 'trailTP': 1, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2019, 'ToMonth': 6, 'ToDay': 19, 'ToYear': 2030}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
