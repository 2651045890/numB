"""batch_012 port of 震荡突破策略Zigzag-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-13 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=3\n// strategy(title = "Noro\'s ZZ-2 Strategy", shorttitle = "Noro\'s ZZ-2 Strategy", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Capital, %")\nlength = input(4, title = "ZigZag length")\nExtreme = input(4, title = "ZigZag extreme")\nsrc = input(close, title = "Source")\nshowzz = input(false, defval = false, title = "Show ZigZag")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//ZigZag\nf_zz(_length, _detection)=>\n    _hls = ema(ema(ema(src, _length), round(_length*0.66)), round(_length*0.33))\n    _isRising = _hls >= _hls[1]\n    _zigzag = _isRising and not _isRising[1] ? lowest(_detection) :  not _isRising and _isRising[1] ? highest(_detection) : na\nzigzag = f_zz(length, Extreme)\nzzcol = showzz ? black : na\nplot(zigzag, color = zzcol, linewidth = 2)\n\n//Levels\ndot = 0.0\ndot := zigzag > 0 ? zigzag : dot[1]\nuplevel = 0.0\nuplevel := dot > dot[1] ? zigzag : uplevel[1]\ndnlevel = 0.0\ndnlevel := dot < dot[1] ? zigzag : dnlevel[1]\nupcol = na\nupcol := dot > dot[1] ? na : lime\nplot(uplevel, color = upcol, linewidth = 2)\ndncol = na\ndncol := dot < dot[1] ? na : red\nplot(dnlevel, color = dncol, linewidth = 2)\n\n//Trading\nlot = 0.0\nlot := strategy.position_size != strategy.position_size[1] ? strategy.equity / close * capital / 100 : lot[1]\nif dot > 0\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : lot, stop = uplevel)\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : lot, stop = dnlevel)\n\n'

class SMZigzagBreakoutStrategyd2b434(PinePortBase, IStrategy):
    source_id = "SM_d2b434ca5edf0326"
    source_file = '震荡突破策略Zigzag-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'length': 4, 'Extreme': 4, 'src': 'close', 'showzz': False, 'fromyear': 1900, 'toyear': 2100, 'frommonth': 1, 'tomonth': 12, 'fromday': 1, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
