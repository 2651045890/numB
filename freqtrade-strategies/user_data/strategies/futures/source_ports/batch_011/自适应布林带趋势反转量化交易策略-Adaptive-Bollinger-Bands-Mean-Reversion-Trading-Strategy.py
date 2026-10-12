"""batch_011 port of 自适应布林带趋势反转量化交易策略-Adaptive-Bollinger-Bands-Mean-Reversion-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-09 00:00:00\nend: 2025-01-16 00:00:00\nperiod: 10m\nbasePeriod: 10m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Bollinger Bands Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=200)\n\n// Inputs for Bollinger Bands\nbbLength = input.int(20, title="Bollinger Bands Length")\nbbStdDev = input.float(2.0, title="Bollinger Bands StdDev")\n\n// Inputs for Risk Management\nstopLossPerc = input.float(1.0, title="Stop Loss (%)", minval=0.1, step=0.1)\ntakeProfitPerc = input.float(2.0, title="Take Profit (%)", minval=0.1, step=0.1)\n\n// Calculate Bollinger Bands\nbasis = ta.sma(close, bbLength)\nbbStdev = ta.stdev(close, bbLength)\nupper = basis + bbStdDev * bbStdev\nlower = basis - bbStdDev * bbStdev\n\n// Plot Bollinger Bands\nplot(basis, color=color.blue, title="Middle Band")\nplot(upper, color=color.red, title="Upper Band")\nplot(lower, color=color.green, title="Lower Band")\n\n// Entry Conditions\nlongCondition = ta.crossover(close, lower)\nshortCondition = ta.crossunder(close, upper)\n\n// Exit Conditions\nexitLongCondition = ta.crossunder(close, basis)\nexitShortCondition = ta.crossover(close, basis)\n\n// Stop Loss and Take Profit Levels\nlongStopLoss = close * (1 - stopLossPerc / 100)\nlongTakeProfit = close * (1 + takeProfitPerc / 100)\nshortStopLoss = close * (1 + stopLossPerc / 100)\nshortTakeProfit = close * (1 - takeProfitPerc / 100)\n\n// Execute Long Trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", from_entry="Long", stop=longStopLoss, limit=longTakeProfit)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", from_entry="Short", stop=shortStopLoss, limit=shortTakeProfit)\n\n// Close Positions on Exit Conditions\nif (exitLongCondition and strategy.position_size > 0)\n    strategy.close("Long")\n\nif (exitShortCondition and strategy.position_size < 0)\n    strategy.close("Short")\n\n// ? SOUND ALERTS IN BROWSER ?\nif (longCondition)\n    alert("? Long Entry Signal!", alert.freq_once_per_bar_close)\n\nif (shortCondition)\n    alert("? Short Entry Signal!", alert.freq_once_per_bar_close)\n\nif (exitLongCondition)\n    alert("? Closing Long Trade!", alert.freq_once_per_bar_close)\n\nif (exitShortCondition)\n    alert("? Closing Short Trade!", alert.freq_once_per_bar_close)\n'

class SM9C2B0A2F160D10C3(PinePortBase, IStrategy):
    source_id = "SM_9c2b0a2f160d10c3"
    source_file = '自适应布林带趋势反转量化交易策略-Adaptive-Bollinger-Bands-Mean-Reversion-Trading-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'bbLength': 20, 'bbStdDev': 2.0, 'stopLossPerc': 1.0, 'takeProfitPerc': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 200
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
