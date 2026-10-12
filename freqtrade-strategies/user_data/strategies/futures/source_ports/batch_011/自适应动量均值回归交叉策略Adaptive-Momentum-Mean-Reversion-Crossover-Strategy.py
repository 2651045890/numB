"""batch_011 port of 自适应动量均值回归交叉策略Adaptive-Momentum-Mean-Reversion-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Adaptive Momentum Reversion Strategy ", overlay=false, initial_capital=50000, pyramiding=0, commission_type=strategy.commission.cash_per_contract, commission_value=0.05, slippage=1)\n\n// Input: ROC Period\nrocPeriod = input.int(2, title="ROC Period", minval=1)\n\n// Input: Bollinger Bands Settings (Lower Band)\nbbLowerLength = input.int(18, title="Lower Bollinger Band Length", minval=1)\nbbLowerStdDev = input.float(1.7, title="Lower Bollinger Band StdDev", minval=0.1, step=0.1)\n\n// Input: Bollinger Bands Settings (Upper Band)\nbbUpperLength = input.int(21, title="Upper Bollinger Band Length", minval=1)\nbbUpperStdDev = input.float(2.1, title="Upper Bollinger Band StdDev", minval=0.1, step=0.1)\n\n// ROC Calculation\nrocValue = (close - close[rocPeriod]) / close[rocPeriod] * 100\n\n// Bollinger Bands Calculation\nbbLowerBasis = ta.sma(rocValue, bbLowerLength)  // Basis for Lower Band\nbbLower = bbLowerBasis - bbLowerStdDev * ta.stdev(rocValue, bbLowerLength)  // Lower Band\n\nbbUpperBasis = ta.sma(rocValue, bbUpperLength)  // Basis for Upper Band\nbbUpper = bbUpperBasis + bbUpperStdDev * ta.stdev(rocValue, bbUpperLength)  // Upper Band\n\n// Plot ROC\nplot(rocValue, color=color.blue, linewidth=2, title="ROC Value")\n\n// Plot Bollinger Bands\nplot(bbLowerBasis, color=color.gray, linewidth=1, title="Lower BB Basis (SMA)")\nplot(bbLower, color=color.green, linewidth=1, title="Lower Bollinger Band")\nplot(bbUpperBasis, color=color.gray, linewidth=1, title="Upper BB Basis (SMA)")\nplot(bbUpper, color=color.red, linewidth=1, title="Upper Bollinger Band")\n\n// Add Zero Line for Reference\nhline(0, "Zero Line", color=color.gray, linestyle=hline.style_dotted)\n\n// Entry Condition: Long when ROC crosses above the lower Bollinger Band\nlongCondition = ta.crossover(rocValue, bbLower)\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Exit Condition: Exit on Upper Bollinger Band Cross or ROC drops below Lower Band again\nexitCondition = ta.crossunder(rocValue, bbUpper)\nif (exitCondition)\n    strategy.close("Long")\n\n// Background Color for Extreme Conditions\nbgcolor(rocValue > bbUpper ? color.new(color.red, 80) : na, title="Overbought (ROC above Upper BB)")\nbgcolor(rocValue < bbLower ? color.new(color.green, 80) : na, title="Oversold (ROC below Lower BB)")'

class SMDBE2BB0BF36AAA70(PinePortBase, IStrategy):
    source_id = "SM_dbe2bb0bf36aaa70"
    source_file = '自适应动量均值回归交叉策略Adaptive-Momentum-Mean-Reversion-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'rocPeriod': 2, 'bbLowerLength': 18, 'bbLowerStdDev': 1.7, 'bbUpperLength': 21, 'bbUpperStdDev': 2.1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0.05
    source_pyramiding = 0
    source_initial_capital = 50000
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
