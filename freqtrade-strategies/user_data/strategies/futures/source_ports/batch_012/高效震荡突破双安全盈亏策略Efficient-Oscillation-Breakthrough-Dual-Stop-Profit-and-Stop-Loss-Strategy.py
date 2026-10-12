"""batch_012 port of 高效震荡突破双安全盈亏策略Efficient-Oscillation-Breakthrough-Dual-Stop-Profit-and-Stop-Loss-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-25 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Erweiterte SSL Channel Strategy mit 2 TPs, SL und BE", overlay=true)\n\nperiod = input(title="Period", defval=10)\nlen = input(title="Length", defval=10)\nmultiplier = input(title="Multiplier", defval=1.0, minval=1.0)\ntp1Percent = input(title="Take Profit 1 (%)", defval=1.0) / 100\ntp2Percent = input(title="Take Profit 2 (%)", defval=20.0) / 100\nslPercent = input(title="Stop Loss (%)", defval=3.0) / 100\n\nvar float tp1Price = na\nvar float tp2Price = na\nvar float slPrice = na\nvar bool tp1Reached = false\n\nsmaHigh = sma(high * multiplier, len)\nsmaLow = sma(low / multiplier, len)\n\nHlv = 0\nHlv := close > smaHigh ? 1 : close < smaLow ? -1 : nz(Hlv[1])\nsslDown = Hlv < 0 ? smaHigh : smaLow\nsslUp = Hlv < 0 ? smaLow : smaHigh\n\nplot(sslDown, linewidth=2, color=color.red)\nplot(sslUp, linewidth=2, color=color.lime)\n\nlongCondition = crossover(close, sslUp)\nshortCondition = crossunder(close, sslDown)\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    tp1Price := strategy.position_avg_price * (1 + tp1Percent)\n    tp2Price := strategy.position_avg_price * (1 + tp2Percent)\n    slPrice := strategy.position_avg_price * (1 - slPercent)\n    tp1Reached := false\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    tp1Price := strategy.position_avg_price * (1 - tp1Percent)\n    tp2Price := strategy.position_avg_price * (1 - tp2Percent)\n    slPrice := strategy.position_avg_price * (1 + slPercent)\n    tp1Reached := false\n\n// Take Profit, Break-even und Stop-Loss Logik\nif (strategy.position_size > 0) // Long-Positionen\n    if (not tp1Reached and close >= tp1Price)\n        strategy.close("Long", qty_percent = 50)\n        strategy.exit("BE Long", "Long", stop = strategy.position_avg_price)\n        tp1Reached := true\n    if (tp1Reached and close < tp1Price)\n        strategy.exit("BE Long", "Long", stop = strategy.position_avg_price)\n    if (close >= tp2Price)\n        strategy.close("Long", qty_percent = 100)\n    if (not tp1Reached)\n        strategy.exit("SL Long", "Long", stop = slPrice)\n\nif (strategy.position_size < 0) // Short-Positionen\n    if (not tp1Reached and close <= tp1Price)\n        strategy.close("Short", qty_percent = 50)\n        strategy.exit("BE Short", "Short", stop = strategy.position_avg_price)\n        tp1Reached := true\n    if (tp1Reached and close > tp1Price)\n        strategy.exit("BE Short", "Short", stop = strategy.position_avg_price)\n    if (close <= tp2Price)\n        strategy.close("Short", qty_percent = 100)\n    if (not tp1Reached)\n        strategy.exit("SL Short", "Short", stop = slPrice)\n\n'

class SMEfficientOscillationBreakthroughDualStopProfitandStopLo8b85a8(PinePortBase, IStrategy):
    source_id = "SM_8b85a8aa7d5e852c"
    source_file = '高效震荡突破双安全盈亏策略Efficient-Oscillation-Breakthrough-Dual-Stop-Profit-and-Stop-Loss-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'period': 10, 'len': 10, 'multiplier': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
