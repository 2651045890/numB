"""batch_012 port of 高级双均线与超级趋势组合交易策略-Advanced-Dual-EMA-and-Supertrend-Combination-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2024-07-01 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Advanced Supertrend + EMA Strategy", overlay=true)\n\n// =================== PARAMETER INPUTS ===================\n// EMA Parameters\nemaFastLength = input.int(5, "Fast EMA", minval=1, maxval=50, group="EMA Settings")\nemaSlowLength = input.int(20, "Slow EMA", minval=1, maxval=100, group="EMA Settings")\n\n// Supertrend Parameters\natrPeriod = input.int(10, "ATR Period", minval=1, maxval=50, group="Supertrend Settings")\nfactor = input.float(3.0, "Factor", step=0.1, group="Supertrend Settings")\n\n// =================== CALCULATIONS ===================\n// EMA Calculations\nemaFast = ta.ema(close, emaFastLength)\nemaSlow = ta.ema(close, emaSlowLength)\n\n// Supertrend Calculation\n[supertrend, direction] = ta.supertrend(factor, atrPeriod)\n\n// =================== SIGNAL GENERATION ===================\n// EMA Crossovers\nemaCrossUp = ta.crossover(emaFast, emaSlow)\nemaCrossDown = ta.crossunder(emaFast, emaSlow)\n\n// Supertrend Signals\nstUp = direction < 0\nstDown = direction > 0\n\n// Buy and Sell Conditions\nlongCondition = emaCrossUp and stUp\nshortCondition = emaCrossDown and stDown\n\n// =================== GRAPHICAL INDICATORS ===================\n// EMA Lines\nplot(emaFast, color=color.new(color.blue, 0), linewidth=2, title="Fast EMA")\nplot(emaSlow, color=color.new(color.red, 0), linewidth=2, title="Slow EMA")\n\n// Supertrend Line\nsupertrendColor = direction < 0 ? color.green : color.red\nplot(supertrend, color=supertrendColor, linewidth=2, title="Supertrend")\n\n// Buy-Sell Signals\nplotshape(longCondition, title="Buy", text="BUY", location=location.belowbar, \n     color=color.green, style=shape.labelup, size=size.normal, textcolor=color.white)\n\nplotshape(shortCondition, title="Sell", text="SELL", location=location.abovebar, \n     color=color.red, style=shape.labeldown, size=size.normal, textcolor=color.white)\n\n// =================== STRATEGY EXECUTIONS ===================\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.close("Long")\n\n// =================== INFORMATION TABLE ===================\nvar table infoTable = table.new(position.bottom_right, 2, 4, bgcolor=color.new(color.black, 90))\n\n// Signal Status\nsignalText = ""\nsignalColor = color.white\nif (longCondition)\n    signalText := "BUY SIGNAL"\n    signalColor := color.green\nif (shortCondition)\n    signalText := "SELL SIGNAL"\n    signalColor := color.red\n\n// Table Content\ntable.cell(infoTable, 0, 0, "CURRENT SIGNAL", bgcolor=color.new(color.blue, 90))\ntable.cell(infoTable, 1, 0, signalText, text_color=signalColor)\n\ntable.cell(infoTable, 0, 1, "EMA TREND")\ntable.cell(infoTable, 1, 1, emaFast > emaSlow ? "UP" : "DOWN", \n     text_color=emaFast > emaSlow ? color.green : color.red)\n\ntable.cell(infoTable, 0, 2, "SUPERTREND")\ntable.cell(infoTable, 1, 2, direction < 0 ? "UP" : "DOWN", \n     text_color=direction < 0 ? color.green : color.red)\n\n// Last Trade Information\ntable.cell(infoTable, 0, 3, "LAST TRADE")\ntable.cell(infoTable, 1, 3, longCondition ? "BUY" : shortCondition ? "SELL" : "-", \n     text_color=longCondition ? color.green : shortCondition ? color.red : color.white)\n\n'

class SMAdvancedDualEMAandSupertrendCombinationTradingStrategya842ba(PinePortBase, IStrategy):
    source_id = "SM_a842ba132e71504d"
    source_file = '高级双均线与超级趋势组合交易策略-Advanced-Dual-EMA-and-Supertrend-Combination-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'emaFastLength': 5, 'emaSlowLength': 20, 'atrPeriod': 10, 'factor': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
