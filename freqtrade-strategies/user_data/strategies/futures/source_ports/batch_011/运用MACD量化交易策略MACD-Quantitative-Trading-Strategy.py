"""batch_011 port of 运用MACD量化交易策略MACD-Quantitative-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '//@version=3\nstrategy(title="MACD - EURUSD", shorttitle="MACD EURUSD")\n\n// Getting inputs\nfast_length = input(title="Fast Length",  defval=12)\nslow_length = input(title="Slow Length",  defval=26)\nsrc = input(title="Source", defval=close)\nsignal_length = input(title="Signal Smoothing",  minval = 1, maxval = 50, defval =9)\nsma_source = input(title="Simple MA(Oscillator)", type=bool, defval=false)\nsma_signal = input(title="Simple MA(Signal Line)", type=bool, defval=false)\n\n// Plot colors\ncol_grow_above = #26A69A\ncol_grow_below = #FFCDD2\ncol_fall_above = #B2DFDB\ncol_fall_below = #EF5350\ncol_macd = #0094ff\ncol_signal = #ff6a00\n\n// Calculating\nfast_ma = sma_source ? sma(src, fast_length) : ema(src, fast_length)\nslow_ma = sma_source ? sma(src, slow_length) : ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal ? sma(macd, signal_length) : ema(macd, signal_length)\nhist = macd - signal\n\nplot(hist, title="Histogram", style=columns, color=(hist>=0 ? (hist[1] < hist ? col_grow_above : col_fall_above) : (hist[1] < hist ? col_grow_below : col_fall_below) ), transp=0 )\nplot(macd, title="MACD", color=col_macd, transp=0)\nplot(signal, title="Signal", color=col_signal, transp=0)\n\nlongCond = crossover(macd, signal) and macd < -0.00025\nexitLong = crossover(macd, hist)\n\n\nstrategy.entry("long", strategy.long,  when=longCond==true)\nstrategy.close("long", when=exitLong==true)'

class SM3BCBB9C2392A46F6(PinePortBase, IStrategy):
    source_id = "SM_3bcbb9c2392a46f6"
    source_file = '运用MACD量化交易策略MACD-Quantitative-Trading-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'fast_length': 12, 'slow_length': 26, 'signal_length': 9, 'sma_source': False, 'sma_signal': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
