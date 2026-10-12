"""batch_012 port of 追踪金本位价值的动态移动平均线策略Daily-Moving-Average-Tracking-Strategy-for-Gold-Value.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-04 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("My Strategy", overlay=true)\n\n// Inputs for user to modify\nstartHour = input(11, title="Start Hour")\nendHour = input(16, title="End Hour")\ntrailingStop = input(100, title="Trailing Stop Start (pips)")\ntrailingStep = input(10, title="Trailing Step (pips)")\n\n// Define the EMAs\nlongEma = ema(close, 200)\nshortEma = ema(close, 50)\n\n// Calculate daily open, high, low, close\ndaily_open = security(syminfo.tickerid, "D", open[1])\ndaily_close = security(syminfo.tickerid, "D", close[1])\n\n// Time conditions\ntimeAllowed = (hour >= startHour) and (hour <= endHour)\n\n// Define long condition based on your criteria\nlongCondition = (daily_close > daily_open) and (close > daily_open) and (shortEma > longEma) and timeAllowed\n\n// Define short condition based on your criteria\nshortCondition = (daily_close < daily_open) and (close < daily_open) and (shortEma < longEma) and timeAllowed\n\n// Enter the trade\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Trailing Stop Loss\nstrategy.exit("Exit Long", "Long", trail_points = trailingStop / syminfo.mintick, trail_offset = trailingStep / syminfo.mintick)\nstrategy.exit("Exit Short", "Short", trail_points = trailingStop / syminfo.mintick, trail_offset = trailingStep / syminfo.mintick)\n\n// Plotting\nplot(daily_open, color=color.red, title="Daily Open")\nplot(longEma, color=color.blue, title="200 EMA")\nplot(shortEma, color=color.orange, title="50 EMA")\n\n'

class SMDailyMovingAverageTrackingStrategyforGoldValuea5611e(PinePortBase, IStrategy):
    source_id = "SM_a5611edf755ceb4d"
    source_file = '追踪金本位价值的动态移动平均线策略Daily-Moving-Average-Tracking-Strategy-for-Gold-Value.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'startHour': 11, 'endHour': 16, 'trailingStop': 100, 'trailingStep': 10}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
