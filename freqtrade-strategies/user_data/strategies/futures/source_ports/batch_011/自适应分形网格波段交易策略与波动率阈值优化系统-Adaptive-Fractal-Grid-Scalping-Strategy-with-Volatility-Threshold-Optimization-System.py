"""batch_011 port of 自适应分形网格波段交易策略与波动率阈值优化系统-Adaptive-Fractal-Grid-Scalping-Strategy-with-Volatility-Threshold-Optimization-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-17 00:00:00\nend: 2025-02-15 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Adaptive Fractal Grid Scalping Strategy", overlay=true)\n\n// Inputs\natrLength = input.int(14, title="ATR Length")\nsmaLength = input.int(50, title="SMA Length")\ngridMultiplierHigh = input.float(2.0, title="Grid Multiplier High")\ngridMultiplierLow = input.float(0.5, title="Grid Multiplier Low")\ntrailStopMultiplier = input.float(0.5, title="Trailing Stop Multiplier")\nvolatilityThreshold = input.float(1.0, title="Volatility Threshold (ATR)")\n\n// Calculate Fractals\nfractalHigh = ta.pivothigh(high, 2, 2)\nfractalLow = ta.pivotlow(low, 2, 2)\n\n// Calculate ATR and SMA\natrValue = ta.atr(atrLength)\nsmaValue = ta.sma(close, smaLength)\n\n// Determine Trend Direction\nisBullish = close > smaValue\nisBearish = close < smaValue\n\n// Calculate Grid Levels\ngridLevelHigh = fractalHigh + atrValue * gridMultiplierHigh\ngridLevelLow = fractalLow - atrValue * gridMultiplierLow\n\n// Plot Fractals and Grid Levels\nplotshape(not na(fractalHigh), style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)\nplotshape(not na(fractalLow), style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)\nplot(gridLevelHigh, color=color.red, linewidth=1, title="Grid Level High")\nplot(gridLevelLow, color=color.green, linewidth=1, title="Grid Level Low")\n\n// Trade Execution Logic with Volatility Threshold\nif (atrValue > volatilityThreshold)\n    if (isBullish and not na(fractalLow))\n        strategy.entry("Buy", strategy.long, limit=gridLevelLow)\n    if (isBearish and not na(fractalHigh))\n        strategy.entry("Sell", strategy.short, limit=gridLevelHigh)\n\n// Profit-Taking and Stop-Loss\nstrategy.exit("Take Profit/Stop Loss", "Buy", limit=gridLevelHigh, stop=fractalLow - atrValue * trailStopMultiplier)\nstrategy.exit("Take Profit/Stop Loss", "Sell", limit=gridLevelLow, stop=fractalHigh + atrValue * trailStopMultiplier)'

class SMD6D27FC42BB73D9C(PinePortBase, IStrategy):
    source_id = "SM_d6d27fc42bb73d9c"
    source_file = '自适应分形网格波段交易策略与波动率阈值优化系统-Adaptive-Fractal-Grid-Scalping-Strategy-with-Volatility-Threshold-Optimization-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atrLength': 14, 'smaLength': 50, 'gridMultiplierHigh': 2.0, 'gridMultiplierLow': 0.5, 'trailStopMultiplier': 0.5, 'volatilityThreshold': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
