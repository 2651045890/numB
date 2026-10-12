"""batch_011 port of 突破新低回归均线策略Mean-Reversion-Breakout-Low-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © merovinh\n\n//@version=5\nstrategy(title="Merovinh - Mean Reversion Lowest low",\n     overlay = true,\n     default_qty_type = strategy.percent_of_equity,\n     initial_capital = 10000,\n     default_qty_value = 10,\n     commission_type = strategy.commission.percent,\n     slippage = 1,\n     commission_value = 0.04)\n\nGR_TIME = \'Time Period\'\n\nbars = input(9, title = "Minimum number of bars", tooltip = "The minimum number of bars before updating lowest low / highest high")\n\nnumberOfLows  = input.string(defval=\'One\', title=\'Number of broken lows\', options=[\'One\', \'Two\', \'Three\', \'Four\'])\n\n//Period\n\nvar prevLow = .0\nvar prevHigh = .0\nvar prevLow2 = .0\nvar prevLow3 = .0\nvar prevLow4 = .0\n\ntruetime = true\n\n\nhighestHigh = ta.highest(high, bars)\nlowestLow = ta.lowest(low, bars)\n\nif numberOfLows == \'One\'\n    if truetime and prevLow > 0 and lowestLow < prevLow\n        strategy.entry(\'long\', strategy.long)\nif numberOfLows == \'Two\'\n    if truetime and prevLow > 0 and lowestLow < prevLow and prevLow < prevLow2\n        strategy.entry(\'long\', strategy.long)\nif numberOfLows == \'Three\'\n    if truetime and prevLow > 0 and lowestLow < prevLow and prevLow < prevLow2 and prevLow2 < prevLow3\n        strategy.entry(\'long\', strategy.long)\nif numberOfLows == \'Four\'\n    if truetime and prevLow > 0 and lowestLow < prevLow and prevLow < prevLow2 and prevLow2 < prevLow3 and prevLow3 < prevLow4\n        strategy.entry(\'long\', strategy.long)\n\nif truetime and prevHigh > 0 and highestHigh > prevHigh\n    strategy.close(\'long\')\n\n\nif prevLow != lowestLow\n    prevLow4 := prevLow3\n    prevLow3 := prevLow2\n    prevLow2 := prevLow\n    prevLow := lowestLow\nprevHigh := highestHigh\n\nplot(lowestLow, color=color.green, linewidth=1, title="Lowest Low Line")\nplot(highestHigh, color=color.green, linewidth=1, title="Highest High Line")\n\n\n'

class SM70BAD29D16D052F4(PinePortBase, IStrategy):
    source_id = "SM_70bad29d16d052f4"
    source_file = '突破新低回归均线策略Mean-Reversion-Breakout-Low-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'bars': 9, 'numberOfLows': 'One'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.04
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
