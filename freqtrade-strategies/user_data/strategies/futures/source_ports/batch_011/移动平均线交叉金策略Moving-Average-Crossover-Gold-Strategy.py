"""batch_011 port of 移动平均线交叉金策略Moving-Average-Crossover-Gold-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-20 00:00:00\nend: 2023-12-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("XAUUSD Strategy with SL, TP, and BE", shorttitle="EA", overlay=true)\n\n// Define strategy parameters\nfastLength = input(9, title="Fast EMA Length")\nslowLength = input(21, title="Slow EMA Length")\nstopLossPercent = input(1, title="Stop Loss (%)", minval=0, maxval=5) / 100\ntakeProfitPercent = input(2, title="Take Profit (%)", minval=0, maxval=5) / 100\nbreakEvenPercent = input(1, title="Break Even (%)", minval=0, maxval=5) / 100\n\n// Calculate EMAs\nfastEMA = ema(close, fastLength)\nslowEMA = ema(close, slowLength)\n\n// Plot EMAs on the chart\nplot(fastEMA, color=color.blue, title="Fast EMA")\nplot(slowEMA, color=color.red, title="Slow EMA")\n\n// Strategy logic\nenterLong = crossover(fastEMA, slowEMA)\nexitLong = crossunder(fastEMA, slowEMA)\n\nenterShort = crossunder(fastEMA, slowEMA)\nexitShort = crossover(fastEMA, slowEMA)\n\n// Calculate stop loss, take profit, and break-even levels\nlongStopLoss = close * (1 - stopLossPercent)\nlongTakeProfit = close * (1 + takeProfitPercent)\nshortStopLoss = close * (1 + stopLossPercent)\nshortTakeProfit = close * (1 - takeProfitPercent)\n\nlongBreakEven = close * (1 + breakEvenPercent)\nshortBreakEven = close * (1 - breakEvenPercent)\n\n// Execute strategy with stop loss, take profit, and break-even\nstrategy.entry("Long", strategy.long, when = enterLong)\nstrategy.exit("Take Profit/Stop Loss Long", from_entry="Long", profit = longTakeProfit, loss = longStopLoss)\n\nstrategy.entry("Short", strategy.short, when = enterShort)\nstrategy.exit("Take Profit/Stop Loss Short", from_entry="Short", profit = shortTakeProfit, loss = shortStopLoss)\n\n// Move stop loss to break even when price reaches break-even level\nstrategy.exit("Break Even Long", from_entry="Long", loss = longBreakEven)\nstrategy.exit("Break Even Short", from_entry="Short", loss = shortBreakEven)\n'

class SM9F7B11E2B2B70D0B(PinePortBase, IStrategy):
    source_id = "SM_9f7b11e2b2b70d0b"
    source_file = '移动平均线交叉金策略Moving-Average-Crossover-Gold-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowLength': 21, 'stopLossPercent': 1, 'takeProfitPercent': 2, 'breakEvenPercent': 1}
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
