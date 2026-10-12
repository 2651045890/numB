"""batch_012 port of 高频动态开盘区间突破交易策略-Dynamic-Opening-Range-Breakout-High-Frequency-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-21 00:00:00\nend: 2025-01-24 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Binance","currency":"DOGE_USDT"}]\nargs: [["MaxCacheLen",580,358374]]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © UKFLIPS69\n\n//@version=6\nstrategy("ORB", overlay=true, fill_orders_on_standard_ohlc = true)\n\ntrade_on_monday = input(false, "Trade on Monday") \ntrade_on_tuesday = input(true, "Trade on Tuesday") \ntrade_on_wednesday = input(true, "Trade on Wednesday")\ntrade_on_thursday = input(false, "Trade on Thursday")\ntrade_on_friday = input(true, "Trade on Friday")\n// Get the current day of the week (1=Monday, ..., 6=Saturday, 0=Sunday)\ncurrent_day = dayofweek(time) \ncurrent_price = request.security(syminfo.tickerid, "1", close)\n// Define trading condition based on the day of the week\nis_trading_day = (trade_on_monday and current_day == dayofweek.monday) or\n                 (trade_on_tuesday and current_day == dayofweek.tuesday) or\n                 (trade_on_wednesday and current_day == dayofweek.wednesday) or\n                 (trade_on_thursday and current_day == dayofweek.thursday) or\n                 (trade_on_friday and current_day == dayofweek.friday)\n// ─── Persistent variables ─────────────────────────\nvar line  orHighLine       = na   // reference to the drawn line for the OR high\nvar line  orLowLine        = na   // reference to the drawn line for the OR low\nvar float orHigh           = na   // stores the open-range high\nvar float orLow            = na   // stores the open-range low\nvar int   barIndex930      = na   // remember the bar_index at 9:30\nvar bool  rangeEstablished = false\nvar bool  tradeTakenToday  = false  // track if we\'ve opened a trade for the day\n\n// ─── Detect times ────────────────────────────────\nis930  = (hour(time, "America/New_York") == 9 and minute(time, "America/New_York") == 30)\nis945  = (hour(time, "America/New_York") == 9 and minute(time, "America/New_York") == 45)\n\n// Between 9:30 and 9:44 (inclusive of 9:30 bar, exclusive of 9:45)?\ninSession = (hour(time, "America/New_York") == 9 and minute(time, "America/New_York") >= 30 and minute(time, "America/New_York") < 45)\n\n// ─── Reset each day at 9:30 ─────────────────────\nif is930\n    // Reset orHigh / orLow\n    orHigh := na\n    orLow  := na\n    rangeEstablished := false\n    tradeTakenToday  := false\n    // Record the bar_index for 9:30\n    barIndex930 := bar_index\n// ─── ONLY FORM OR / TRADE IF TODAY IS ALLOWED ─────────────────────\nif is_trading_day\n// ─── Accumulate the OR high/low from 9:30 to 9:44 ─\n    if inSession\n        orHigh := na(orHigh) ? high : math.max(orHigh, high)\n        orLow  := na(orLow)  ? low  : math.min(orLow, low)\n\n// ─── Exactly at 9:45, draw the lines & lock range ─\n    if is945 and not na(orHigh) and not na(orLow)\n\n    // Mark that the OR is established\n        rangeEstablished := true\n\n// ─── TRADING LOGIC AFTER 9:45, but BEFORE NOON, and if NO trade taken ─\n    if rangeEstablished and not na(orHigh) and not na(orLow) \n    // Only trade if it\'s still BEFORE 12:00 (noon) EST and we haven\'t taken a trade today\n        if hour(time, "America/New_York") < 12 and (not tradeTakenToday)\n        // 1) Compute distances for stops & targets\n            float stopSize   = 0.5 * (orHigh - orLow)      // half the OR size\n            float targetSize = 3 * stopSize      // 3x the stop => 1.5x the entire OR\n    \n        // 2) Check if price breaks above OR => go long\n            if close > orHigh \n            // Only enter a new long if not already in a long position (optional)\n                if strategy.position_size <= 0\n                    strategy.entry("ORB Long", strategy.long)\n                    strategy.exit("Long Exit", from_entry = "ORB Long", stop = orHigh - stopSize, limit  = strategy.position_avg_price + targetSize)\n                // Flag that we\'ve taken a trade today\n                    tradeTakenToday := true\n    \n        // 3) Check if price breaks below OR => go short\n            if close < orLow \n            // Only enter a new short if not already in a short position (optional)\n                if strategy.position_size >= 0\n                    strategy.entry("ORB Short", strategy.short)\n                    strategy.exit("Short Exit", from_entry = "ORB Short", stop = orLow + stopSize, limit  = strategy.position_avg_price - targetSize)\n                // Flag that we\'ve taken a trade today\n                    tradeTakenToday := true\nif hour(time, "America/New_York") == 16 and minute(time, "America/New_York") == 0\n    strategy.close_all()\n\n'

class SMDynamicOpeningRangeBreakoutHighFrequencyTradingStrategye75b36(PinePortBase, IStrategy):
    source_id = "SM_e75b36944637beae"
    source_file = '高频动态开盘区间突破交易策略-Dynamic-Opening-Range-Breakout-High-Frequency-Trading-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'trade_on_monday': False, 'trade_on_tuesday': True, 'trade_on_wednesday': True, 'trade_on_thursday': False, 'trade_on_friday': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
