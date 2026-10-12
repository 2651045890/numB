"""batch_012 port of 黄金快速突破策略Breakout-Scalper-Catching-Trend-Changes-Quickly.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-17 00:00:00\nend: 2023-10-24 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Breakout Scalper", overlay=true)\n\nfast_window = input(title="Fast Window",  defval=13, minval=1)\nslow_window = input(title="Slow Window",  defval=52, minval=1)\ninstant_period = input(title="Instant Period",  defval=3, minval=1)\n\nfast_low = lowest(fast_window)\nfast_high = highest(fast_window)\nfast_mid = (fast_low + fast_high) / 2\n\nslow_low = lowest(slow_window)\nslow_high = highest(slow_window)\nslow_mid = (slow_low + slow_high) / 2\n\ninstant_price = ema(close, instant_period)\n\nplot(instant_price, title="Instant Price", color=black, transp=50)\nfp = plot(fast_mid, title="Fast Mid", color=green)\nsp = plot(slow_mid, title="Slow Mid", color=red)\nfill(fp, sp, color=(fast_mid > slow_mid ? green : red))\n\nis_buy_mode = (instant_price > fast_mid) and (fast_mid > slow_mid)\nis_sell_mode = (instant_price < fast_mid) and (fast_mid < slow_mid)\nentry_color = is_buy_mode ? green : (is_sell_mode ? red : na)\nexit_color = is_buy_mode ? red : (is_sell_mode ? green : na)\n\nentry_buy_stop = slow_high\nentry_sell_stop = slow_low\nexit_buy_stop = max(fast_low, slow_low)\nexit_sell_stop = min(fast_high, slow_high)\nstrategy.entry("long", strategy.long, stop=entry_buy_stop, when=is_buy_mode)\nstrategy.exit("stop", "long", stop=exit_buy_stop)\nstrategy.entry("short", strategy.short, stop=entry_sell_stop, when=is_sell_mode)\nstrategy.exit("stop", "short", stop=exit_sell_stop)\nstrategy.close("long", when=(not is_buy_mode))\nstrategy.close("short", when=(not is_sell_mode))\n\nentry_buy_stop_color = (strategy.position_size == 0) ? (is_buy_mode ? green : na) : na\nplotshape(entry_buy_stop, location=location.absolute, color=entry_buy_stop_color, style=shape.circle)\nentry_sell_stop_color = (strategy.position_size == 0) ? (is_sell_mode ? red : na) : na\nplotshape(entry_sell_stop, location=location.absolute, color=entry_sell_stop_color, style=shape.circle)\nexit_buy_stop_color = (strategy.position_size > 0) ? red : na\nplotshape(exit_buy_stop, location=location.absolute, color=exit_buy_stop_color, style=shape.xcross)\nexit_sell_stop_color = (strategy.position_size < 0) ? green : na\nplotshape(exit_sell_stop, location=location.absolute, color=exit_sell_stop_color, style=shape.xcross)\n\n'

class SMBreakoutScalperCatchingTrendChangesQuicklyb26abb(PinePortBase, IStrategy):
    source_id = "SM_b26abb21b0ef696c"
    source_file = '黄金快速突破策略Breakout-Scalper-Catching-Trend-Changes-Quickly.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'fast_window': 13, 'slow_window': 52, 'instant_period': 3}
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
