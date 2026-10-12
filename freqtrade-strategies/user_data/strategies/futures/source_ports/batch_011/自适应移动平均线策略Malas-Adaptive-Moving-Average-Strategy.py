"""batch_011 port of 自适应移动平均线策略Malas-Adaptive-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-30 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © dongyun\n\n//@version=4\nstrategy("自适应移动平均的MESA系统", overlay=true)\n\nfastlimit = input(0.5,\'\')\nslowlimit = input(0.05,\'\')\n\nsmooth = 0.0\ndetrender = 0.0\nI1 = 0.0\nQ1 = 0.0\nJI = 0.0\nJQ = 0.0\nI2 = 0.0\nQ2 = 0.0\nRe = 0.0\nIm = 0.0\nperiod = 0.0\nsmoothperiod = 0.0\nphase = 0.0\ndeltaphase = 0.0\nalpha = 0.0\nMAMA = 0.0\nFAMA = 0.0\nprice = 0.0\n\nprice := (high + low)/2\nPI = 2 * asin(1)\n\nif (bar_index > 5)\n\tsmooth := (4*price + 3*price[1] + 2*price[2] + price[3])/10\n\tdetrender := (.0962*smooth + .5769*nz(smooth[2]) - .5769*nz(smooth[4]) - .0962*nz(smooth[6]))*(.075*nz(period[1]) + .54)\n\n\t// compute InPhase and Quadrature components\n\tQ1 := (.0962*detrender + .5769*nz(detrender[2]) - .5769*nz(detrender[4]) - .0962*nz(detrender[6]))*(.075*nz(period[1]) + .54)\n\n\tI1 := nz(detrender[3])\n\n\t// advance the pulse of i1 and q1 by 90 degrees\n\tJI := (.0962*I1 + .5769*nz(I1[2]) - .5769*nz(I1[4]) - .0962*nz(I1[6]))*(.075*nz(period[1]) + .54)\n\tJQ := (.0962*Q1 + .5769*nz(Q1[2]) - .5769*nz(Q1[4]) - .0962*nz(Q1[6]))*(.075*nz(period[1]) + .54)\n\n\t//phase addition for 3-bar averaging \n\tI2 := I1 - JQ\n\tQ2 := Q1 + JI\n\n\t//smooth the i and q components before applying\n\tI2 := .2*I2 + .8*nz(I2[1])\n\tQ2 := .2*Q2 + .8*nz(Q2[1])\n\n\t// hymodyne discriminator\n\tRe := I2*I2[1] + Q2*nz(Q2[1])\n\tIm := I2*Q2[1] + Q2*nz(I2[1])\n\tRe := .2*Re + .8*nz(Re[1])\n\tIm := .2*Im + .8*nz(Im[1])\n\n\tif (Im != 0 and Re != 0)\n\t\tperiod := 2 * PI/atan(Im/Re)\n\n\tif (period > 1.5 * nz(period[1]))\n\t\tperiod := 1.5*nz(period[1])\n\n\tif (period < .67*nz(period[1]))\n\t\tperiod := .67*nz(period[1])\n\n\tif (period < 6)\n\t\tperiod := 6\n\n\tif (period > 50)\n\t\tperiod := 50\n\n\tperiod := .2*period + .8*nz(period[1])\n\tsmoothperiod := .33*period + .67*nz(smoothperiod[1])\n\n\tif (I1 != 0)\n\t\tphase := (180/PI) * atan(Q1/I1)\n\n\tdeltaphase := nz(phase[1]) - phase\n\n\tif (deltaphase < 1)\n\t\tdeltaphase := 1\n\n\talpha := fastlimit/deltaphase\n\tif(alpha < slowlimit)\n\t\talpha := slowlimit\n\n\tMAMA := alpha*price + (1 - alpha)*nz(MAMA[1])\n\tFAMA := .5*alpha*MAMA + (1 - .5*alpha)*nz(FAMA[1])\n\n\tif (FAMA < MAMA)\n\t\tstrategy.entry("Long", strategy.long)\n\telse\n\t\tif (FAMA > MAMA)\n\t\t\tstrategy.entry("Short", strategy.short)\n'

class SM3C1E1935A875A82B(PinePortBase, IStrategy):
    source_id = "SM_3c1e1935a875a82b"
    source_file = '自适应移动平均线策略Malas-Adaptive-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastlimit': 0.5, 'slowlimit': 0.05}
    source_qty_type = 'fixed'
    source_qty_value = 1
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
