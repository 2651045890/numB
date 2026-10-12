"""batch_011 port of 跨周期方向策略Eltrut-Turtle-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-27 00:00:00\nend: 2023-09-26 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Eltrut", shorttitle="Eltrut Strat", overlay=true, pyramiding=0, default_qty_type= strategy.percent_of_equity,calc_on_order_fills=false, slippage=25,commission_type=strategy.commission.percent,commission_value=0.075)\n\ntestStartYear = input(2016, "Backtest Start Year")\ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2030, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(30, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\n\n// R E F L E X / T R E N D F L E X\n\nf_supersmoother(_src,_len)=>\n    pi = 2 * asin(1)\n    _a = exp(-sqrt(2) * pi / _len)\n    _c2 = 2 * _a * cos(sqrt(2) * pi / _len)\n    _c3 = -_a * _a\n    _c1 = 1 - _c2 - _c3\n    _out = 0.0\n    _out := _c1 * _src + _c2 * nz(_out[1],nz(_src[1],_src)) + _c3 * nz(_out[2],nz(_src[2],nz(_src[1],_src)))\n\nf_IQIFM(_src1,_max)=>\n    _src = _src1 < 0.001 ? _src1 * 10000 : _src1\n    _imult = 0.635, _qmult = 0.338 , _inphase = 0.0, _quad = 0.0\n    _re = 0.0, _im = 0.0, _deltaphase = 0.0, _instper = 0.0, _per = 0.0, _v4 = 0.0\n    _v1 = _src - nz(_src[7])\n    _inphase := 1.25 * (nz(_v1[4]) - _imult * _v1[2]) + _imult * nz(_inphase[3])\n    _quad := _v1[2] - _qmult * _v1 + _qmult * nz(_quad[2])\n    _re := 0.2 * (_inphase * _inphase[1] + _quad * _quad[1]) + 0.8 * nz(_re[1])\n    _im := 0.2 * (_inphase * _quad[1] - _inphase[1] * _quad) + 0.8 * nz(_im[1])\n    if _re != 0.0\n        _deltaphase := atan(_im / _re)\n    for i = 0 to _max\n        _v4 := _v4 + _deltaphase[i]\n        if _v4 > 4 * asin(1) and _instper == 0.0\n            _instper := i\n    if _instper == 0.0\n        _instper := nz(_instper[1])\n    _per := 0.25 * _instper + 0.75 * nz(_per[1])\n    _per\n\nf_flex(_src1, _fixed_len, _reflex) =>\n    _src = _src1\n    _len = _fixed_len \n    _ss1 = f_supersmoother(_src, _len)\n    _ss = _ss1\n    _slope = (_ss[_len] - _ss) / _len\n    _sum = 0.0\n    for _i = 1 to _len\n        _c1 = _reflex ? _ss + _i * _slope - _ss[_i] : _ss - _ss[_i]\n        _sum := _sum + _c1\n    _sum := _sum / _len\n    _ms = 0.0\n    _ms := 0.04 * pow(_sum,2) + 0.96 * nz(_ms[1])\n    _flex1 = _ms != 0 ? _sum / sqrt(nz(_ms)) : 0.0\n    _flex = _flex1\n    _flex\n\nrflx = f_flex(close, 20, true)  \ntrndflx = f_flex(close, 20, false)   \n\n// S I G N A L\nhi7 = highest(7)\nlo7 = lowest(7)\nlong_cond = crossunder(close, lo7[1])\nshort_cond = crossover(close, hi7[1])\n\n// F I L T E R S\n\nlong_filter1 = trndflx < 1\nshort_filter1 = trndflx > -1\n\nbasis = sma(close, 35)\ndev = 3 * stdev(close, 35)\nlong_filter2 = close > basis - dev\nshort_filter2 = close < basis + dev\n\n// S T R A T E G Y\n\nlong = long_cond and long_filter1 and long_filter2\nshort = short_cond and short_filter1 and short_filter2\n\nif( true)\n    strategy.entry("Long", strategy.long, when = long)\n    strategy.entry("Long", strategy.long, when = short)\n\n\n// User Options to Change Inputs (%)\nstopPer = input(3, title=\'Stop Loss %\', type=input.float) / 100\ntakePer = input(9, title=\'Take Profit %\', type=input.float) / 100\n\n// Determine where you\'ve entered and in what direction\nlongStop = strategy.position_avg_price * (1 - stopPer)\nshortStop = strategy.position_avg_price * (1 + stopPer)\nshortTake = strategy.position_avg_price * (1 - takePer)\nlongTake = strategy.position_avg_price * (1 + takePer)\n\nif strategy.position_size > 0 \n    strategy.exit(id="Exit Long", stop=longStop, limit=longTake)\nif strategy.position_size < 0 \n    strategy.exit(id="Exit Short", stop=shortStop, limit=shortTake)\n\n\n// P L O T \n\nplotshape(long, color = #1e90ff, text = "", style=shape.triangleup, location=location.belowbar, size=size.tiny)\nplotshape(short, color = #ff69b4, text = "", style=shape.triangledown, location=location.abovebar, size=size.tiny)\n\nalertcondition(long, "Long", "Enter Long")\nalertcondition(short, "Short", "Enter S")'

class SMD4E7DDB23A75C84C(PinePortBase, IStrategy):
    source_id = "SM_d4e7ddb23a75c84c"
    source_file = '跨周期方向策略Eltrut-Turtle-Reversal-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {'testStartYear': 2016, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2030, 'testStopMonth': 12, 'testStopDay': 30, 'stopPer': 3, 'takePer': 9}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1
    source_commission_percent = 0.075
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'loop', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
