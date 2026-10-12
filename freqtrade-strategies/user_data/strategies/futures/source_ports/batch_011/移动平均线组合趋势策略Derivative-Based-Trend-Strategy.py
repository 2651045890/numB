"""batch_011 port of 移动平均线组合趋势策略Derivative-Based-Trend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-04 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Big 3",overlay=true, default_qty_type=strategy.percent_of_equity)\n \n// enter on Arrows\n// take profit on touch with 80 SMA, gray, or at discretion\n \nfast = sma(close,20)\nmid = sma(close,40)\nslow = sma(close,80)\n \nplot(fast,linewidth=1)\nplot(mid,linewidth=2)\nplot(slow,linewidth=4)\n \nisUptrend = close > fast and close > mid and close > slow\nisDowntrend = close < fast and close < mid and close < slow\n \nconfirmed = (low > fast and low > mid and low > slow) or (high < fast and high < mid and high < slow)\nderiv = 3 * mid[0] - 4 * mid[1] + mid[2]\n\nstableUptrend = (fast > mid) and (mid > slow) and (deriv > 0)\nstableDowntrend = (fast < mid) and (mid < slow) and (deriv < 0)\n \nbarcolor(isUptrend ? green : isDowntrend ? red : gray)\nplotshape(not confirmed[1] and confirmed and isUptrend ? close : na,style=shape.arrowup,location=location.belowbar,color=green)\nplotshape(not confirmed[1] and confirmed and isDowntrend ? close : na,style=shape.arrowdown,location=location.abovebar,color=red)\n\nstop = na\n//stop = input(1000, "Stop")\n\n\nstrategy.entry("long", strategy.long, when=(stableUptrend), stop=stop)\nstrategy.close("long", when=(deriv <= 0))\n\nstrategy.entry("short", strategy.short, when=(stableDowntrend), stop=stop)\nstrategy.close("short", when=(deriv >= 0))\n\n\n\n'

class SM5D1B9E68C05E5269(PinePortBase, IStrategy):
    source_id = "SM_5d1b9e68c05e5269"
    source_file = '移动平均线组合趋势策略Derivative-Based-Trend-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['entry_price_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
