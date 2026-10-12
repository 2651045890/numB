"""batch_011 port of 自适应趋势跟踪多周期ATR动态阈值做空策略-Adaptive-Trend-Following-Multi-Period-ATR-Dynamic-Threshold-Short-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 2d\nbasePeriod: 2d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("[SHORT ONLY] ATR Sell the Rip Mean Reversion Strategy", overlay=true, initial_capital = 1000000, default_qty_value = 100, default_qty_type = strategy.percent_of_equity, process_orders_on_close = true, margin_long = 5, margin_short = 5, calc_on_every_tick = true, fill_orders_on_standard_ohlc = true)\n\n//#region INPUTS SECTION\n// ============================================\n\n// ============================================\n// Strategy Settings\n// ============================================\natrPeriod = input.int(title="ATR Period", defval=20, minval=1, group="Strategy Settings")\natrMultInput = input.float(title=\'ATR Multiplier\', defval=1.0, step=0.25, group="Strategy Settings")\nsmoothPeriodInput = input.int(title=\'Smoothing Period\', defval=10, minval=1, group="Strategy Settings")\n//#endregion\n\n// ============================================\n// EMA Filter Settings\n// ============================================\nuseEmaFilter = input.bool(true, "Use EMA Filter", group="Trend Filter")\nemaPeriodInput = input.int(200, "EMA Period", minval=1, group="Trend Filter")\n\n//#region INDICATOR CALCULATIONS\n// ============================================\n// Calculate ATR Signal Trigger\n// ============================================\natrValue = ta.atr(atrPeriod)\natrThreshold = close + atrValue * atrMultInput\nsignalTrigger = ta.sma(atrThreshold, smoothPeriodInput)\n\nplot(signalTrigger, title="Smoothed ATR Trigger", color=color.white)\n\n// ============================================\n// Trend Filter\n// ============================================\nma200 = ta.ema(close, emaPeriodInput)\nplot(ma200, color=color.red, force_overlay=true)\n\n//#region TRADING CONDITIONS\n// ============================================\n// Entry/Exit Logic\n// ============================================\nshortCondition = close>signalTrigger\nexitCondition = close<low[1]\n\n// Apply EMA Filter if enabled\nif useEmaFilter\n    shortCondition := shortCondition and close < ma200\n//#endregion\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\nif exitCondition\n    strategy.close_all()'

class SM446E3AD9E2B61D22(PinePortBase, IStrategy):
    source_id = "SM_446e3ad9e2b61d22"
    source_file = '自适应趋势跟踪多周期ATR动态阈值做空策略-Adaptive-Trend-Following-Multi-Period-ATR-Dynamic-Threshold-Short-Strategy.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'atrPeriod': 20, 'atrMultInput': 1.0, 'smoothPeriodInput': 10, 'useEmaFilter': True, 'emaPeriodInput': 200}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
