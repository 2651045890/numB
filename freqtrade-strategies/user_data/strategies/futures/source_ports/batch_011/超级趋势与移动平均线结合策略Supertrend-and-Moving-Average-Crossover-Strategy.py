"""batch_011 port of 超级趋势与移动平均线结合策略Supertrend-and-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-19 00:00:00\nend: 2024-02-18 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Supertrend and Moving Averages Strategy", overlay=true)\n\n// Supertrend parameters\natrLength = input.int(10, title="ATR Length", minval=1)\nfactor = input.float(3.0, title="Factor", minval=0.01, step=0.01)\n[supertrend, direction] = ta.supertrend(factor, atrLength)\n\n// Moving Averages parameters\nlength_ema = input(10, title="Length of EMA")\nlength_sma = input(20, title="Length of SMA")\n\n// Calculate EMAs and SMAs\nema_10 = ta.ema(close, length_ema)\nsma_20 = ta.sma(close, length_sma)\n\n// Strategy logic\nlongCondition = ema_10 > sma_20 and direction > 0\nshortCondition = ema_10 < sma_20 and direction < 0\n\nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.entry("Short", strategy.short, when=shortCondition)\n\n// Plot Supertrend\nplot(direction > 0 ? supertrend : na, color=color.green, style=plot.style_line, linewidth=2, title="Up Trend")\nplot(direction < 0 ? supertrend : na, color=color.red, style=plot.style_line, linewidth=2, title="Down Trend")\n\n// Plot Moving Averages\nplot(ema_10, color=color.blue, title="10 EMA")\nplot(sma_20, color=color.red, title="20 SMA")\n\n// Alerts for Supertrend\nalertcondition(direction[1] > direction, title=\'Downtrend to Uptrend\', message=\'The Supertrend value switched from Downtrend to Uptrend \')\nalertcondition(direction[1] < direction, title=\'Uptrend to Downtrend\', message=\'The Supertrend value switched from Uptrend to Downtrend\')\nalertcondition(direction[1] != direction, title=\'Trend Change\', message=\'The Supertrend value switched from Uptrend to Downtrend or vice versa\')\n'

class SM6068680DDF7B0C48(PinePortBase, IStrategy):
    source_id = "SM_6068680ddf7b0c48"
    source_file = '超级趋势与移动平均线结合策略Supertrend-and-Moving-Average-Crossover-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'atrLength': 10, 'factor': 3.0, 'length_ema': 10, 'length_sma': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
