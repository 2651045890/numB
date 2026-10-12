"""batch_012 port of 量子启发式概率趋势交易策略基于EMA和RSI的量化模型-Quantum-Inspired-Probability-Trend-Trading-Strategy-EMA-RSI-Based-Quantitative-Model.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-24 00:00:00\nend: 2025-03-23 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Quantum-Inspired Trading Strategy", overlay=true)\n\n// Parameters\nemaShortLength = input.int(9, "Short EMA")\nemaMidLength = input.int(19, "Mid EMA")\nemaLongLength = input.int(55, "Long EMA")\natrLength = input.int(14, "ATR Length")\nkFactor = input.float(0.1, "Quantum Walk Factor")\n\n// Moving Averages & Trend Probability\nemaShort = ta.ema(close, emaShortLength)\nemaMid = ta.ema(close, emaMidLength)\nemaLong = ta.ema(close, emaLongLength)\n\ntrendProb = 1 / (1 + math.exp(-kFactor * (emaShort - emaLong)))\ntrendBullish = trendProb > 0.6\ntrendBearish = trendProb < 0.4\n\n// RSI-Based Quantum Stochastic Walk Entry Probability\nrsi = ta.rsi(close, 14)\nprobabilityDirection = 1 / (1 + math.exp(-kFactor * (rsi - 50)))\nlongCondition = probabilityDirection > 0.55 and trendBullish\nshortCondition = probabilityDirection < 0.45 and trendBearish\n\n// ATR-Based Quantum Decay Stop Loss & Take Profit\natr = ta.atr(atrLength)\ntimeDecay = bar_index % 50 // Use bar_index directly\n\ndecayFactor = math.exp(-0.02 * timeDecay)\nstopLoss = atr / decayFactor\ntakeProfit = atr * 1.5 / decayFactor\n\n// Trade Execution\nif longCondition\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", from_entry="Long", stop=close - stopLoss, limit=close + takeProfit)\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", from_entry="Short", stop=close + stopLoss, limit=close - takeProfit)\n\n// Plotting indicators\nplot(emaShort, color=color.blue, title="Short EMA")\nplot(emaMid, color=color.orange, title="Mid EMA")\nplot(emaLong, color=color.red, title="Long EMA")\n\n'

class SMEMARSIQuantumInspiredProbabilityTrendTradingStrategyEMAac77c1(PinePortBase, IStrategy):
    source_id = "SM_ac77c181f3e96cd4"
    source_file = '量子启发式概率趋势交易策略基于EMA和RSI的量化模型-Quantum-Inspired-Probability-Trend-Trading-Strategy-EMA-RSI-Based-Quantitative-Model.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaShortLength': 9, 'emaMidLength': 19, 'emaLongLength': 55, 'atrLength': 14, 'kFactor': 0.1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
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
