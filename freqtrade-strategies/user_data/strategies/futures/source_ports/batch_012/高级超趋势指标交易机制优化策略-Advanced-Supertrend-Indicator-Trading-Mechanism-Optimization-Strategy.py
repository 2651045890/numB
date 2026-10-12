"""batch_012 port of 高级超趋势指标交易机制优化策略-Advanced-Supertrend-Indicator-Trading-Mechanism-Optimization-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-08-01 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"DOGE_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend Strategy with Money Ocean Trade", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Input parameters\nsupertrendLength = input.int(6, title="Supertrend Length")\nsupertrendFactor = input.float(0.25, title="Supertrend Factor")\n\n// Supertrend calculation\n[supertrend, direction] = ta.supertrend(supertrendFactor, supertrendLength)\n\n// Plot Supertrend line\nsupertrendColor = direction == 1 ? color.green : color.red\nplot(supertrend, title="Supertrend", color=supertrendColor, linewidth=2, style=plot.style_line)\n\n// Variables to track trend change and candle break\nvar bool trendChanged = false\nvar float prevSupertrend = na\n\nif (not na(prevSupertrend) and direction != nz(ta.valuewhen(prevSupertrend != supertrend, direction, 1)))\n    trendChanged := true\nelse\n    trendChanged := false\n\nprevSupertrend := supertrend\n\nlongEntry = trendChanged and close[1] < supertrend[1] and close > supertrend\nshortEntry = trendChanged and close[1] > supertrend[1] and close < supertrend\n\n// Strategy execution\nif (longEntry)\n    strategy.entry("Long", strategy.long)\n\nif (shortEntry)\n    strategy.entry("Short", strategy.short)\n\n// Plot entry signals on the chart\nplotshape(series=longEntry, location=location.belowbar, color=color.green, style=shape.labelup, title="BUY")\nplotshape(series=shortEntry, location=location.abovebar, color=color.red, style=shape.labeldown, title="SELL")\n\n// Alerts\nalertcondition(longEntry, title="Buy Signal", message="Buy Signal Triggered!")\nalertcondition(shortEntry, title="Short Signal", message="Short Signal Triggered!")\n\n\n'

class SMAdvancedSupertrendIndicatorTradingMechanismOptimizationbad9c9(PinePortBase, IStrategy):
    source_id = "SM_bad9c989e15a29ca"
    source_file = '高级超趋势指标交易机制优化策略-Advanced-Supertrend-Indicator-Trading-Mechanism-Optimization-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'supertrendLength': 6, 'supertrendFactor': 0.25}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
