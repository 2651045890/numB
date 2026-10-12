"""batch_011 port of 自适应移动平均交叉追踪止损策略-Adaptive-Moving-Average-Crossover-with-Trailing-Stop-Loss-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © chinmay.hundekari\n\n//@version=5\n//@version=5\nstrategy("test", overlay = true)\n\n// Calculate two moving averages with different lengths.\nSLMA = input.int(50,"SMA",minval=10,step=1)\nFSMA = input.int(5,"SMA",minval=1,step=1)\nfancy_tests = input.bool(true,"Enable Fancy Changes")\nlongLossPerc = input.float(2, title="Trailing Stop Loss (%)",\n     minval=0.0, step=0.1) * 0.01\nstdMult = input.float(2.0, title="Standard Deviation Multiplier",\n     minval=0.0, step=0.01)\n\nfloat fastMA = ta.sma(close, FSMA)\nfloat slowMA = ta.sma(close, SLMA)\nfloat closMA = ta.sma(close, 25)\n\nconfidence = 1.0\nif (fancy_tests)\n    longLossPerc := stdMult * ta.stdev(ohlc4, 20)/close\nbalance = strategy.initial_capital + strategy.netprofit\nbalanceInContracts = balance* confidence/close\n\n// Enter a long position when `fastMA` crosses over `slowMA`.\nif ta.crossover(fastMA, slowMA)\n    strategy.entry("BUY", strategy.long, qty=balanceInContracts)\n//longStopPrice  = strategy.position_avg_price * (1 - longLossPerc)\n//Trailing Stop loss Code\nlongStopPrice = 0.0\npercLoss = longLossPerc\nlongStopPrice := if strategy.position_size > 0\n    //if (strategy.openprofit_percent/100.0 > longLossPerc)\n    //    percLoss := math.min(strategy.openprofit_percent/200.0, longLossPerc)\n    stopValue = close * (1 - percLoss)\n    math.max(stopValue, longStopPrice[1])\nelse\n    0\nif strategy.position_size > 0\n    strategy.exit("STP", stop=longStopPrice)\nplot(strategy.position_size > 0 ? longStopPrice : na,\n     color=color.red, style=plot.style_cross,\n     linewidth=2, title="Long Stop Loss")\n// Enter a short position when `fastMA` crosses under `slowMA`.\n//if ta.crossunder(fastMA, closMA)\n//    strategy.close_all("SEL")//strategy.entry("sell", strategy.short)\n\n// Plot the moving averages.\nplot(fastMA, "Fast MA", color.aqua)\nplot(slowMA, "Slow MA", color.orange)\nplot((confidence)*(close), "Confidence", color=color.green, linewidth=2)\n'

class SM0473D1DDF7A9F823(PinePortBase, IStrategy):
    source_id = "SM_0473d1ddf7a9f823"
    source_file = '自适应移动平均交叉追踪止损策略-Adaptive-Moving-Average-Crossover-with-Trailing-Stop-Loss-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'SLMA': 50, 'FSMA': 5, 'fancy_tests': True, 'longLossPerc': 2, 'stdMult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
