"""batch_011 port of 移动平均线交叉与平仓交易策略Exponential-Moving-Average-and-Moving-Average-Crossover-with-Close-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("EMA and MA Crossover with Close Strategy", shorttitle="EMA_MA_Close", overlay=true)\n\n// Define the length of the Exponential Moving Average and Moving Average\nlengthEMA = 9\nlengthMA = 20\n\n// Calculate the 9 EMA and 20 MA\nema9 = ema(close, lengthEMA)\nma20 = sma(close, lengthMA)\n\n// Define the buy and sell conditions\nbuyCondition = close > ema9 and close > ma20\nsellCondition = close < ema9 and close < ma20\n\n// Define the close position condition\ncloseCondition = crossover(close, ema9) or crossover(close, ma20)\n\n// Execute buy or sell orders\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\nelse if (sellCondition)\n    strategy.entry("Sell", strategy.short)\n\n// Close any position if the close condition is met\nif (closeCondition)\n    strategy.close_all()\n\n// Coloring the candles based on conditions\nbarcolor(buyCondition ? color.green : na)\nbarcolor(sellCondition ? color.red : na)\n\n// Plotting the EMA and MA for reference\nplot(ema9, color=color.blue, title="9 EMA")\nplot(ma20, color=color.orange, title="20 MA")\n'

class SM7078D7FD0C1A0F67(PinePortBase, IStrategy):
    source_id = "SM_7078d7fd0c1a0f67"
    source_file = '移动平均线交叉与平仓交易策略Exponential-Moving-Average-and-Moving-Average-Crossover-with-Close-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
