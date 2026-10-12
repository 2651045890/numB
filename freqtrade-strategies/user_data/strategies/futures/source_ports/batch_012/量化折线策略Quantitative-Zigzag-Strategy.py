"""batch_012 port of 量化折线策略Quantitative-Zigzag-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-14 00:00:00\nend: 2023-11-20 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Gentleman-Goat\n\n//@version=5\nstrategy("Sine Wave Theory",overlay=false, precision = 2, initial_capital = 1000,shorttitle = "SINE_W_T")\n\nvar bar_change_wave_direction = input.int(defval=1,title="Starting Wave Direction",group="Bar Change")\nbar_change_sine_wave_number = input.int(defval=28,title="Sine Wave #",group="Bar Change")\nbar_change_sine_wave_res = input.timeframe(defval="D",title="Resolution",group="Bar Change")\nbar_change_trade = input.bool(defval=true,title="Trade",group="Bar Change")\n\nvar volume_wave_direction = input.int(defval=1,title="Starting Wave Direction",group="Volume")\navg_volume_length = input.int(7,title="Lookback Length",group="Volume")\nvolume_sine_wave_number = input.int(defval=28,title="Sine Wave #",group="Volume")\nvolume_sine_wave_res = input.timeframe(defval="D",title="Resolution",group="Volume")\nvolume_trade = input.bool(defval=false,title="Trade",group="Volume")\n\nvar coin_flip_wave_direction = input.int(defval=1,title="Starting Wave Direction",group="Coin Flip")\ncoin_flip_sine_wave_number = input.int(defval=28,title="Sine Wave #",group="Coin Flip")\ncoin_flip_seed = input.int(defval=1,title="Seed #",group="Coin Flip")\ncoin_flip_trade = input.bool(defval=false,title="Trade",group="Coin Flip")\n\navg_volume = ta.sma(volume,avg_volume_length)\n\n//Green or Red Candle\nbar_color = close>open ? color.green : color.red\nbar_color_time_adj = request.security(syminfo.tickerid, bar_change_sine_wave_res, bar_color)\n\n//Above or Below Average\nvolume_state = (volume>avg_volume) ? color.blue : color.purple\nvolume_state_time_adj = request.security(syminfo.tickerid, volume_sine_wave_res, volume_state)\n \n//Coinflip\ncoin_flip = math.random(0,100,coin_flip_seed)>=50 ? color.teal : color.yellow\n\nvar bar_change_wave_count = 0\nvar volume_wave_count = 0\nvar coin_flip_wave_count = 0\n\n//Wave Counters\nif(volume_state_time_adj[1] != volume_state_time_adj)\n    volume_wave_count := volume_wave_count + volume_wave_direction\n\nif(bar_color_time_adj[1] != bar_color_time_adj)\n    bar_change_wave_count := bar_change_wave_count + bar_change_wave_direction\n\nif(coin_flip[1] != coin_flip)\n    coin_flip_wave_count := coin_flip_wave_count + coin_flip_wave_direction\n\n//Direction changers\nif(math.abs(bar_change_wave_count) == bar_change_sine_wave_number and bar_color_time_adj[1] != bar_color_time_adj)\n    bar_change_wave_direction := bar_change_wave_direction * -1\n\nif(math.abs(volume_wave_count) == volume_sine_wave_number and volume_state_time_adj[1] != volume_state_time_adj)\n    volume_wave_direction := volume_wave_direction * -1\n\nif(math.abs(coin_flip_wave_count) == coin_flip_sine_wave_number and coin_flip[1] != coin_flip)\n    coin_flip_wave_direction := coin_flip_wave_direction * -1\n\n//Entry positions\nif(bar_change_wave_count==bar_change_sine_wave_number and bar_change_trade==true)\n    strategy.entry(id="short",direction=strategy.short)\nif(bar_change_wave_count==bar_change_sine_wave_number*-1 and bar_change_trade==true)\n    strategy.entry(id="long",direction=strategy.long)\n\nif(volume_wave_count==volume_sine_wave_number and volume_trade==true)\n    strategy.entry(id="short-volume",direction=strategy.short)\nif(volume_wave_count==volume_sine_wave_number*-1 and volume_trade==true)\n    strategy.entry(id="long-volume",direction=strategy.long)\n\nif(coin_flip_wave_count==coin_flip_sine_wave_number and coin_flip_trade==true)\n    strategy.entry(id="short-coinflip",direction=strategy.short)\nif(coin_flip_wave_count==coin_flip_sine_wave_number*-1 and coin_flip_trade==true)\n    strategy.entry(id="long-coinflip",direction=strategy.long)\n\nhline(0, title=\'Center\', color=color.white, linestyle=hline.style_dashed, linewidth=1)\nplot(bar_change_wave_count,title="Bar Change", color=bar_color, linewidth=2)\nplot(volume_wave_count,title="Volume Average Change", color=volume_state, linewidth=2)\nplot(coin_flip_wave_count,title="Coin Flip Change", color=coin_flip, linewidth=2)\n\n'

class SMQuantitativeZigzagStrategy93fd72(PinePortBase, IStrategy):
    source_id = "SM_93fd72f78c24e2c3"
    source_file = '量化折线策略Quantitative-Zigzag-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'bar_change_wave_direction': 1, 'bar_change_sine_wave_number': 28, 'bar_change_sine_wave_res': 'D', 'bar_change_trade': True, 'volume_wave_direction': 1, 'avg_volume_length': 7, 'volume_sine_wave_number': 28, 'volume_sine_wave_res': 'D', 'volume_trade': False, 'coin_flip_wave_direction': 1, 'coin_flip_sine_wave_number': 28, 'coin_flip_seed': 1, 'coin_flip_trade': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
