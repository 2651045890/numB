"""batch_011 port of 移动平均线交叉策略Simple-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Simple Moving Average Crossover", overlay=true)\n\n// Input parameters\nfastLength = input(10, title="Fast MA Length")\nslowLength = input(30, title="Slow MA Length")\nstopLossPercent = input(1, title="Stop Loss Percentage")\n\n// Calculate moving averages\nfastMA = ta.sma(close, fastLength)\nslowMA = ta.sma(close, slowLength)\n\n// Buy condition: Fast MA crosses above Slow MA\nbuyCondition = ta.crossover(fastMA, slowMA)\n\n// Sell condition: Fast MA crosses below Slow MA\nsellCondition = ta.crossunder(fastMA, slowMA)\n\n// Plot moving averages as lines\nplot(fastMA, color=color.blue, title="Fast MA", linewidth=2)\nplot(slowMA, color=color.red, title="Slow MA", linewidth=2)\n\n// Execute trades based on conditions\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (sellCondition)\n    strategy.close("Buy")\n\n// Set stop loss level\nstopLossLevel = close * (1 - stopLossPercent / 100)\nstrategy.exit("Sell", from_entry="Buy", loss=stopLossLevel)\n\n\n'

class SM12C290DAF59A0162(PinePortBase, IStrategy):
    source_id = "SM_12c290daf59a0162"
    source_file = '移动平均线交叉策略Simple-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fastLength': 10, 'slowLength': 30, 'stopLossPercent': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
