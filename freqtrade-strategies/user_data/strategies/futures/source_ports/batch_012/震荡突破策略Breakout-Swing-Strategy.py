"""batch_012 port of 震荡突破策略Breakout-Swing-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-20 00:00:00\nend: 2023-10-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\nstrategy("Advanced OutSide Forex strategy", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, calc_on_every_tick = true, commission_type = strategy.commission.percent, commission_value = 0.0)\n\nsv = change(hlc3) >= 0 ? volume : -volume\nkvo = ema(sv, 34) - ema(sv, 55)\nsig = ema(kvo, 13)\n\nlength = input(title="Length", type=input.integer, defval=27)\nsrc = input(close, title="Source")\nlsma = hma(src, length)\n\nif (high > high[1] and low < low[1])\n\tif (close > open and kvo>0 and lsma<close)\n\t\tstrategy.entry("long", strategy.long, comment="long")\nif (high < high[1] and low > low[1])\t\t\n\tif (close < open and kvo<0 and lsma>close)\n\t\tstrategy.entry("short", strategy.short, comment="short")\n\ntplong=input(0.006, step=0.001, title="Take profit % for long")\nsllong=input(0.012, step=0.001, title="Stop loss % for long")\ntpshort=input(0.0075, step=0.001, title="Take profit % for short")\nslshort=input(0.015, step=0.001, title="Stop loss % for short")\n\n\nstrategy.exit("short_tp/sl", "long", profit=close * tplong / syminfo.mintick, loss=close * sllong / syminfo.mintick, comment=\'LONG EXIT\',  alert_message = \'closeshort\')\nstrategy.exit("short_tp/sl", "short", profit=close * tpshort / syminfo.mintick, loss=close * slshort / syminfo.mintick, comment=\'SHORT EXIT\',  alert_message = \'closeshort\')\n\n'

class SMBreakoutSwingStrategy2b4460(PinePortBase, IStrategy):
    source_id = "SM_2b446091ae945f1d"
    source_file = '震荡突破策略Breakout-Swing-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 27, 'src': 'close', 'tplong': 0.006, 'sllong': 0.012, 'tpshort': 0.0075, 'slshort': 0.015}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
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
