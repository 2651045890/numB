"""batch_012 port of 量化交易突破策略首时段ATR止损与EMA斜率优化策略-Quantitative-Breakout-Strategy-First-Hour-ATR-Stop-Loss-with-EMA-Slope-Optimization.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-29 00:00:00\nend: 2025-02-26 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("FnO Intraday Strategy with ATR SL, EMA Slope & Signals", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// INPUTS\natrPeriod      = input.int(14, "ATR Period")\natrMultiplier  = input.float(1.0, "ATR Stop Loss Multiplier", step=0.1)\ntargetPercent  = input.float(1.0, "Profit Target (%)", step=0.1) * 0.01\n\n// Define session start and first candle period (for Indian market, session starts at 09:15)\nsessionStartHour   = input.int(9, "Session Start Hour", minval=0, maxval=23)\nsessionStartMinute = input.int(15, "Session Start Minute", minval=0, maxval=59)\nfirstCandleMins    = 60  // First candle duration in minutes\n\n// Compute today\'s session start and first candle end timestamps\ncurrYear  = year(time)\ncurrMonth = month(time)\ncurrDay   = dayofmonth(time)\nsessionStartTS = timestamp(currYear, currMonth, currDay, sessionStartHour, sessionStartMinute)\nsessionEndTS   = sessionStartTS + firstCandleMins * 60 * 1000  // PineScript time is in ms\n\n// INITIALIZE first-hour high/low (reset at the start of each day)\nvar float firstHourHigh = na\nvar float firstHourLow  = na\nif (ta.change(time("D")))\n    firstHourHigh := na, firstHourLow := na\n\n// Update first-hour high/low while within the first candle period\nif (time >= sessionStartTS and time <= sessionEndTS)\n    firstHourHigh := na(firstHourHigh) ? high : math.max(firstHourHigh, high)\n    firstHourLow  := na(firstHourLow)  ? low  : math.min(firstHourLow, low)\n\n// Plot the first-hour high and low once the first candle period is over\nplot(time > sessionEndTS ? firstHourHigh : na, title="First Hour High", color=color.green, style=plot.style_linebr)\nplot(time > sessionEndTS ? firstHourLow  : na, title="First Hour Low",  color=color.red,   style=plot.style_linebr)\n\n// Calculate indicators: 9 EMA, VWAP, and EMA slope\nema9    = ta.ema(close, 9)\nvwapVal = ta.vwap(hlc3)  // Using typical price for VWAP calculation\nemaSlope = ema9 - ema9[1]\n\n// Define "first hour complete" flag so entries only occur after the first candle period\nfirstHourComplete = time > sessionEndTS\n\n// ENTRY CONDITIONS\n// Long: Price breaks above first-hour high, and 9 EMA crosses above VWAP with a positive slope.\nlongBreakout       = ta.crossover(close, firstHourHigh)\nlongEMAConfirmation = ta.crossover(ema9, vwapVal) and (emaSlope > 0)\nlongCondition      = firstHourComplete and longBreakout and longEMAConfirmation\n\n// Short: Price breaks below first-hour low, and 9 EMA crosses below VWAP with a negative slope.\nshortBreakout       = ta.crossunder(close, firstHourLow)\nshortEMAConfirmation = ta.crossunder(ema9, vwapVal) and (emaSlope < 0)\nshortCondition      = firstHourComplete and shortBreakout and shortEMAConfirmation\n\n// Generate entries\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Add buy and sell signals on the chart\nplotshape(longCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(shortCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Calculate ATR for dynamic stop loss\natrValue = ta.atr(atrPeriod)\n\n// Set exits using ATR-based stop loss and fixed profit target (1% gain)\nif (strategy.position_size > 0)\n    longStop   = strategy.position_avg_price - atrValue * atrMultiplier\n    longTarget = strategy.position_avg_price * (1 + targetPercent)\n    strategy.exit("Long Exit", from_entry="Long", stop=longStop, limit=longTarget)\nif (strategy.position_size < 0)\n    shortStop   = strategy.position_avg_price + atrValue * atrMultiplier\n    shortTarget = strategy.position_avg_price * (1 - targetPercent)\n    strategy.exit("Short Exit", from_entry="Short", stop=shortStop, limit=shortTarget)\n\n// Plot EMA and VWAP for visual confirmation\nplot(ema9, title="9 EMA", color=color.blue)\nplot(vwapVal, title="VWAP", color=color.orange)\n\n'

class SMATREMAQuantitativeBreakoutStrategyFirstHourATRStopLosswb3fd99(PinePortBase, IStrategy):
    source_id = "SM_b3fd99656b5a9462"
    source_file = '量化交易突破策略首时段ATR止损与EMA斜率优化策略-Quantitative-Breakout-Strategy-First-Hour-ATR-Stop-Loss-with-EMA-Slope-Optimization.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'atrPeriod': 14, 'atrMultiplier': 1.0, 'sessionStartHour': 9, 'sessionStartMinute': 15}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
