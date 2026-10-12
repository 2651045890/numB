"""batch_011 port of 自适应布林通道动态仓位管理策略-Adaptive-Bollinger-Bands-Dynamic-Position-Management-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-11 00:00:00\nend: 2024-12-10 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bollinger Bands Strategy", overlay=true)\n\n// 設定布林通道\nlength = 20\nsource = close\nmult = 2.0\nbasis = ta.sma(source, length)\ndev = mult * ta.stdev(source, length)\nupper = basis + dev\nlower = basis - dev\n\n// 畫出布林通道\nplot(upper, color=color.red, linewidth=1)\nplot(basis, color=color.blue, linewidth=1)\nplot(lower, color=color.green, linewidth=1)\n\n// 設定買入條件：突破布林通道高點5%或持續1小時在高點上方\nbreakout_level = upper * 1.01\n\nhour_breakout = ta.change(time("60")) == 1 and close > upper\n\nbuy_condition = (close > breakout_level or hour_breakout)\nif (buy_condition)\n    strategy.entry("Buy", strategy.long, qty=0.5)\n\n// 設定賣出條件：第一次回測中線、跌破低點5%或回升中線\nsell_10_condition = ta.crossover(close, basis) and strategy.opentrades > 0\nsell_50_condition = close < lower * 0.95\n\n// 賣出10%現貨\nif (sell_10_condition)\n    strategy.close("Buy", qty=0.1)\n\n// 賣出50%現貨\nif (sell_50_condition)\n    strategy.close("Buy", qty=0.5)\n\n// 監控買入與賣出信號\nplotshape(series=buy_condition, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal")\nplotshape(series=sell_10_condition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell 10% Signal")\nplotshape(series=sell_50_condition, location=location.abovebar, color=color.blue, style=shape.labeldown, title="Sell 50% Signal")\n'

class SM45851A0B618E4287(PinePortBase, IStrategy):
    source_id = "SM_45851a0b618e4287"
    source_file = '自适应布林通道动态仓位管理策略-Adaptive-Bollinger-Bands-Dynamic-Position-Management-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
