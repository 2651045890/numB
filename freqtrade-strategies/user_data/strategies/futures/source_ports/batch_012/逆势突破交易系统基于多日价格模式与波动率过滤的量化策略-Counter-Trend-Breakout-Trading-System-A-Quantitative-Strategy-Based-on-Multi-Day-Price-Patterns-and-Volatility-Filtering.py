"""batch_012 port of 逆势突破交易系统基于多日价格模式与波动率过滤的量化策略-Counter-Trend-Breakout-Trading-System-A-Quantitative-Strategy-Based-on-Multi-Day-Price-Patterns-and-Volatility-Filtering.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-25 00:00:00\nend: 2024-12-14 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n\n//@version=6\nstrategy("3 Red / 3 Green Strategy with Volatility Check", overlay=true, initial_capital=100000, currency=currency.USD)\n\n// Input parameters\nmaxTradeDuration = input.int(title="Maximum Trade Duration (days)", defval=22, minval=1)\nuseGreenExit   = input.bool(title="Use 3 Green Days Exit", defval=true, tooltip = "Exit condition: either 3 consecutive green days (if enabled) or if the trade duration reaches maxTradeDuration days.")\natrPeriod      = input.int(title="ATR Period", defval=12, minval=0, step=1, tooltip="Use zero to disable ATR filter")\n\n// Define red and green days based on open vs close prices\nredDay   = close < open\ngreenDay = close > open\n\n// Conditions: 3 consecutive red days trigger an entry; 3 consecutive green days trigger an exit.\nthreeRed   = redDay and redDay[1] and redDay[2]\nthreeGreen = greenDay and greenDay[1] and greenDay[2]\n\nvar float currentATR = 0.0\nvar float averageATR = 0.0\nvar bool atr_entry = true\n\n// Calculate ATR and its 30-day average\nif(atrPeriod>0)\n    currentATR := ta.atr(atrPeriod)\n    averageATR := ta.sma(currentATR, 30)\n\natr_entry := (currentATR > 0 and averageATR > 0) ? (currentATR > averageATR) : true\n// Persistent variable to record the bar index when the trade is entered.\nvar int entryBarIndex = na\n\n// Entry: When no position is open, 3 consecutive red days occur, and current ATR is above its 30-day average, enter a long trade.\nif (strategy.position_size == 0 and threeRed and atr_entry)\n    strategy.entry("Long", strategy.long)\n    entryBarIndex := bar_index\n\n// Compute trade duration in days using the absolute difference\ntradeDuration = not na(entryBarIndex) ? math.abs(bar_index - entryBarIndex) : 0\n\n// Exit condition: either 3 consecutive green days (if enabled) or if the trade duration reaches maxTradeDuration days.\nexitCondition = (useGreenExit and threeGreen) or (tradeDuration >= maxTradeDuration)\n\nif (strategy.position_size > 0 and exitCondition)\n    strategy.close("Long")\n\n// Reset the entry bar index when a trade just closed.\nif (strategy.position_size[1] > 0 and strategy.position_size == 0)\n    entryBarIndex := na\n\n// Optional: Plot signals and ATR values for visual confirmation.\nplotshape(threeRed, title="Entry Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.tiny)\nplotshape(threeGreen, title="Green Exit Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.tiny)\nplot(currentATR, title="Current ATR", color=color.blue)\nplot(averageATR, title="30-Day Average ATR", color=color.orange)\n\n'

class SMCounterTrendBreakoutTradingSystemAQuantitativeStrategyBb39367(PinePortBase, IStrategy):
    source_id = "SM_b393670e2db4b44b"
    source_file = '逆势突破交易系统基于多日价格模式与波动率过滤的量化策略-Counter-Trend-Breakout-Trading-System-A-Quantitative-Strategy-Based-on-Multi-Day-Price-Patterns-and-Volatility-Filtering.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'maxTradeDuration': 22, 'useGreenExit': True, 'atrPeriod': 12}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
