"""batch_011 port of 趋势跟随可变仓位网格策略-Trend-Following-Variable-Position-Grid-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © niosupetranmartinez\n//@version=5\nstrategy("Trend Follower Scalping Strategy", overlay=true, process_orders_on_close = true)\n\n// Inputs\nemaLen = input(200, \'EMA Length\')\nrsiLen = input(9, \'RSI Length\')\ntrendDirection = input.string("Both", \'Trend Direction\', options=["Long Only", "Short Only", "Both"])\nrisk_reward_ratio = input(2, \'Risk Reward Ratio\')\nuseMacdFilter = input.bool(true, "Use MACD Filter")\nmacdTimeframe = input("5", "MACD Timeframe")\n\n// EMA and RSI\nema200 = ta.ema(close, emaLen)\ncustomRsi = ta.rsi(close, rsiLen)\n\n// MACD Filter\n[macdLine, signalLine, _] = request.security(syminfo.tickerid, macdTimeframe, ta.macd(close, 12, 26, 9))\n\n\n// Majority Body Candle Identification Function\nisMajorityBodyCandle(candleOpen, candleClose, high, low) =>\n    bodySize = math.abs(candleClose - candleOpen)\n    fullSize = high - low\n    bodySize / fullSize > 0.6\n\n// Engulfing Patterns\nisBullishEngulfing = close > open and close[1] < open[1] and (close - open) > (open[1] - close[1]) and isMajorityBodyCandle(open, close, high, low)\nisBearishEngulfing = close < open and close[1] > open[1] and (open - close) > (close[1] - open[1]) and isMajorityBodyCandle(open, close, high, low)\n\n// Entry Conditions with MACD Filter\nlongCondition = close > ema200 and customRsi > 50 and isBullishEngulfing and (not useMacdFilter or macdLine > signalLine)\nshortCondition = close < ema200 and customRsi < 50 and isBearishEngulfing and (not useMacdFilter or macdLine < signalLine)\n\n// Trade Execution\nvar float stopLossPrice = na\nvar float entryPrice = na\n\n// Long Entry\nif (longCondition and (trendDirection == "Long Only" or trendDirection == "Both"))\n    entryPrice := close\n    engulfingBodySize = math.abs(close - open)\n    minimumStopLoss = entryPrice * 0.997\n    calculatedStopLoss = entryPrice - (engulfingBodySize * 2)\n    stopLossPrice := calculatedStopLoss < minimumStopLoss ? calculatedStopLoss : minimumStopLoss\n    risk = entryPrice - stopLossPrice\n    takeProfitPrice = entryPrice + (risk_reward_ratio * risk)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", "Long", stop = stopLossPrice, limit = takeProfitPrice)\n\n// Short Entry\nif (shortCondition and (trendDirection == "Short Only" or trendDirection == "Both"))\n    entryPrice := close\n    engulfingBodySize = math.abs(open - close)\n    minimumStopLoss = entryPrice * 1.003\n    calculatedStopLoss = entryPrice + (engulfingBodySize * 2)\n    stopLossPrice := calculatedStopLoss > minimumStopLoss ? calculatedStopLoss : minimumStopLoss\n    risk = stopLossPrice - entryPrice\n    takeProfitPrice = entryPrice - (risk_reward_ratio * risk)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", "Short", stop = stopLossPrice, limit = takeProfitPrice)\n\n// Plotting\nplot(ema200, color=color.blue, linewidth=2, title="EMA 200")'

class SM563864141A1E1803(PinePortBase, IStrategy):
    source_id = "SM_563864141a1e1803"
    source_file = '趋势跟随可变仓位网格策略-Trend-Following-Variable-Position-Grid-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'emaLen': 200, 'rsiLen': 9, 'trendDirection': 'Both', 'risk_reward_ratio': 2, 'useMacdFilter': True, 'macdTimeframe': '5'}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'func', 'tuple', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
