"""batch_011 port of 螺旋上升突破均线策略Spiral-Breakout-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-07 00:00:00\nend: 2024-01-14 00:00:00\nperiod: 45m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("SSL Chaikin BF ?", overlay=true, precision=2, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.075)\n\n/////////////// Time Frame ///////////////\n_0 = input(false,  "════════ Test Period ═══════")\ntestStartYear = input(2017, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() => true\n\n/////////////// Chaikin MF /////////////// \n_1 = input(false,  "═══════ Chaikin MF ═══════")\nlength = input(20, minval=1, title = "Chaikin SMA Length")\nupperThreshold = input(0.04, step=0.01, title="Upper Threshold")\nlowerThreshold = input(0.02, step=0.01, title="Lower Threshold")\nad = close==high and close==low or high==low ? 0 : ((2*close-low-high)/(high-low))*volume\nmf = sum(ad, length) / sum(volume, length)\n\n/////////////// SSL Channels /////////////// \n_2 = input(false,  "═════════ SSL ══════════")\nlen1=input(title="SMA Length 1", defval=12)\nlen2=input(title="SMA Length 2", defval=13)\n\nsmaHigh = sma(high, len1)\nsmaLow = sma(low, len2)\n\nHlv = 0\nHlv := close > smaHigh ? 1 : close < smaLow ? -1 : Hlv[1]\nsslDown = Hlv < 0 ? smaHigh : smaLow\nsslUp = Hlv < 0 ? smaLow : smaHigh\n\n///////////// Rate Of Change ///////////// \n_3 = input(false,  "══════ Rate of Change ══════")\nsource = close\nroclength = input(13, "ROC Length",  minval=1)\npcntChange = input(4, "ROC % Change", minval=1)\nroc = 100 * (source - source[roclength]) / source[roclength]\nemaroc = ema(roc, roclength / 2)\nisMoving() => emaroc > (pcntChange / 2) or emaroc < (0 - (pcntChange / 2))\n\n///////////////  Strategy  /////////////// \nlong = sslUp > sslDown and isMoving() or crossover(mf, upperThreshold)\nshort = sslUp < sslDown and isMoving() or crossunder(mf, lowerThreshold)\n\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nlong_signal = crossover(last_long, last_short)\nshort_signal = crossover(last_short, last_long)\n\nlast_open_long_signal = 0.0\nlast_open_short_signal = 0.0\nlast_open_long_signal := long_signal ? open : nz(last_open_long_signal[1])\nlast_open_short_signal := short_signal ? open : nz(last_open_short_signal[1])\n\nlast_long_signal = 0.0\nlast_short_signal = 0.0\nlast_long_signal := long_signal ? time : nz(last_long_signal[1])\nlast_short_signal := short_signal ? time : nz(last_short_signal[1])\n\nin_long_signal = last_long_signal > last_short_signal\nin_short_signal = last_short_signal > last_long_signal\n\nlast_high = 0.0\nlast_low = 0.0\nlast_high := not in_long_signal ? na : in_long_signal and (na(last_high[1]) or high > nz(last_high[1])) ? high : nz(last_high[1])\nlast_low := not in_short_signal ? na : in_short_signal and (na(last_low[1]) or low < nz(last_low[1])) ? low : nz(last_low[1])\n\nsince_longEntry = barssince(last_open_long_signal != last_open_long_signal[1]) \nsince_shortEntry = barssince(last_open_short_signal != last_open_short_signal[1]) \n\n//////////////// Stop loss /////////////// \n_4 = input(false,  "════════ Stop Loss ═══════")\nsl_inp = input(2.0, title=\'Stop Loss %\') / 100\n\nslLong = in_long_signal ? strategy.position_avg_price * (1 - sl_inp) : na\nslShort = strategy.position_avg_price * (1 + sl_inp)\nlong_sl = in_long_signal ? slLong : na\nshort_sl = in_short_signal ? slShort : na\n\n/////////////// Execution /////////////// \nif testPeriod()\n    strategy.entry("L", strategy.long, when=long)\n    strategy.entry("S", strategy.short, when=short)\n    strategy.exit("L SL", "L", stop=long_sl, when=since_longEntry > 0)\n    strategy.exit("S SL", "S", stop=short_sl, when=since_shortEntry > 0)\n\n/////////////// Plotting /////////////// \np1 = plot(sslDown, linewidth = 1, color=color.red)\np2 = plot(sslUp, linewidth = 1, color=color.lime)\nfill(p1, p2,  color = sslDown < sslUp ? color.lime : color.red, transp=80)\nbgcolor(isMoving() ? long ? color.green : short ? color.red : na : color.white, transp=80)\nbgcolor(long_signal ? color.lime : short_signal ? color.red : na, transp=30)\nbgcolor(crossover(mf, upperThreshold) ? color.blue : crossunder(mf, lowerThreshold) ? color.orange : na, transp=30)'

class SMA1633608EFAB2577(PinePortBase, IStrategy):
    source_id = "SM_a1633608efab2577"
    source_file = '螺旋上升突破均线策略Spiral-Breakout-Moving-Average-Strategy.md'
    timeframe = '45m'
    can_short = True
    source_defaults = {'_0': False, 'testStartYear': 2017, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31, '_1': False, 'length': 20, 'upperThreshold': 0.04, 'lowerThreshold': 0.02, '_2': False, 'len1': 12, 'len2': 13, '_3': False, 'roclength': 13, 'pcntChange': 4, '_4': False, 'sl_inp': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.075
    source_pyramiding = 0
    source_initial_capital = 10000
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
