"""batch_011 port of 移动平均线穿越策略Crossing-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-30 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="EMA 34, 89, 200 e cruzamento das EMA", overlay=true)\n\n// Input options\nfastMALen = input(title="Fast MA",  defval=34)\nmidMALen  = input(title="Medium MA",  defval=89)\nslowMALen = input(title="Slow MA",  defval=200)\n\n// Calculate values\nfastMA = ema(close, fastMALen)\nmidMA  = ema(close, midMALen)\nslowMA = ema(close, slowMALen)\n\n// Plot values\nplot(series=fastMA, color=yellow,\n     title="Fast MA", linewidth=3, trackprice=false)\nplot(series=midMA, color=red,\n     title="Mid MA", linewidth=4, trackprice=false)\nplot(series=slowMA, color=white,\n     title="Slow MA", linewidth=5)\n\n// Highlight crossovers\nlongCondition = crossover(ema(close, 34), ema(close, 200)) \nif (longCondition)\n    strategy.entry("COMPRA FINAL", strategy.long)\n\nlongCondition1 = crossover(ema(close, 34), ema(close, 89)) \nif (longCondition1)\n    strategy.entry("COMPRA INICIAL", strategy.long)\n\nshortCondition = crossunder(ema(close, 34), ema(close, 200))\nif (shortCondition)\n    strategy.entry("VENDE FINAL", strategy.short)\n    \nshortCondition1 = crossunder(ema(close, 34), ema(close, 89))\nif (shortCondition1)\n    strategy.entry("VENDE INICIAL", strategy.short)\n'

class SM744A02402309980C(PinePortBase, IStrategy):
    source_id = "SM_744a02402309980c"
    source_file = '移动平均线穿越策略Crossing-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastMALen': 34, 'midMALen': 89, 'slowMALen': 200}
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
