"""batch_011 port of 趋势追踪EMA策略EMA-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-09 00:00:00\nend: 2023-10-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title = "EMA Close Strategy", shorttitle = "EMA Close",calc_on_order_fills=true,calc_on_every_tick =true, initial_capital=21000,commission_value=.25,overlay = true,default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\nEmaSource   = input(defval = close, title = "EMA Source")\nEmaLength   = input(defval = 8, title = "EMA Period", minval = 1)\n\nStartYear = input(2018, "Backtest Start Year")\nStartMonth = input(1, "Backtest Start Month")\nStartDay = input(1, "Backtest Start Day")\nstopLoss = input(30, title = "Stop loss percentage(0.1%)") \nUseStopLoss = input(true,"UseStopLoss")\n\nwindow() => time >=  timestamp(StartYear, StartMonth, StartDay,00,00) ? true : false\n\n\n\nEMA = ema(EmaSource,EmaLength)\n\nplot(EMA, title = "EMA", color = green, linewidth = 2, style = line, transp = 50)\n\nlong = crossunder(EMA, close)\nshort= crossover(EMA, close)\n\nif (long)\n    strategy.entry("LongId", strategy.long, when=window())\n    \nif (short)\n    strategy.entry("ShortId", strategy.short, when=window())\n\nif (UseStopLoss)\n    strategy.exit("StopLoss", "LongId", loss = close * stopLoss / 1000 / syminfo.mintick)\n    strategy.exit("StopLoss", "ShortId", loss = close * stopLoss / 1000 / syminfo.mintick)'

class SM7991E7BE62E068B2(PinePortBase, IStrategy):
    source_id = "SM_7991e7be62e068b2"
    source_file = '趋势追踪EMA策略EMA-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'EmaLength': 8, 'StartYear': 2018, 'StartMonth': 1, 'StartDay': 1, 'stopLoss': 30, 'UseStopLoss': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.25
    source_pyramiding = 0
    source_initial_capital = 21000
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
