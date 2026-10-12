"""batch_011 port of 移动平均线交叉与动态波动率止损量化策略-Moving-Average-Crossover-with-Dynamic-Volatility-Based-Stop-Loss-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-02 00:00:00\nend: 2025-04-01 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=6\nstrategy(title=" VS-NTC> NASDQ100 Long MA+RSI+ATR", shorttitle="VS-NTC> Long NASDQ100 MA+RSI+ATR", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// ————— Inputs —————\nsmaLenShort  = input.int(50,  title="Short SMA Length")\nsmaLenLong   = input.int(200, title="Long SMA Length")\nrsiLen       = input.int(14,  title="RSI Length")\natrPeriod    = input.int(14,  title="ATR Period")\natrMult      = input.float(1.0, title="Stop-Loss ATR Multiplier", step=0.1)\nrrRatio      = input.float(1.5, title="Risk-to-Reward Ratio",    step=0.1)\n\n// ————— Indicator Calculations —————\nsmaShort = ta.sma(close, smaLenShort)\nsmaLong  = ta.sma(close, smaLenLong)\nrsiVal   = ta.rsi(close, rsiLen)\natrVal   = ta.atr(atrPeriod)\n\n// ————— Entry Conditions —————\n// Long Condition: 50SMA > 200SMA and RSI < 70\nlongCondition = (smaShort < smaLong) and (rsiVal > 30)\n// Short Condition: 50SMA < 200SMA and RSI > 30 (example: avoid oversold)\n// Or use RSI > 70 to short if the market is overbought.\nshortCondition = false\n// shortCondition = (smaShort > smaLong) and (rsiVal < 35)\n\n// ————— Entry Logic —————\nif longCondition\n    strategy.entry(id="Long", direction=strategy.long)\n\nif shortCondition\n    strategy.entry(id="Short", direction=strategy.short)\n\n// ————— Stop-Loss & Take-Profit Calculation —————\nvar float stopPrice       = na\nvar float takeProfitPrice = na\n\n// If we have a position open, we determine SL & TP differently for Long or Short.\nif strategy.position_size > 0\n    // We are in a Long trade\n    stopPrice       := strategy.position_avg_price - (atrVal * atrMult)\n    takeProfitPrice := strategy.position_avg_price + ((strategy.position_avg_price - stopPrice) * rrRatio)\n\n    strategy.exit("Exit SL/TP", stop=stopPrice, limit=takeProfitPrice)\nelse if strategy.position_size < 0\n    // We are in a Short trade\n    stopPrice       := strategy.position_avg_price + (atrVal * atrMult)\n    // For short, the distance from entry to stop is (stopPrice - entry)\n    // So the take-profit is entry - that same distance times RR\n    takeProfitPrice := strategy.position_avg_price - ((stopPrice - strategy.position_avg_price) * rrRatio)\n\n    strategy.exit("Exit SL/TP", stop=stopPrice, limit=takeProfitPrice)\nelse\n    // No open position → reset plots to na\n    stopPrice       := na\n    takeProfitPrice := na\n\n// ————— Plot the Planned Stop-Loss & Take-Profit —————\nplot(stopPrice,       title="Stop Loss",   color=color.red,   linewidth=2)\nplot(takeProfitPrice, title="Take Profit", color=color.green, linewidth=2)\n\n\n// ————— Label Each Closed Trade (Wins & Losses) —————\nvar int lastClosedTradeCount = 0\ncurrentClosedCount = strategy.closedtrades\n\n// If there\'s at least one new closed trade, label it\nif currentClosedCount > lastClosedTradeCount\n    newTradeIndex = currentClosedCount - 1\n\n    tradeProfit  = strategy.closedtrades.profit(newTradeIndex)\n    exitBarIndex = strategy.closedtrades.exit_bar_index(newTradeIndex)\n    exitPrice    = strategy.closedtrades.exit_price(newTradeIndex)\n\n    // Win label if profit > 0\n    if tradeProfit > 0\n        labelText  = "Win: " + str.tostring(tradeProfit)\n        labelStyle = label.style_label_up\n        labelColor = color.new(color.green, 0)\n        label.new(exitBarIndex, exitPrice, text=labelText, style=labelStyle, color=labelColor, size=size.tiny)\n\n    // Loss label if profit < 0\n    if tradeProfit < 0\n        labelText  = "Loss: " + str.tostring(tradeProfit)\n        labelStyle = label.style_label_down\n        labelColor = color.new(color.red, 0)\n        label.new(exitBarIndex, exitPrice, text=labelText, style=labelStyle, color=labelColor, size=size.tiny)\n\n    lastClosedTradeCount := currentClosedCount'

class SM95DC511F3EA4376D(PinePortBase, IStrategy):
    source_id = "SM_95dc511f3ea4376d"
    source_file = '移动平均线交叉与动态波动率止损量化策略-Moving-Average-Crossover-with-Dynamic-Volatility-Based-Stop-Loss-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'smaLenShort': 50, 'smaLenLong': 200, 'rsiLen': 14, 'atrPeriod': 14, 'atrMult': 1.0, 'rrRatio': 1.5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
