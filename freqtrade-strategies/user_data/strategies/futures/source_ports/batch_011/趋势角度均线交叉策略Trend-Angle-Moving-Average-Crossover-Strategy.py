"""batch_011 port of 趋势角度均线交叉策略Trend-Angle-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// Based on ma angles code by Duyck which also uses Everget Jurik MA calulation and angle calculation by KyJ\nstrategy("Trend Angle BF", overlay=false)\n\n/////////////// Time Frame ///////////////\ntestStartYear = input(2017, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() => true\n    \nsrc=input(ohlc4,title="source")\n\n// definition of "Jurik Moving Average", by Everget\njma(_src,_length,_phase,_power) =>\n    phaseRatio = _phase < -100 ? 0.5 : _phase > 100 ? 2.5 : _phase / 100 + 1.5\n    beta = 0.45 * (_length - 1) / (0.45 * (_length - 1) + 2)\n    alpha = pow(beta, _power)\n    jma = 0.0\n    e0 = 0.0\n    e0 := (1 - alpha) * _src + alpha * nz(e0[1])\n    e1 = 0.0\n    e1 := (_src - e0) * (1 - beta) + beta * nz(e1[1])\n    e2 = 0.0\n    e2 := (e0 + phaseRatio * e1 - nz(jma[1])) * pow(1 - alpha, 2) + pow(alpha, 2) * nz(e2[1])\n    jma := e2 + nz(jma[1])\n\n//// //// Determine Angle by KyJ //// //// \nangle(_src) =>\n    rad2degree=180/3.14159265359  //pi \n    ang=rad2degree*atan((_src[0] - _src[1])/atr(14)) \n\njma_line=jma(src,10,50,1)\nma=ema(src,input(56))\njma_slope=angle(jma_line)\nma_slope=angle(ma)\n\n///////////// Rate Of Change ///////////// \nsource = close\nroclength = input(12, minval=1)\npcntChange = input(2, minval=1)\nroc = 100 * (source - source[roclength]) / source[roclength]\nemaroc = ema(roc, roclength / 2)\nisMoving() => emaroc > (pcntChange / 2) or emaroc < (0 - (pcntChange / 2))\n\n/////////////// Strategy ///////////////\nlong = ma_slope>=0 and isMoving()\nshort = ma_slope<=0 and isMoving()\n\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nlong_signal = crossover(last_long, last_short)\nshort_signal = crossover(last_short, last_long)\n\nlast_open_long_signal = 0.0\nlast_open_short_signal = 0.0\nlast_open_long_signal := long_signal ? open : nz(last_open_long_signal[1])\nlast_open_short_signal := short_signal ? open : nz(last_open_short_signal[1])\n\nlast_long_signal = 0.0\nlast_short_signal = 0.0\nlast_long_signal := long_signal ? time : nz(last_long_signal[1])\nlast_short_signal := short_signal ? time : nz(last_short_signal[1])\n\nin_long_signal = last_long_signal > last_short_signal\nin_short_signal = last_short_signal > last_long_signal\n\nlast_high = 0.0\nlast_low = 0.0\nlast_high := not in_long_signal ? na : in_long_signal and (na(last_high[1]) or high > nz(last_high[1])) ? high : nz(last_high[1])\nlast_low := not in_short_signal ? na : in_short_signal and (na(last_low[1]) or low < nz(last_low[1])) ? low : nz(last_low[1])\nsl_inp = input(2.0, title=\'Stop Loss %\') / 100\ntp_inp = input(900.0, title=\'Take Profit %\') / 100 \n \ntake_level_l = strategy.position_avg_price * (1 + tp_inp)\ntake_level_s = strategy.position_avg_price * (1 - tp_inp) \n\nsince_longEntry = barssince(last_open_long_signal != last_open_long_signal[1]) \nsince_shortEntry = barssince(last_open_short_signal != last_open_short_signal[1]) \n\nslLong = in_long_signal ? strategy.position_avg_price * (1 - sl_inp) : na\nslShort = strategy.position_avg_price * (1 + sl_inp)\nlong_sl = in_long_signal ? slLong : na\nshort_sl = in_short_signal ? slShort : na\n\n/////////////// Execution /////////////// \nif testPeriod()\n    strategy.entry("Long",  strategy.long, when=long)\n    strategy.entry("Short", strategy.short, when=short)\n    strategy.exit("Long Ex", "Long", stop=long_sl, limit=take_level_l, when=since_longEntry > 0)\n    strategy.exit("Short Ex", "Short", stop=short_sl, limit=take_level_s, when=since_shortEntry > 0)\n    \n///////////// Plotting /////////////\nhline(0, title=\'Zero line\', color=color.purple, linewidth=1)\nplot(ma_slope,title="ma slope", linewidth=2,color=ma_slope>=0?color.lime:color.red)\nbgcolor(isMoving() ? long ? color.green : short ? color.red : na : color.white, transp=80)\nbgcolor(long_signal ? color.lime : short_signal ? color.red : na, transp=30) \n'

class SMB7EF4405C9F053F6(PinePortBase, IStrategy):
    source_id = "SM_b7ef4405c9f053f6"
    source_file = '趋势角度均线交叉策略Trend-Angle-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'testStartYear': 2017, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31, 'roclength': 12, 'pcntChange': 2, 'sl_inp': 2.0, 'tp_inp': 900.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
