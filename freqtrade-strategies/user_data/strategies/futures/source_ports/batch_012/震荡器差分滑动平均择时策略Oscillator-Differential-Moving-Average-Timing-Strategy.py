"""batch_012 port of 震荡器差分滑动平均择时策略Oscillator-Differential-Moving-Average-Timing-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-19 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="MACD Histogram Backtest", shorttitle="MACD")\n\n// Getting inputs\nfast_length = input(title="Fast Length", type=input.integer, defval=12)\nslow_length = input(title="Slow Length", type=input.integer, defval=26)\nsrc = input(title="Source", type=input.source, defval=close)\nsignal_length = input(title="Signal Smoothing", type=input.integer, minval = 1, maxval = 50, defval = 9)\nsma_source = input(title="Simple MA(Oscillator)", type=input.bool, defval=false)\nsma_signal = input(title="Simple MA(Signal Line)", type=input.bool, defval=false)\n\n// Plot colors\ncol_grow_above = #26A69A\ncol_grow_below = #FFCDD2\ncol_fall_above = #B2DFDB\ncol_fall_below = #EF5350\ncol_macd = #0094ff\ncol_signal = #ff6a00\n\n// Calculating\nfast_ma = sma_source ? sma(src, fast_length) : ema(src, fast_length)\nslow_ma = sma_source ? sma(src, slow_length) : ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal ? sma(macd, signal_length) : ema(macd, signal_length)\nhist = macd - signal\n\ngrow = (hist[1] < hist)\nfall = (hist[1] > hist) and hist >= 0\nstop = (hist[1] > hist)\n\nplot(hist, title="Histogram", style=plot.style_columns, color=(hist>=0 ? (hist[1] < hist ? col_grow_above : col_fall_above) : (hist[1] < hist ? col_grow_below : col_fall_below) ), transp=0 )\nplot(macd, title="MACD", color=col_macd, transp=0)\nplot(signal, title="Signal", color=col_signal, transp=0)\n\n//Strategy Testing\n\n// Component Code Start\n// Example usage:\n// if testPeriod()\n//   strategy.entry("LE", strategy.long)\ntestStartYear = input(2017, "Backtest Start Year")\ntestStartMonth = input(01, "Backtest Start Month")\ntestStartDay = input(2, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(30, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\n// A switch to control background coloring of the test period\ntestPeriodBackground = input(title="Color Background?", type=input.bool, defval=true)\ntestPeriodBackgroundColor = testPeriodBackground and (time >= testPeriodStart) and (time <= testPeriodStop) ? #00FF00 : na\nbgcolor(testPeriodBackgroundColor, transp=97)\n\ntestPeriod() => true\n// Component Code Stop\n\n//Entry and Close settings\nif testPeriod() \n    strategy.entry("grow", true, 10, when = grow, limit = close)\n    strategy.close("grow", when = fall)\n    strategy.close("grow", when = stop)\n    \n//if testPeriod() \n//   strategy.entry("fall", false, 1000, when = fall, limit = close)\n//    strategy.close("fall", when = grow)    \n\n\n'

class SMOscillatorDifferentialMovingAverageTimingStrategy8b2ae8(PinePortBase, IStrategy):
    source_id = "SM_8b2ae857c52b6516"
    source_file = '震荡器差分滑动平均择时策略Oscillator-Differential-Moving-Average-Timing-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fast_length': 12, 'slow_length': 26, 'src': 'close', 'signal_length': 9, 'sma_source': False, 'sma_signal': False, 'testStartYear': 2017, 'testStartMonth': 1, 'testStartDay': 2, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 30, 'testPeriodBackground': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
