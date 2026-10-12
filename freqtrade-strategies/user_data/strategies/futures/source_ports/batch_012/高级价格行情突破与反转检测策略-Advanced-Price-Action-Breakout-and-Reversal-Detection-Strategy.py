"""batch_012 port of 高级价格行情突破与反转检测策略-Advanced-Price-Action-Breakout-and-Reversal-Detection-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-03 00:00:00\nend: 2024-08-03 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// Pine Script v5 – Price Action Trading Bot for EUR/USD on 15m timeframe\n//@version=5\nstrategy("Price Action Bot - EUR/USD", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=2)\n\n// === INPUTS ===\nriskRewardRatio = input.float(3.0, "Risk/Reward Ratio", minval=1.0)\nstopLossPips = input.float(10, "Stop Loss (pips)", minval=1)\ntrailingStop = input.bool(true, "Enable Trailing Stop")\nnewsFilter = input.bool(true, "Disable Trading During High Impact News")\n\n// === TIME FILTER FOR NEWS ===\n// Placeholder for news filter logic (needs manual adjustment or external integration)\nallowTrade = hour != 13 and hour != 14  // Avoiding possible news hours (example: 13:00–14:59 UTC)\n\n// === PRICE ACTION SIGNALS ===\nbullishPinBar = close > open and (high - close) > 2 * (close - open)\nbearishPinBar = open > close and (close - low) > 2 * (open - close)\n\nbullBreakout = close > ta.highest(close[1], 5)\nbearBreakout = close < ta.lowest(close[1], 5)\n\n// === ENTRY CONDITIONS ===\nlongCondition = allowTrade and (bullishPinBar or bullBreakout)\nshortCondition = allowTrade and (bearishPinBar or bearBreakout)\n\n// === TRADE EXECUTION ===\npip = syminfo.mintick * 10\nsl = stopLossPips * pip\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("TP/SL", "Long", stop=close - sl, limit=close + (sl * riskRewardRatio), trail_points=trailingStop ? sl/2 : na)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("TP/SL", "Short", stop=close + sl, limit=close - (sl * riskRewardRatio), trail_points=trailingStop ? sl/2 : na)\n\n// === PLOT SIGNALS ===\nplotshape(longCondition, location=location.belowbar, color=color.green, style=shape.triangleup, title="Buy Signal")\nplotshape(shortCondition, location=location.abovebar, color=color.red, style=shape.triangledown, title="Sell Signal")\n\n'

class SMAdvancedPriceActionBreakoutandReversalDetectionStrategyb5b15f(PinePortBase, IStrategy):
    source_id = "SM_b5b15f7c94e6eaa5"
    source_file = '高级价格行情突破与反转检测策略-Advanced-Price-Action-Breakout-and-Reversal-Detection-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'riskRewardRatio': 3.0, 'stopLossPips': 10, 'trailingStop': True, 'newsFilter': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 2
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
