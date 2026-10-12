"""batch_011 port of 趋势突破策略ATR-Trend-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-16 00:00:00\nend: 2024-03-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title = "Claw-Pattern", overlay=true, calc_on_every_tick=true, default_qty_type= strategy.percent_of_equity,default_qty_value=10, currency="USD")\n//Developer: Trading Strategy Guides\n//Creator: Trading Strategy Guides\n//Date: 3/18/2024\n//Description: A trend trading system strategy \n\natr_period = input(title="ATR Period", defval=120, type=input.integer)\natr_mult = input(title="ATR Multiplier", defval=2, type=input.integer)\ndir = input(title="Direction (Long=1, Short=-1, Both = 0)", defval=1, type=input.integer)\nfactor = input(title="Stop Level Deviation (% Chan.)", defval=0.75, type=input.float)\nrr = input(title="Reward to Risk Multiplier", defval=2, type=input.integer)\ntrail_bar_start = input(title="Trail Stop Bar Start", defval=20, type=input.integer)\ncol_candles = input(title="Enable Colored Candles", defval=false, type=input.bool)\n\natr_signal = atr(atr_period)\n\nlower_trend = low - atr_mult*atr_signal\nupper_trend = high + atr_mult*atr_signal\n\nupper_trend := upper_trend > upper_trend[1] and close < upper_trend[1] ? upper_trend[1] : upper_trend\nlower_trend := lower_trend < lower_trend[1] and close > lower_trend[1] ? lower_trend[1] : lower_trend\n\nupper_color = barssince(cross(close, upper_trend[1])) > barssince(cross(close, lower_trend[1])) ? color.red : na\nlower_color = barssince(cross(close, upper_trend[1])) > barssince(cross(close, lower_trend[1])) ? na : color.green\n\ntrend_line = lower_trend\n\nplot(lower_trend, color=lower_color, title="Lower Trend Color")\nplot(upper_trend, color=upper_color, title="Upper Trend Color")\n\nis_buy = strategy.position_size == 0 and crossover(close, upper_trend[1]) and upper_color[1]==color.red and (dir == 1 or dir == 0)\nis_sell = strategy.position_size == 0 and crossover(close, lower_trend[1]) and lower_color[1]==color.green and (dir == -1 or dir == 0)\n\nif is_buy\n    strategy.entry("Enter Long", strategy.long)\nelse if is_sell\n    strategy.entry("Enter Short", strategy.short)'

class SM3B3553EAB042A7E2(PinePortBase, IStrategy):
    source_id = "SM_3b3553eab042a7e2"
    source_file = '趋势突破策略ATR-Trend-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'atr_period': 120, 'atr_mult': 2, 'dir': 1, 'factor': 0.75, 'rr': 2, 'trail_bar_start': 20, 'col_candles': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
