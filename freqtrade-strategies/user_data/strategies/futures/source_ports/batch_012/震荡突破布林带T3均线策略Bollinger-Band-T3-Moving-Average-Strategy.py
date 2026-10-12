"""batch_012 port of 震荡突破布林带T3均线策略Bollinger-Band-T3-Moving-Average-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-25 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(shorttitle="BB T3 Strategy", title="BB T3 Strategy", overlay=true)\n\n//T3\nb = 0.7\nc1 = -b*b*b\nc2 = 3*b*b+3*b*b*b\nc3 = -6*b*b-3*b-3*b*b*b\nc4 = 1+3*b+b*b*b+3*b*b\n\nt3(len) => c1 * ema(ema(ema(ema(ema(ema(close, len), len), len), len), len), len) + c2 * ema(ema(ema(ema(ema(close, len), len), len), len), len) + c3 * ema(ema(ema(ema(close, len), len), len), len) + c4 * ema(ema(ema(close, len), len), len)\n//T3 end\n\nlength = input(20, minval=1)\n\nmult = input(2.5, minval=0.001, maxval=50, title="StdDev")\nbasis = t3(length)\nbasisDev = t3(length/10)\n\ndev = mult * stdev(basisDev,length)\nupper = basis + dev\nlower = basis - dev\noffset = input(0, "Offset", type = input.integer, minval = -500, maxval = 500)\nplot(basis, "Basis", color=#872323, offset = offset)\np1 = plot(upper, "Upper", color=color.teal, offset = offset)\np2 = plot(lower, "Lower", color=color.teal, offset = offset)\nfill(p1, p2, title = "Background", color=#198787, transp=95)\n\nstoploss = input(true, "Stop Loss")\n\nbasisSma = sma(close, length)\np3 = plot(basisSma, color=color.blue, title="MA", offset=offset)\n\nfastT3 = t3(50)\nslowT3 = t3(200)\n\ncrossUp = crossover(basisSma, basis)\ncrossDown = crossunder(basisSma, basis)\nbollBounce = crossover(close, upper)\nbollReject = crossunder(close, lower)\nunderBasis = crossunder(close, basis)\noverBasis = crossover(close, basis)\n\ntrendUp = fastT3 > slowT3\ntrendDown = fastT3 < slowT3\n\nstrategy.entry("long", strategy.long, when=(trendUp and crossUp), stop=(stoploss ? high+syminfo.mintick : na))\nstrategy.close("long", when=(bollBounce or crossDown or underBasis))\nstrategy.entry("short", strategy.short, when=(trendDown and crossDown), stop=(stoploss ? low-syminfo.mintick : na))\nstrategy.close("short", when=(bollReject or crossUp or overBasis))\n\n'

class SMT3BollingerBandT3MovingAverageStrategy0cc45e(PinePortBase, IStrategy):
    source_id = "SM_0cc45ee5b9143f50"
    source_file = '震荡突破布林带T3均线策略Bollinger-Band-T3-Moving-Average-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'length': 20, 'mult': 2.5, 'offset': 0, 'stoploss': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
