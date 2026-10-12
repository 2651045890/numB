"""batch_012 port of 首个蜡烛突破-止损或收盘自动平仓策略-First-Candle-Breakout-with-Stop-Loss-or-End-of-Day-Closing-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-03-28 00:00:00\nend: 2025-03-31 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("First Candle Breakout - Close on SL or EOD", overlay=true)\n\n// User Inputs\nstartHour = input(9, "Start Hour (Exchange Time)")\nstartMinute = input(15, "Start Minute (Exchange Time)")\nendHour = input(15, "End Hour (Exchange Time)")  // Market closing hour\nendMinute = input(30, "End Minute (Exchange Time)")\n\n// Variables to store the first candle\'s high & low\nvar float firstCandleHigh = na\nvar float firstCandleLow = na\nvar bool tradeTaken = false  // Ensures only one trade per day\nvar int tradeDirection = 0   // 1 for long, -1 for short\n\n// Identify first candle\'s high & low\nif (hour == startHour and minute == startMinute and bar_index > 1)\n    firstCandleHigh := high\n    firstCandleLow := low\n    tradeTaken := false  // Reset trade flag at start of day\n    tradeDirection := 0   // Reset trade direction\n\n// Buy condition: Close above first candle high AFTER the first candle closes\nlongCondition = not na(firstCandleHigh) and close > firstCandleHigh and not tradeTaken and hour > startHour\nif (longCondition)\n    strategy.entry("Buy", strategy.long, comment="Buy")\n    tradeTaken := true  // Mark trade as taken\n    tradeDirection := 1  // Mark trade as long\n\n// Sell condition: Close below first candle low AFTER the first candle closes\nshortCondition = not na(firstCandleLow) and close < firstCandleLow and not tradeTaken and hour > startHour\nif (shortCondition)\n    strategy.entry("Sell", strategy.short, comment="Sell")\n    tradeTaken := true  // Mark trade as taken\n    tradeDirection := -1  // Mark trade as short\n\n// Stop loss for long trades (first candle low)\nif (tradeDirection == 1 and close <= firstCandleLow)\n    strategy.close("Buy", comment="SL Hit")\n\n// Stop loss for short trades (first candle high)\nif (tradeDirection == -1 and close >= firstCandleHigh)\n    strategy.close("Sell", comment="SL Hit")\n\n// Close trade at end of day if still open\nif (tradeTaken and hour == endHour and minute == endMinute)\n    strategy.close_all(comment="EOD Close")\n\n'

class SMFirstCandleBreakoutwithStopLossorEndofDayClosingStrategea8d90(PinePortBase, IStrategy):
    source_id = "SM_ea8d907f1e7f2d86"
    source_file = '首个蜡烛突破-止损或收盘自动平仓策略-First-Candle-Breakout-with-Stop-Loss-or-End-of-Day-Closing-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'startHour': 9, 'startMinute': 15, 'endMinute': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
