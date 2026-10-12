"""batch_012 port of 高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-31 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 30m\nbasePeriod: 30m\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("RSI + Bollinger Bands Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Bollinger Bands Settings\nbbLength = input.int(20, title="BB Length")\nbbStdDev = input.float(2.0, title="BB Standard Deviation")\nbasis = ta.sma(close, bbLength)\ndev = bbStdDev * ta.stdev(close, bbLength)\nupperBB = basis + dev\nlowerBB = basis - dev\n\n// Plot Bollinger Bands\nplot(basis, color=color.orange, title="BB Basis")\nplot(upperBB, color=color.blue, title="Upper Bollinger Band")\nplot(lowerBB, color=color.blue, title="Lower Bollinger Band")\nfill(plot(upperBB), plot(lowerBB), color=color.blue, transp=90, title="BB Fill")\n\n// RSI Settings\nrsiLength = input.int(14, title="RSI Length")\nrsiOverbought = input.int(70, title="RSI Overbought Level")\nrsiOversold = input.int(30, title="RSI Oversold Level")\nrsi = ta.rsi(close, rsiLength)\n\n// Plot RSI on separate pane\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.green)\nplot(rsi, color=color.purple, title="RSI", linewidth=2, display=display.none) // Hidden on main chart\n\n// Long Condition: RSI crosses above oversold and price touches lower BB\nlongCondition = ta.crossover(rsi, rsiOversold) and close <= lowerBB\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short Condition: RSI crosses below overbought and price touches upper BB\nshortCondition = ta.crossunder(rsi, rsiOverbought) and close >= upperBB\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Exit Long: RSI crosses above overbought or price crosses above basis\nexitLong = ta.crossunder(rsi, rsiOverbought) or close >= basis\nif (exitLong)\n    strategy.close("Long")\n\n// Exit Short: RSI crosses below oversold or price crosses below basis\nexitShort = ta.crossover(rsi, rsiOversold) or close <= basis\nif (exitShort)\n    strategy.close("Short")\n\n'

class SMRSIAdvancedDualMovingAverageMomentumReversalStrategyRSIaa566f(PinePortBase, IStrategy):
    source_id = "SM_aa566f92cd4dba0a"
    source_file = '高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'bbLength': 20, 'bbStdDev': 2.0, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
