"""batch_011 port of 自适应权重趋势跟踪策略VIDYA多指标组合系统-Adaptive-Weighted-Trend-Following-Strategy-VIDYA-Multi-Indicator-System.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-04 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © GriffinJames\n\n\n//@version=5\nstrategy("VIDYA Strategy", overlay=true, initial_capital=25000)\n\n// Inputs\nsrc = input(close, title="Source")\npds = input.int(21, title="Length")\nfixCMO = input.bool(true, title="Fixed CMO Length (9)?")\nselect = input.bool(true, title="Calculation Method: CMO/StDev?")\nalpha = 2 / (pds + 1)\nmomm = ta.change(src)\n\n// Functions to calculate MOM\nf1(m) => m >= 0.0 ? m : 0.0\nf2(m) => m >= 0.0 ? 0.0 : -m\n\nm1 = f1(momm)\nm2 = f2(momm)\nsm1 = fixCMO ? math.sum(m1, 9) : math.sum(m1, pds)\nsm2 = fixCMO ? math.sum(m2, 9) : math.sum(m2, pds)\n\npercent(nom, div) => 100 * nom / div\nchandeMO = na(percent(sm1 - sm2, sm1 + sm2)) ? 0 : percent(sm1 - sm2, sm1 + sm2)\n\n// Select calculation method\nk = select ? math.abs(chandeMO) / 100 : ta.stdev(src, pds)\n\n// Calculate VIDYA\nvar float VIDYA = na\nVIDYA := na(VIDYA[1]) ? src : alpha * k * src + (1 - alpha * k) * VIDYA[1]\n\n// Conditions for long and short\ncol12 = VIDYA > VIDYA[1]\ncol32 = VIDYA < VIDYA[1]\n\n// Plot VIDYA with dynamic colors\ncolor2 = col12 ? color.new(color.blue, 0) : col32 ? color.new(color.maroon, 0) : color.new(color.blue, 0)\nplot(VIDYA, "VAR", color=color2, linewidth=2)\n\n// Long and Short Strategy\nif (col12)\n    strategy.entry("Go Long", strategy.long)\nif (col32)\n    strategy.entry("Go Short", strategy.short)\n\n// Alert for VIDYA color change\nalertcondition(ta.cross(VIDYA, VIDYA[1]), title="Color ALARM!", message="VIDYA has changed color!")\n'

class SM9B49E3FB30491526(PinePortBase, IStrategy):
    source_id = "SM_9b49e3fb30491526"
    source_file = '自适应权重趋势跟踪策略VIDYA多指标组合系统-Adaptive-Weighted-Trend-Following-Strategy-VIDYA-Multi-Indicator-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'pds': 21, 'fixCMO': True, 'select': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 25000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
