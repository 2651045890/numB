"""batch_011 port of 突破重叠K线高低位策略Inside-Bar-Range-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-04 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ilikelyrics560\n\n//@version=5\nstrategy("Inside Bar Range Breakout Strategy", overlay=true)\n\n// Inputs\nlookback = input.int(20, "Lookback Period", minval=1)\natrMult = input.float(1.5, "ATR Multiplier", step=0.1)\natrLen = input.int(14, "ATR Length", minval=1)\nslMult = input.float(2, "Stop Loss Multiplier", step=0.1)\ntpMult = input.float(3, "Take Profit Multiplier", step=0.1)\n\n// Variables\natr = ta.atr(atrLen)\nRange = high - low \ninsideBar = Range < Range[1]\nbreakoutUp = close > high[1]\nbreakoutDown = close < low[1]\nliquidityUp = ta.highest(high, lookback)\nliquidityDown = ta.lowest(low, lookback)\nlongEntry = breakoutUp and low > liquidityDown\nshortEntry = breakoutDown and high < liquidityUp\nlongExit = close < low[1] \nshortExit = close > high[1]\n\n// Plotting\nplot(liquidityUp, "Liquidity Up", color.new(color.green, 30), 1)\nplot(liquidityDown, "Liquidity Down", color.new(color.red, 30), 1)\nbgcolor(longEntry ? color.new(color.green, 30) : na, title="Long Entry")\nbgcolor(shortEntry ? color.new(color.maroon, 30) : na, title="Short Entry")\n\n// Trading\nif (longEntry)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long Exit", "Long", stop=low - slMult * atr, limit=high + tpMult * atr)\n\nif (shortEntry)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short Exit", "Short", stop=high + slMult * atr, limit=low - tpMult * atr)'

class SM153FB446A71F2DE7(PinePortBase, IStrategy):
    source_id = "SM_153fb446a71f2de7"
    source_file = '突破重叠K线高低位策略Inside-Bar-Range-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lookback': 20, 'atrMult': 1.5, 'atrLen': 14, 'slMult': 2, 'tpMult': 3}
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
