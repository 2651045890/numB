"""batch_011 port of 自适应多重均线动量突破交易策略-Adaptive-Multi-MA-Momentum-Breakthrough-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-10 00:00:00\nend: 2025-01-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\n\n//study("Limit order strategy", overlay=true)\nstrategy(\'Limit order strategy\', overlay = true)\n\nlengthMA = input(1)\nlengthmi = input(14)\nlengthhigh = input(14)\nlengthlow = input(14)\n\ncalc_smma(src, len) =>\n    smma = 0.0\n    smma := na(smma[1]) ? ta.sma(src, len) : (smma[1] * (len - 1) + src) / len\n    smma\n\ncalc_zlema(src, length) =>\n    ema1 = ta.ema(src, length)\n    ema2 = ta.ema(ema1, length)\n    d = ema1 - ema2\n    ema1 + d\n\n\nsrc = calc_smma(hlc3, lengthMA)\nhi = calc_smma(high, lengthhigh)\nlo = calc_smma(low, lengthlow)\nmi = calc_zlema(src, lengthmi)\n\nplot(src, color = color.new(#FF1493, 0), linewidth = 2, title = \'src\')\nplot(hi, color = color.new(#7CFC00, 0), linewidth = 2, title = \'hi\')\nplot(lo, color = color.new(#FF0000, 0), linewidth = 2, title = \'lo\')\nplot(mi, color = color.new(#00FFFF, 0), linewidth = 2, title = \'mi\')\n\n\n//strategy.order("buy", true, 1, stop = na, when = openbuy) // buy by market if current open great then previous high\n//strategy.order("sell", false, 1, stop = na, when = opensell) // sell by market if current open less then previous low\n//if src >= mi and src[1] <= mi[1] and src[1] <= lo[1]\n//\tstrategy.entry("buy 1", strategy.long, qty = 15)\nsigorderbuy1 = src > mi and src[1] < mi[1] and src < lo and mi < lo\nsigorderbuy2 = src > lo and src[1] < lo[1] and mi < lo\nsigorderbuy3 = src > hi and src[1] < hi[1] and mi < hi\nsigorderbuy4 = src > mi and src[1] < mi[1] and src > hi and mi > hi\n//sigorderbuy5 = mi > hi and  src > hi  and src > mi and src[1] < mi[1] \n//sigorderbuy6 = mi < hi and src > hi and src[1] < hi[1]\nsigclosebuy = src < mi and src[1] > mi[1] or mi < lo and src < lo and src[1] > lo[1]\n\nsigordersell1 = src < mi and src[1] > mi[1] and src > hi and mi > hi\nsigordersell2 = src < hi and src[1] > hi[1] and mi > hi\nsigordersell3 = src < lo and src[1] > lo[1] and mi > lo\nsigordersell4 = src < mi and src[1] > mi[1] and src < lo and mi < lo\n//sigordersell5 = mi < lo and  src < lo  and src < mi and src[1] > mi[1] \n//sigordersell6 = mi > lo and src < lo and src[1] > lo[1]\nsigclosesell = src > mi and src[1] < mi[1] or mi > hi and src > hi and src[1] < hi[1]\n\nplot(sigorderbuy1 ? 1 : 0, \'sigorderbuy1\')\nplot(sigorderbuy2 ? 1 : 0, \'sigorderbuy2\')\nplot(sigorderbuy3 ? 1 : 0, \'sigorderbuy3\')\nplot(sigorderbuy4 ? 1 : 0, \'sigorderbuy4\')\n//plot(sigorderbuy5 ? 1 : 0,"sigorderbuy5") \n//plot(sigorderbuy6 ? 1 : 0,"sigorderbuy6") \n\nplot(sigordersell1 ? 1 : 0, \'sigordersell1\')\nplot(sigordersell2 ? 1 : 0, \'sigordersell2\')\nplot(sigordersell3 ? 1 : 0, \'sigordersell3\')\nplot(sigordersell4 ? 1 : 0, \'sigordersell4\')\n//plot(sigordersell5 ? 1 : 0,"sigordersell5") \n//plot(sigordersell6 ? 1 : 0,"sigordersell6")\n\nplot(sigclosebuy ? 1 : 0, \'sigclosebuy\')\nplot(sigclosesell ? 1 : 0, \'sigclosesell\')\n\n\nopenbuy = sigorderbuy1 or sigorderbuy2 or sigorderbuy3 or sigorderbuy4 // or sigorderbuy5 or sigorderbuy6\nopensell = sigordersell1 or sigordersell2 or sigordersell3 or sigordersell4 //or sigordersell5 or sigordersell6\nopenclosebuy = sigclosebuy\nopenclosesell = sigclosesell\n\nalertcondition(condition = openbuy, title = \'sigorderbuy all\', message = \'{"accountmt":"70415621,666734890","time":"15","msg":"Buy {{ticker}} sig_b1={{plot("sigorderbuy1")}} sig_b2={{plot("sigorderbuy2")}} sig_b3={{plot("sigorderbuy3")}} sig_b4={{plot("sigorderbuy4")}}"}\')\nalertcondition(condition = opensell, title = \'sigordersell all\', message = \'{"accountmt":"70415621,666734890","time":"15","msg":"Sell {{ticker}} sig_s1={{plot("sigordersell1")}} sig_ss={{plot("sigordersell2")}} sig_s3={{plot("sigordersell3")}} sig_s4={{plot("sigordersell4")}} sig_s5={{plot("sigordersell5")}} sig_61={{plot("sigordersell6")}}"}\')\n\nalertcondition(condition = sigclosebuy, title = \'Close buy\', message = \'{"accountmt":"70415621,666734890","time":"15","msg":"Close {{ticker}} T=short"}\')\nalertcondition(condition = sigclosesell, title = \'Close sell\', message = \'{"accountmt":"70415621,666734890","time":"15","msg":"Close {{ticker}} T=long"}\')\n\nif sigorderbuy1\n    strategy.order(\'Buy 1\', strategy.long, 1)\nif sigorderbuy2\n    strategy.order(\'Buy 2\', strategy.long, 1)\nif sigorderbuy3\n    strategy.order(\'Buy 3\', strategy.long, 1)\nif sigorderbuy4\n    strategy.order(\'Buy 4\', strategy.long, 1)\n\n\nif sigordersell1\n    strategy.order(\'sell 1\', strategy.short, 1)\nif sigordersell2\n    strategy.order(\'sell 2\', strategy.short, 1)\nif sigordersell3\n    strategy.order(\'sell 3\', strategy.short, 1)\nif sigordersell4\n    strategy.order(\'sell 4\', strategy.short, 1)\n//strategy.order("sell 5", false, 1, when = sigordersell5)\n//strategy.order("sell 6", false, 1, when = sigordersell6)\n'

class SM74B08D1A55590A0F(PinePortBase, IStrategy):
    source_id = "SM_74b08d1a55590a0f"
    source_file = '自适应多重均线动量突破交易策略-Adaptive-Multi-MA-Momentum-Breakthrough-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lengthMA': 1, 'lengthmi': 14, 'lengthhigh': 14, 'lengthlow': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
