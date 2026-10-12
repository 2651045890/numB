"""batch_011 port of 移动平均线金叉死叉交易策略Moving-Average-Crossover-MACD-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMMA", max_bars_back = 200)\n\nvar up1 = #26A69A\nvar up2 = #B2DFDB\nvar down1 = #FF5252\nvar down2 = #FFCDD2\nvar confirmationLength = 2\n\nvar earliest = timestamp("20 Jan 2024 00:00 +0000")\n\n// Regn u\nshortEMA = ta.ema(close, 12)\nlongEMA = ta.ema(close, 26)\nmacd = shortEMA - longEMA\nsignal = ta.ema(macd, 9)\ndelta = macd - signal\nabsDelta = math.abs(delta)\npreviousDelta = delta[1]\n\nsignalCrossover = ta.crossover(macd, signal)\nsignalCrossunder = ta.crossunder(macd, signal)\n\nharskiftetdag = hour(time[confirmationLength]) > hour(time)\n\nenterLongSignal = signalCrossover[confirmationLength] and (macd > signal) and (absDelta >= 0.08)\nexitLongSignal = signalCrossunder[confirmationLength] and (macd < signal)\n\nenterShortSignal = signalCrossunder[confirmationLength] and (macd < signal) and (absDelta >= 0.08)\nexitShortSignal = signalCrossover[confirmationLength] and (macd > signal)\n\n// Så er det tid til at købe noe\nqty = math.floor(strategy.equity / close)\n\nif time >= earliest and not harskiftetdag\n    if exitLongSignal \n        strategy.close("long")\n    else if enterLongSignal\n        strategy.close("short")\n        strategy.entry("long", strategy.long, qty = qty)\n\n    if exitShortSignal\n        strategy.close("short")\n    else if enterShortSignal\n        strategy.close("long")\n        strategy.entry("short", strategy.short, qty = qty)\n\n// Så er det tid til at vise noe\n\nplot(macd, color=color.blue)\nplot(signal, color=color.orange)\n\n// bgcolor(color = delta > 0.1 ? color.new(color.green, 90) : color.new(color.green, 100))\n// bgcolor(color = signalCrossover ? color.purple : signalCrossunder ? color.aqua : color.new(color.green, 100))\n\nhistogramColor = delta > 0 ? (previousDelta < delta ? up1 : up2) : (previousDelta > delta ? down1 : down2)\n\nplot(\n     delta,\n     style=plot.style_columns,\n     color=histogramColor\n     )'

class SM51251B5B0684C412(PinePortBase, IStrategy):
    source_id = "SM_51251b5b0684c412"
    source_file = '移动平均线金叉死叉交易策略Moving-Average-Crossover-MACD-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
