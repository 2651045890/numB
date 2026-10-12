"""batch_011 port of 突破型上升趋势参考策略Quantitative-Breakthrough-Uptrend-Reference-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-14 00:00:00\nend: 2024-02-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © CheatCode1\n\n//@version=5\nstrategy("Quantitative Trend Strategy- Uptrend long", \'Steady Uptrend Strategy\', overlay=true, initial_capital = 1500, default_qty_value = 100, commission_type = strategy.commission.percent, commission_value = 0.01, default_qty_type = strategy.percent_of_equity)\n\n\nlength = input.int(20, minval=1)\nsrc = input(close, title="Source")\nbasis = ta.sma(src, length)\noffset = input.int(0, "Offset", minval = -500, maxval = 500)\nplot(basis, "Basis", color=#FF6D00, offset = offset)\n\ninp1 = input.int(46, \'LookbackLeft\')\ninp2 = input.int(32, \'LookbackRight\')\n\nl1 = ta.pivothigh(close, inp1, inp2)\nS1 = ta.pivotlow(close, inp1, inp2)\n\n// plot(l1, \'Pivothigh\', color.red, 1)\n// // plot(S1, \'Pivot Low\', color.red)\n\nl1V = ta.valuewhen(l1, close, 0)\nS1V = ta.valuewhen(S1, close, 0)\n\nPlotl1 = not na(l1) ? l1V : na\nPlotS1 = not na(S1) ? S1V : na\n\nplot(Plotl1, \'Resistance\', color.green, 1, plot.style_stepline, true)\nplot(PlotS1, \'Support\', color.red, 1, plot.style_stepline, true)\n\nPriceforlong = close > l1V ? true : na\nPriceforshort = close < S1V ? true : na\n\nplotshape(Priceforlong ? high : na, \'p\', shape.arrowup, location.abovebar, color.green, size = size.small)\nplotshape(Priceforshort ? low : na, \'s\', shape.arrowdown, location.belowbar, color.red, size = size.small)\n\nvol = volume\nvolma = ta.sma(vol, 20)\n\nPlotl1C = ta.valuewhen(na(Plotl1), l1V, 0)\nPlotS1C = ta.valuewhen(na(PlotS1), S1V, 0)\n//Strategy Execution\nvolc = volume > volma \n\nLc1 = Priceforlong \n\nSc1 = Priceforshort\n\nsL = Plotl1 < PlotS1 ? close : na\nsS = PlotS1 > Plotl1 ? close : na\n\n\nif Lc1 \n    strategy.entry(\'Long\', strategy.long)\n// if Sc1 and C2\n//     strategy.entry(\'Short\', strategy.short)\n\nif Priceforshort\n    strategy.cancel(\'Long\')\nif Priceforlong   \n    strategy.cancel(\'Short\')\n\n\n// Stp1 = ta.crossover(k, d)\n// Ltp1 = ta.crossunder(k, d)\n// Ltp = d > 70  ? Ltp1 : na\n// Stp = d < 30  ? Stp1 : na\n\n\nif strategy.openprofit >= 0 and sL\n    strategy.close(\'Long\')\nif strategy.openprofit >= 0 and sS\n    strategy.close(\'Short\')\ntakeP = input.float(2, title=\'Take Profit\') / 100\nstopL = input.float(1.75, title=\'Stop Loss\') / 100\n\n\n// // Pre Directionality\n\nStop_L = strategy.position_avg_price * (1 - stopL)\n\nStop_S = strategy.position_avg_price * (1 + stopL)\n\nTake_S= strategy.position_avg_price * (1 - takeP)\n\nTake_L = strategy.position_avg_price * (1 + takeP)\n     \n// sL = Plotl1 < PlotS1 ? close : na\n// sS = PlotS1 < Plotl1 ? close : na\n     \n// //Post Excecution\nif strategy.position_size > 0 and not (Lc1)\n    strategy.exit("Close Long", stop = Stop_L, limit = Take_L)\n\nif strategy.position_size < 0 and not (Sc1)\n    strategy.exit("Close Short", stop = Stop_S, limit = Take_S)'

class SM4AA95B314D581F13(PinePortBase, IStrategy):
    source_id = "SM_4aa95b314d581f13"
    source_file = '突破型上升趋势参考策略Quantitative-Breakthrough-Uptrend-Reference-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 20, 'offset': 0, 'inp1': 46, 'inp2': 32, 'takeP': 2, 'stopL': 1.75}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.01
    source_pyramiding = 0
    source_initial_capital = 1500
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
