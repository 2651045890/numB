"""batch_011 port of 趋势追踪优化双T3指标策略-Optimized-Dual-T3-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-15 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=6\nstrategy("FON60DK by leventsah", overlay=true)\n\n// Girdi AL\nt3_length = input.int(5, title="Tillson Per AL", minval=1)\nt3_opt = input.float(0.1, title="Tillson Opt AL", step=0.1, minval=0)\ntott_length = input.int(5, title="TOTT Per AL", minval=1)\ntott_opt = input.float(0.1, title="TOTT Opt AL", step=0.1, minval=0)\ntott_coeff = input.float(0.006, title="TOTT Coeff AL", step=0.001, minval=0)\n\n//GİRDİ SAT\nt3_lengthSAT = input.int(5, title="Tillson Per SAT", minval=1)\nt3_optSAT = input.float(0.1, title="Tillson Opt SAT", step=0.1, minval=0)\ntott_lengthSAT = input.int(5, title="TOTT Per SAT", minval=1)\ntott_opt_SAT = input.float(0.1, title="TOTT Opt SAT", step=0.1, minval=0)\ntott_coeff_SAT = input.float(0.006, title="TOTT Coeff SAT", step=0.001, minval=0)\n\nwilliam_length = input.int(3, title="William %R Periyodu", minval=1)\n\n// Tillson T3 AL\nt3(src, length, opt) =>\n    k = 2 / (length + 1)\n    ema1 = ta.ema(src, length)\n    ema2 = ta.ema(ema1, length)\n    ema3 = ta.ema(ema2, length)\n    ema4 = ta.ema(ema3, length)\n    c1 = -opt * opt * opt\n    c2 = 3 * opt * opt + 3 * opt * opt * opt\n    c3 = -6 * opt * opt - 3 * opt - 3 * opt * opt * opt\n    c4 = 1 + 3 * opt + opt * opt * opt + 3 * opt * opt\n    t3_val = c1 * ema4 + c2 * ema3 + c3 * ema2 + c4 * ema1\n    t3_val\n\nt3_value = t3(close, t3_length, t3_opt)\nt3_valueSAT = t3(close, t3_lengthSAT, t3_optSAT)\n\n\n// TOTT hesaplaması (Twin Optimized Trend Tracker)\nVar_Func(src, length) =>\n    valpha = 2 / (length + 1)\n    vud1 = math.max(src - src[1], 0)\n    vdd1 = math.max(src[1] - src, 0)\n    vUD = math.sum(vud1, 9)\n    vDD = math.sum(vdd1, 9)\n    vCMO = (vUD - vDD) / (vUD + vDD)\n    var float VAR = na\n    VAR := valpha * math.abs(vCMO) * src + (1 - valpha * math.abs(vCMO)) * nz(VAR[1], src)\n    VAR\n\nVAR = Var_Func(close, tott_length)\nVAR_SAT = Var_Func(close, tott_lengthSAT)\n\n//LONG \nMAvg = VAR\nfark = MAvg * tott_opt * 0.01\nlongStop = MAvg - fark\nlongStopPrev = nz(longStop[1], longStop)\nlongStop := MAvg > longStopPrev ? math.max(longStop, longStopPrev) : longStop\nshortStop = MAvg + fark\nshortStopPrev = nz(shortStop[1], shortStop)\nshortStop := MAvg < shortStopPrev ? math.min(shortStop, shortStopPrev) : shortStop\ndir = 1\ndir := nz(dir[1], dir)\ndir := dir == -1 and MAvg > shortStopPrev ? 1 : dir == 1 and MAvg < longStopPrev ? -1 : dir\nMT = dir == 1 ? longStop : shortStop\nOTT = MAvg > MT ? MT * (200 + tott_opt) / 200 : MT * (200 - tott_opt) / 200\nOTTup = OTT * (1 + tott_coeff)\nOTTdn = OTT * (1 - tott_coeff)\n\n//CLOSE\nMAvgS = VAR_SAT\nfarkS = MAvgS * tott_opt_SAT * 0.01\nlongStopS = MAvgS - farkS\nlongStopPrevS = nz(longStopS[1], longStopS)\nlongStopS := MAvgS > longStopPrevS ? math.max(longStopS, longStopPrevS) : longStopS\nshortStopS = MAvgS + farkS\nshortStopPrevS = nz(shortStopS[1], shortStopS)\nshortStopS := MAvgS < shortStopPrevS ? math.min(shortStopS, shortStopPrevS) : shortStopS\ndirS = 1\ndirS := nz(dirS[1], dirS)\ndirS := dirS == -1 and MAvgS > shortStopPrevS ? 1 : dirS == 1 and MAvgS < longStopPrevS ? -1 : dirS\nMTS = dirS == 1 ? longStopS : shortStopS\nOTTS = MAvgS > MTS ? MTS * (200 + tott_opt_SAT) / 200 : MTS * (200 - tott_opt_SAT) / 200\nOTTupS = OTTS * (1 + tott_coeff_SAT)\nOTTdnS = OTTS * (1 - tott_coeff_SAT)\n\n// Calculation of Williams %R\nwilliamsR = -100 * (ta.highest(high, william_length) - close) / (ta.highest(high, william_length) - ta.lowest(low, william_length))\n\n// Alım koşulu\nlongCondition = (t3_value > OTTup) and (williamsR > -20)\n\n// Short koşulu (long pozisyonunu kapatmak için)\nshortCondition = (t3_valueSAT < OTTdnS) and (williamsR > -70)\n\n// Alım pozisyonu açma\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short koşulu sağlandığında long pozisyonunu kapama\nif (shortCondition)\n    strategy.close("Long")\n\n\n// Alım pozisyonu boyunca barları yeşil yapma\nbarcolor(strategy.position_size > 0 ? color.green : na)\n\n// Grafikte göstergeleri çizme\nplot(t3_value, color=color.blue, linewidth=1, title="Tillson AL")\nplot(OTTup, color=color.green, linewidth=1, title="TOTT Up AL")\nplot(OTTdn, color=color.red, linewidth=1, title="TOTT Down AL")\n\n// Grafikte göstergeleri çizme\nplot(t3_valueSAT, color=color.blue, linewidth=1, title="Tillson SAT")\nplot(OTTupS, color=color.green, linewidth=1, title="TOTT Up SAT")\nplot(OTTdnS, color=color.red, linewidth=1, title="TOTT Down SAT")\n'

class SMC5320FB5B9BC73A4(PinePortBase, IStrategy):
    source_id = "SM_c5320fb5b9bc73a4"
    source_file = '趋势追踪优化双T3指标策略-Optimized-Dual-T3-Trend-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'t3_length': 5, 't3_opt': 0.1, 'tott_length': 5, 'tott_opt': 0.1, 'tott_coeff': 0.006, 't3_lengthSAT': 5, 't3_optSAT': 0.1, 'tott_lengthSAT': 5, 'tott_opt_SAT': 0.1, 'tott_coeff_SAT': 0.006, 'william_length': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
