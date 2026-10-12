"""batch_011 port of 自适应趋势跟踪与多重确认交易策略Adaptive-Trend-Following-and-Multi-Confirmation-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-16 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Coral Tides Strategy", shorttitle="CoralTidesStrat", overlay=true)\n\n// === Inputs ===\ndlen = input.int(defval=20, title="Donchian Channel Period", minval=10)\ncoralPeriod = input.int(defval=14, title="Coral Trend Period")\n\n// === Functions ===\n// Coral Trend Calculation\ncoralTrend(period) =>\n    smooth = (high + low + close) / 3\n    coral = ta.ema(smooth, period)\n    trend = 0\n    trend := close > coral ? 1 : close < coral ? -1 : trend[1]\n    [trend, coral]\n\n// Donchian Trend Calculation\ndonchianTrend(len) =>\n    hh = ta.highest(high, len)\n    ll = ta.lowest(low, len)\n    trend = 0\n    trend := close > hh[1] ? 1 : close < ll[1] ? -1 : trend[1]\n    trend\n\n// === Trend Calculation ===\n[coralTrendVal, coralLine] = coralTrend(coralPeriod)\ndonchianTrendVal = donchianTrend(dlen)\n\n// === Signal Logic ===\nvar int trendState = 0\nbuySignal = false\nsellSignal = false\n\nif (coralTrendVal == 1 and donchianTrendVal == 1 and trendState != 1)\n    buySignal := true\n    sellSignal := false\n    trendState := 1\nelse if (coralTrendVal == -1 and donchianTrendVal == -1 and trendState != -1)\n    sellSignal := true\n    buySignal := false\n    trendState := -1\nelse\n    buySignal := false\n    sellSignal := false\n\n// === Strategy Execution ===\n// Entry Signals\nif (buySignal)\n    strategy.entry("Long", strategy.long)\nif (sellSignal)\n    strategy.entry("Short", strategy.short)\n\n// === Plots ===\n// Coral Trend Line\nplot(coralLine, color=color.green, linewidth=2, title="Coral Trend Line")\n\n// Buy/Sell Signal Labels\nif buySignal\n    label.new(bar_index, low, "BUY", color=color.green, textcolor=color.white, style=label.style_label_down, size=size.normal)\nif sellSignal\n    label.new(bar_index, high, "SELL", color=color.red, textcolor=color.white, style=label.style_label_up, size=size.normal)\n'

class SM3F1E3E43C5457351(PinePortBase, IStrategy):
    source_id = "SM_3f1e3e43c5457351"
    source_file = '自适应趋势跟踪与多重确认交易策略Adaptive-Trend-Following-and-Multi-Confirmation-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'dlen': 20, 'coralPeriod': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'tuple', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
