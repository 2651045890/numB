"""batch_012 port of 黄金交叉均线突破策略Crude-Oil-Moving-Average-Crossover-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-08 00:00:00\nend: 2024-01-07 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Crude Oil Moving Average Crossover", overlay=true)\n\n// Define inputs\nfastLength = input(10, "Fast Length")\nslowLength = input(30, "Slow Length")\n\n// Calculate moving averages\nfastMA = ta.sma(close, fastLength)\nslowMA = ta.sma(close, slowLength)\n\n// Plot moving averages\nplot(fastMA, color=color.blue, title="Fast MA")\nplot(slowMA, color=color.red, title="Slow MA")\n\n// Entry conditions\nlongCondition = ta.crossover(fastMA, slowMA)\nshortCondition = ta.crossunder(fastMA, slowMA)\n\n// Exit conditions\nexitCondition = ta.crossover(slowMA, fastMA)\n\n// Execute strategy\nif longCondition\n    strategy.entry("Buy", strategy.long)\nif shortCondition\n    strategy.entry("Sell", strategy.short)\nif exitCondition\n    strategy.close_all()\n\n// Plot buy and sell signals\nplotshape(longCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(shortCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.small)\n\n\n'

class SMCrudeOilMovingAverageCrossoverStrategy7caff9(PinePortBase, IStrategy):
    source_id = "SM_7caff9cb53353773"
    source_file = '黄金交叉均线突破策略Crude-Oil-Moving-Average-Crossover-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'fastLength': 10, 'slowLength': 30}
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
