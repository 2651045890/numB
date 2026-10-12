"""batch_011 port of 自适应波动突破回撤交易策略-Adaptive-Volatility-Breakout-Retest-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2025-03-31 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("HFT Swing Bot", overlay=true)\n\n// Define 200 Moving Average\nma200 = ta.sma(close, 200)\n\n// Breakout confirmation (previous close above/below MA)\nbreakoutUp = ta.crossover(close, ma200)\nbreakoutDown = ta.crossunder(close, ma200)\n\n// Retest condition (price comes back to the 200MA after breakout)\nretestUp = breakoutUp and ta.lowest(low, 5) <= ma200\nretestDown = breakoutDown and ta.highest(high, 5) >= ma200\n\n// Entry conditions with confirmation candle\nlongCondition = breakoutUp and retestUp\nshortCondition = breakoutDown and retestDown\n\n// Adaptive SL & TP using ATR-based volatility\natr = ta.atr(14) // 14-period ATR for volatility adjustment\nriskFactor = input.float(1.0, "Risk Multiplier") // Adjust risk level for quick trades\n\n// Small SL and TP for quick profit capture\nlongSL = close - (atr * riskFactor) // Tight Stop Loss\nlongTP = close + (atr * riskFactor)  // Tight Take Profit\n\nshortSL = close + (atr * riskFactor) // Tight Stop Loss\nshortTP = close - (atr * riskFactor) // Tight Take Profit\n\n// Execute trades with adaptive SL/TP\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("LongExit", from_entry="Long", stop=longSL, limit=longTP)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("ShortExit", from_entry="Short", stop=shortSL, limit=shortTP)\n\n// Plot MA and signals\nplot(ma200, color=color.blue, linewidth=2, title="200 MA")\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="BUY")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="SELL")\n'

class SMED8ED853052512E8(PinePortBase, IStrategy):
    source_id = "SM_ed8ed853052512e8"
    source_file = '自适应波动突破回撤交易策略-Adaptive-Volatility-Breakout-Retest-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'riskFactor': 1.0}
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
