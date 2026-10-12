"""batch_011 port of 自适应零滞后指数移动平均线量化交易策略Adaptive-Zero-Lag-Exponential-Moving-Average-Quantitative-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-19 00:00:00\nend: 2024-02-18 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="Adaptive Zero Lag EMA v2", shorttitle="AZLEMA", overlay = true)\n\nsrc = input(title="Source",  defval=close)\nPeriod = input(title="Period",  defval = 20)\nadaptive = input(title="Adaptive Method", options=["Off", "Cos IFM", "I-Q IFM", "Average"], defval="Off")\nGainLimit = input(title="Gain Limit",  defval = 10)\nThreshold = input(title="Threshold", type = float, defval=0.05, step=0.01)\nfixedSL = input(title="SL Points", defval=70)\nfixedTP = input(title="TP Points", defval=5)\nrisk = input(title=\'Risk\', defval=0.01, step=0.01)\n\n//##############################################################################\n//I-Q IFM\n//#############################################################################\nrange = input(title="Max Period",  defval=60, minval=8, maxval=100)\n\nPI = 3.14159265359\nimult = 0.635\nqmult = 0.338\ninphase = 0.0\nquadrature = 0.0\nre = 0.0\nim = 0.0\ndeltaIQ = 0.0\ninstIQ = 0.0\nlenIQ = 0.0\nV = 0.0\n\nP = src - src[7]\ninphase := 1.25*(P[4] - imult*P[2]) + imult*nz(inphase[3])\nquadrature := P[2] - qmult*P + qmult*nz(quadrature[2])\nre := 0.2*(inphase*inphase[1] + quadrature*quadrature[1]) + 0.8*nz(re[1])\nim := 0.2*(inphase*quadrature[1] - inphase[1]*quadrature) + 0.8*nz(im[1])\nif (re!= 0.0)\n    deltaIQ := atan(im/re)\nfor i=0 to range\n    V := V + deltaIQ[i]\n    if (V > 2*PI and instIQ == 0.0)\n        instIQ := i\nif (instIQ == 0.0)\n    instIQ := nz(instIQ[1])\nlenIQ := 0.25*instIQ + 0.75*nz(lenIQ[1])\n\n//##############################################################################\n//COSINE IFM\n//#############################################################################\ns2 = 0.0\ns3 = 0.0\ndeltaC = 0.0\ninstC = 0.0\nlenC = 0.0\nv1 = 0.0\nv2 = 0.0\nv4 = 0.0\n\nv1 := src - src[7]\ns2 := 0.2*(v1[1] + v1)*(v1[1] + v1) + 0.8*nz(s2[1])\ns3 := 0.2*(v1[1] - v1)*(v1[1] - v1) + 0.8*nz(s3[1])\nif (s2 != 0)\n    v2 := sqrt(s3/s2)\nif (s3 != 0)\n    deltaC := 2*atan(v2)\nfor i = 0 to range\n    v4 := v4 + deltaC[i]\n    if (v4 > 2*PI and instC == 0.0)\n        instC := i - 1\nif (instC == 0.0)\n    instC := instC[1]\nlenC := 0.25*instC + 0.75*nz(lenC[1])\n\nif (adaptive == "Cos IFM")\n    Period := round(lenC)\nif (adaptive == "I-Q IFM")\n    Period := round(lenIQ)\nif (adaptive == "Average")\n    Period := round((lenC + lenIQ)/2)\n\n//##############################################################################\n//ZERO LAG EXPONENTIAL MOVING AVERAGE\n//##############################################################################\nLeastError = 1000000.0\nEC = 0.0\nGain = 0.0\nEMA = 0.0\nError = 0.0\nBestGain = 0.0\n\nalpha =2/(Period + 1)\nEMA := alpha*src + (1-alpha)*nz(EMA[1])\n\nfor i = -GainLimit to GainLimit\n    Gain := i/10\n    EC := alpha*(EMA + Gain*(src - nz(EC[1]))) + (1 - alpha)*nz(EC[1])\n    Error := src - EC\n    if(abs(Error)<LeastError)\n        LeastError := abs(Error)\n        BestGain := Gain\n\nEC := alpha*(EMA + BestGain*(src - nz(EC[1]))) + (1-alpha)*nz(EC[1])\n\nplot(EC, title="EC", color=orange, linewidth=2)\nplot(EMA, title="EMA", color=red, linewidth=2)\n\nbuy = crossover(EC,EMA) and 100*LeastError/src > Threshold\nsell = crossunder(EC,EMA) and 100*LeastError/src > Threshold\nstrategy.initial_capital = 50000\nif (time>timestamp(2016, 1, 1 , 0, 0))\n    //LONG\n    balance = strategy.initial_capital + strategy.netprofit\n    lots = ((risk * balance)/fixedSL)*1\n    strategy.entry("BUY", strategy.long, qty=lots, oca_name="BUY",  when=buy)\n    strategy.exit("B.Exit", "BUY", qty_percent = 100, loss=fixedSL, trail_offset=15, trail_points=fixedTP)\n    //SHORT\n    strategy.entry("SELL", strategy.short, qty=lots, oca_name="SELL", when=sell)\n    strategy.exit("S.Exit", "SELL", qty_percent = 100, loss=fixedSL, trail_offset=15, trail_points=fixedTP)\n'

class SME56621F0534A4D36(PinePortBase, IStrategy):
    source_id = "SM_e56621f0534a4d36"
    source_file = '自适应零滞后指数移动平均线量化交易策略Adaptive-Zero-Lag-Exponential-Moving-Average-Quantitative-Trading-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'Period': 20, 'adaptive': 'Off', 'GainLimit': 10, 'Threshold': 0.05, 'fixedSL': 70, 'fixedTP': 5, 'risk': 0.01, 'range': 60}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['loop', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
