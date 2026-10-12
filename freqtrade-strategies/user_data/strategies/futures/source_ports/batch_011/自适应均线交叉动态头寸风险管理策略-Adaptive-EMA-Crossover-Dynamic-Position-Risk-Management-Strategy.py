"""batch_011 port of 自适应均线交叉动态头寸风险管理策略-Adaptive-EMA-Crossover-Dynamic-Position-Risk-Management-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2024-07-11 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Carlos Humberto Rodríguez Arias\n\n//@version=5\nstrategy("EMA Crossover Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// EMA periods\nMT_EMA = input.int(21, title="Medium Term EMA")\nLT_EMA = input.int(55, title="Long Term EMA")\nRR = input.float(2.0, title="Risk-Reward Ratio") // User-defined RR\nRiskPercent = input.float(1.0, title="Risk Percentage") // User-defined risk percentage\n\n// Calculate EMAs\nSignal_MT_EMA = ta.ema(close, MT_EMA)\nSignal_LT_EMA = ta.ema(close, LT_EMA)\n\n// Plot EMAs\nplot(Signal_MT_EMA, title="Medium Term EMA", color=color.orange, linewidth=2)\nplot(Signal_LT_EMA, title="Long Term EMA", color=color.blue, linewidth=2)\n\n// Determine trend conditions\nuptrend = ta.crossover(Signal_MT_EMA, Signal_LT_EMA)\ndowntrend = ta.crossunder(Signal_MT_EMA, Signal_LT_EMA)\n\n// Stop-Loss Calculations\nlongStopLoss = ta.lowest(low, 2) // SL for buy = lowest low of last 2 candles\nshortStopLoss = ta.highest(high, 2) // SL for sell = highest high of last 2 candles\n\n// Take-Profit Calculations\nlongTakeProfit = close + (close - longStopLoss) * RR\nshortTakeProfit = close - (shortStopLoss - close) * RR\n\n// Calculate Position Size based on Risk Percentage\ncapital = strategy.equity * (RiskPercent / 100)\nlongPositionSize = capital / (close - longStopLoss)\nshortPositionSize = capital / (shortStopLoss - close)\n\n// Execute Buy Order\nif uptrend\n    strategy.entry("Long", strategy.long, qty=longPositionSize)\n    strategy.exit("Long Exit", from_entry="Long", stop=longStopLoss, limit=longTakeProfit)\n\n// Execute Sell Order\nif downtrend\n    strategy.entry("Short", strategy.short, qty=shortPositionSize)\n    strategy.exit("Short Exit", from_entry="Short", stop=shortStopLoss, limit=shortTakeProfit)\n'

class SMD7C6A12AAAE2122B(PinePortBase, IStrategy):
    source_id = "SM_d7c6a12aaae2122b"
    source_file = '自适应均线交叉动态头寸风险管理策略-Adaptive-EMA-Crossover-Dynamic-Position-Risk-Management-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'MT_EMA': 21, 'LT_EMA': 55, 'RR': 2.0, 'RiskPercent': 1.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
