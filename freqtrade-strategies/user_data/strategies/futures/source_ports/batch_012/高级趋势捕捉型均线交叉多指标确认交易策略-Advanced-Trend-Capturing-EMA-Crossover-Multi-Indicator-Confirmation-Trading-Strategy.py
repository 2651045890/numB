"""batch_012 port of 高级趋势捕捉型均线交叉多指标确认交易策略-Advanced-Trend-Capturing-EMA-Crossover-Multi-Indicator-Confirmation-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-02-18 00:00:00\nend: 2025-02-25 00:00:00\nperiod: 10m\nbasePeriod: 10m\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized BTC/USD Scalping", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// --- Indicator Parameters ---\nema_fast = ta.ema(close, 9)\nema_slow = ta.ema(close, 21)\nsma_trend = ta.sma(close, 200)\nrsi_value = ta.rsi(close, 14)\n\n// --- Bollinger Bands Definition ---\n[bb_upper, bb_middle, bb_lower] = ta.bb(close, 20, 2)\n\n// --- Trading Parameters ---\ntake_profit_multiplier = 2.0\nstop_loss_multiplier = 1.0\natr_value = ta.atr(14)\n\n// --- Entry Conditions ---\nlongCondition = ta.crossover(ema_fast, ema_slow) and close > sma_trend and rsi_value > 50 and close > bb_middle\nshortCondition = ta.crossunder(ema_fast, ema_slow) and close < sma_trend and rsi_value < 50 and close < bb_middle\n\n// --- Define TP and SL ---\nlong_sl = close - atr_value * stop_loss_multiplier\nlong_tp = close + atr_value * take_profit_multiplier\nshort_sl = close + atr_value * stop_loss_multiplier\nshort_tp = close - atr_value * take_profit_multiplier\n\n// --- Execute Trades ---\nif longCondition\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit Long", from_entry="Long", limit=long_tp, stop=long_sl)\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Take Profit Short", from_entry="Short", limit=short_tp, stop=short_sl)\n\n// --- Fix for plotshape issue ---\nplot_buy_signal = longCondition ? 1 : na\nplot_sell_signal = shortCondition ? 1 : na\n\nplotshape(series=plot_buy_signal, location=location.belowbar, color=color.green, style=shape.labelup, title="BUY")\nplotshape(series=plot_sell_signal, location=location.abovebar, color=color.red, style=shape.labeldown, title="SELL")\n\n\n'

class SMAdvancedTrendCapturingEMACrossoverMultiIndicatorConfirm410a94(PinePortBase, IStrategy):
    source_id = "SM_410a94eba6696052"
    source_file = '高级趋势捕捉型均线交叉多指标确认交易策略-Advanced-Trend-Capturing-EMA-Crossover-Multi-Indicator-Confirmation-Trading-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
