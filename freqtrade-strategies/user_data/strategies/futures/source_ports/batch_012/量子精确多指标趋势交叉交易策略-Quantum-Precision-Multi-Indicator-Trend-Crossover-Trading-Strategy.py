"""batch_012 port of 量子精确多指标趋势交叉交易策略-Quantum-Precision-Multi-Indicator-Trend-Crossover-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-22 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Quantum Precision Forex Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Input parameters\natrLength = input(14, "ATR Length")\natrMultiplier = input(2.0, "ATR Multiplier")\nriskRewardRatio = input(3, "Risk-Reward Ratio")\nconfirmationLength = input(10, "Confirmation Period")\n\n// ATR Calculation\naTR = ta.atr(atrLength)\nstopLoss = atrMultiplier * aTR\ntakeProfit = stopLoss * riskRewardRatio\n\n// Custom Quantum Confirmation Indicator\nmomentum = ta.mom(close, confirmationLength)\nvolatility = ta.stdev(close, 20) > ta.sma(ta.stdev(close, 20), 50)\ntrendStrength = ta.ema(close, 20) > ta.ema(close, 50)\nconfirmationSignal = momentum > 0 and volatility and trendStrength\n\n// Entry Conditions\nlongCondition = confirmationSignal and ta.crossover(ta.ema(close, 10), ta.ema(close, 30))\nshortCondition = not confirmationSignal and ta.crossunder(ta.ema(close, 10), ta.ema(close, 30))\n\nif (longCondition)\n    strategy.entry("Quantum Long", strategy.long)\n    strategy.exit("Quantum Exit Long", from_entry="Quantum Long", stop=close - stopLoss, limit=close + takeProfit)\n\nif (shortCondition)\n    strategy.entry("Quantum Short", strategy.short)\n    strategy.exit("Quantum Exit Short", from_entry="Quantum Short", stop=close + stopLoss, limit=close - takeProfit)\n\n// Neural Adaptive Trendlines\ntrendlineShort = ta.linreg(close, 10, 0)\ntrendlineLong = ta.linreg(close, 50, 0)\nplot(trendlineShort, title="Short-Term Trendline", color=color.blue, linewidth=2)\nplot(trendlineLong, title="Long-Term Trendline", color=color.red, linewidth=2)\n\n// AI-Inspired Market Sentiment Indicator\nmarketSentiment = ta.correlation(ta.ema(close, 10), ta.ema(close, 50), 20)\nplot(marketSentiment, title="Market Sentiment", color=color.green)\n'

class SMQuantumPrecisionMultiIndicatorTrendCrossoverTradingStrafd1a0b(PinePortBase, IStrategy):
    source_id = "SM_fd1a0bebdcccf8be"
    source_file = '量子精确多指标趋势交叉交易策略-Quantum-Precision-Multi-Indicator-Trend-Crossover-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrLength': 14, 'atrMultiplier': 2.0, 'riskRewardRatio': 3, 'confirmationLength': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
