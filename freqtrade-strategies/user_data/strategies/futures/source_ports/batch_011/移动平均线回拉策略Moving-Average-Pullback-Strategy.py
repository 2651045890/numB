"""batch_011 port of 移动平均线回拉策略Moving-Average-Pullback-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-12 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("MAC Pullback", overlay=true)\n\n// Setting up timeperiod for testing\nstartPeriodYear = input(2014, "Backtest Start Year")\nstartPeriodMonth = input(1, "Backtest Start Month")\nstartPeriodDay = input(2, "Backtest Start Day")\ntestPeriodStart = timestamp(startPeriodYear, startPeriodMonth, startPeriodDay, 0, 0)\n\nstopPeriodYear = input(2035, "Backtest Stop Year")\nstopPeriodMonth = input(12, "Backtest Stop Month")\nstopPeriodDay = input(30, "Backtest Stop Day")\ntestPeriodStop = timestamp(stopPeriodYear, stopPeriodMonth, stopPeriodDay, 0, 0)\n\n// Moving Averages\nema14 = ema(close, 14)\nema28 = ema(close, 28)\nsma56 = sma(close, 56)\n\n// Plot\nplot(ema14, title="ema14", linewidth=2, color=green)\nplot(ema28, title="ema28", linewidth=2, color=red)\nplot(sma56, title="sma56", linewidth=3, color=blue)\n\n\n// Strategy\ngoLong = cross(ema14, sma56) and ema14 > ema28\ngoShort = cross(ema14, sma56) and ema14 < ema28\n\n\n// Locate Swing Lows\nleftBars = input(20)\nrightBars=input(20)\nswinglow = pivotlow(close, leftBars, rightBars)\nplot(swinglow, style=cross, linewidth=8, color=#00FF00, offset=-rightBars)\n\nif goLong == true and time >= testPeriodStart and time <= testPeriodStop\n    // We try to make sure that we\'re catching the first Pullback after the crossover\n    if ema14[12] < sma56[12] \n        pivotpoint = lowest(40)[0] //lowest value of the month as our swing low\n        \n        // We calculate a Fib 1.272 extension (from the previous swing low to \n        // the crossover long entry\'s open) and use this as our entry target to short the Pullback\n        extensiontarget = ((close[1] - pivotpoint) * 1.27) + pivotpoint\n        shorttarget = ((close[1] - pivotpoint) * 0.618) + pivotpoint        \n        \n        strategy.order("Pullback", strategy.short, 5.0, limit=extensiontarget)\n        // I would like to use a trailing stop but for know we just hope to get \n        // filled if the pullback reaches all the way down to the 0.618.\n        // We also place a tight stop loss since we trying to short an uptrend\n        strategy.exit("Pullback Exit", "Pullback", limit=shorttarget, loss=400)'

class SM16FB7D34EA345897(PinePortBase, IStrategy):
    source_id = "SM_16fb7d34ea345897"
    source_file = '移动平均线回拉策略Moving-Average-Pullback-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'startPeriodYear': 2014, 'startPeriodMonth': 1, 'startPeriodDay': 2, 'stopPeriodYear': 2035, 'stopPeriodMonth': 12, 'stopPeriodDay': 30, 'leftBars': 20, 'rightBars': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
