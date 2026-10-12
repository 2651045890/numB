"""batch_011 port of 自适应多状态EMA-RSI动量策略结合波动指数过滤系统-Adaptive-Multi-State-EMA-RSI-Momentum-Strategy-with-Choppiness-Index-Filter-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-12-19 00:00:00\nend: 2024-12-26 00:00:00\nperiod: 45m\nbasePeriod: 45m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © nopology\n\n//@version=6\n\nstrategy("CI, EMA, RSI", overlay=false)\n\n// Input parameters\nlengthCI = input(14, title="CI Length")\nlengthRSI = input(14, title="RSI Length")\nfastLength = input(9, title="Fast EMA Length")\nslowLength = input(21, title="Slow EMA Length")\n\n// Calculate CI\natr = ta.atr(lengthCI)\nhighLowRange = math.log10(math.max(high[lengthCI], high) - math.min(low[lengthCI], low))\nsumATR = math.sum(atr, lengthCI)\nci = 100 * (math.log10(sumATR / highLowRange) / math.log10(lengthCI))\n\n// Calculate RSI\nrsi = ta.rsi(close, lengthRSI)\n\n// Calculate EMAs\nfastEMA = ta.ema(close, fastLength)\nslowEMA = ta.ema(close, slowLength)\n\n// Define conditions\ntrendingMarket = ci < 38.2\nrangingMarket = ci > 61.8\nbullishSignal = ta.crossover(fastEMA, slowEMA) and rsi < 70\nbearishSignal = ta.crossover(slowEMA, fastEMA) and rsi > 30\n\n// Plot indicators for visualization\nplot(ci, title="Choppiness Index", color=color.purple, linewidth=2)\nplot(fastEMA, title="Fast EMA", color=color.blue)\nplot(slowEMA, title="Slow EMA", color=color.red)\n\n// Strategy Execution\nif (trendingMarket)\n    if (bullishSignal)\n        strategy.entry("Long", strategy.long)\n    if (bearishSignal)\n        strategy.entry("Short", strategy.short)\nelse if (rangingMarket)\n    if (rsi < 30)\n        strategy.entry("Long", strategy.long)\n    if (rsi > 70)\n        strategy.entry("Short", strategy.short)\n\n// Close positions when conditions no longer met or reverse\nif (trendingMarket and not bullishSignal)\n    strategy.close("Long")\nif (trendingMarket and not bearishSignal)\n    strategy.close("Short")\nif (rangingMarket and rsi > 40)\n    strategy.close("Long")\nif (rangingMarket and rsi < 60)\n    strategy.close("Short")\n\n// Optional: Add stop loss and take profit\nstopLossPerc = input.float(2, title="Stop Loss (%)", minval=0.1, step=0.1) / 100\ntakeProfitPerc = input.float(4, title="Take Profit (%)", minval=0.1, step=0.1) / 100\n\nstrategy.exit("Exit Long", "Long", stop=close*(1-stopLossPerc), limit=close*(1+takeProfitPerc))\nstrategy.exit("Exit Short", "Short", stop=close*(1+stopLossPerc), limit=close*(1-takeProfitPerc))'

class SMD4FD68535F80CD69(PinePortBase, IStrategy):
    source_id = "SM_d4fd68535f80cd69"
    source_file = '自适应多状态EMA-RSI动量策略结合波动指数过滤系统-Adaptive-Multi-State-EMA-RSI-Momentum-Strategy-with-Choppiness-Index-Filter-System.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'lengthCI': 14, 'lengthRSI': 14, 'fastLength': 9, 'slowLength': 21, 'stopLossPerc': 2, 'takeProfitPerc': 4}
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
