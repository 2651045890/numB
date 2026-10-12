"""batch_011 port of 超级趋势日线反转策略Super-Trend-Daily-Reversal-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-22 00:00:00\nend: 2024-02-21 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Super Trend Daily BF ?", overlay=true, precision=2, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.075)\n\n/////////////// Time Frame ///////////////\n_1 = input(false,  "════════ Test Period ═══════")\ntestStartYear = input(2017, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() => true\n\n///////////// Super Trend /////////////\n_2 = input(false,  "══════ Super Trend ══════")\nlength = input(title="ATR Period", type=input.integer, defval=3)\nmult = input(title="ATR Multiplier", type=input.float, step=0.1, defval=1.3)\n\natr = mult * atr(length)\n\nlongStop = hl2 - atr\nlongStopPrev = nz(longStop[1], longStop)\nlongStop :=  close[1] > longStopPrev ? max(longStop, longStopPrev) : longStop\n\nshortStop = hl2 + atr\nshortStopPrev = nz(shortStop[1], shortStop)\nshortStop := close[1] < shortStopPrev ? min(shortStop, shortStopPrev) : shortStop\n\ndir = 1\ndir := nz(dir[1], dir)\ndir := dir == -1 and close > shortStopPrev ? 1 : dir == 1 and close < longStopPrev ? -1 : dir\n\n///////////// Rate Of Change ///////////// \n_3 = input(false,  "══════ Rate of Change ══════")\nsource = close\nroclength = input(30, "ROC Length",  minval=1)\npcntChange = input(6, "ROC % Change", minval=1)\nroc = 100 * (source - source[roclength]) / source[roclength]\nemaroc = ema(roc, roclength / 2)\nisMoving() => emaroc > (pcntChange / 2) or emaroc < (0 - (pcntChange / 2))\n\n///////////////  Strategy  /////////////// \nlong = dir == 1 and dir[1] == -1 and isMoving()\nshort = dir == -1 and dir[1] == 1 and isMoving()\n\nlast_long = 0.0\nlast_short = 0.0\nlast_long := long ? time : nz(last_long[1])\nlast_short := short ? time : nz(last_short[1])\n\nlong_signal = crossover(last_long, last_short)\nshort_signal = crossover(last_short, last_long)\n\nlast_open_long_signal = 0.0\nlast_open_short_signal = 0.0\nlast_open_long_signal := long_signal ? open : nz(last_open_long_signal[1])\nlast_open_short_signal := short_signal ? open : nz(last_open_short_signal[1])\n\nlast_long_signal = 0.0\nlast_short_signal = 0.0\nlast_long_signal := long_signal ? time : nz(last_long_signal[1])\nlast_short_signal := short_signal ? time : nz(last_short_signal[1])\n\nin_long_signal = last_long_signal > last_short_signal\nin_short_signal = last_short_signal > last_long_signal\n\nlast_high = 0.0\nlast_low = 0.0\nlast_high := not in_long_signal ? na : in_long_signal and (na(last_high[1]) or high > nz(last_high[1])) ? high : nz(last_high[1])\nlast_low := not in_short_signal ? na : in_short_signal and (na(last_low[1]) or low < nz(last_low[1])) ? low : nz(last_low[1])\n\nsince_longEntry = barssince(last_open_long_signal != last_open_long_signal[1]) \nsince_shortEntry = barssince(last_open_short_signal != last_open_short_signal[1]) \n\n/////////////// Dynamic ATR Stop Losses ///////////////\n_4 = input(false,  "════════ Stop Loss ═══════")\nSL_type = input("Fixed", options=["Fixed", "ATR Derived"], title="Stop Loss Type")\nsl_inp = input(6.0, title=\'Fixed Stop Loss %\') / 100\natrLkb = input(20, minval=1, title=\'ATR Stop Period\')\natrMult = input(1.5, step=0.25, title=\'ATR Stop Multiplier\') \natr1 = atr(atrLkb)\n\nlongStop1 = 0.0\nlongStop1 :=  short_signal ? na : long_signal ? close - (atr1 * atrMult) : longStop1[1]\nshortStop1 = 0.0\nshortStop1 := long_signal ? na : short_signal ? close + (atr1 * atrMult) : shortStop1[1]\n\nslLong = in_long_signal ? strategy.position_avg_price * (1 - sl_inp) : na\nslShort = strategy.position_avg_price * (1 + sl_inp)\nlong_sl = in_long_signal ? slLong : na\nshort_sl = in_short_signal ? slShort : na\n\n/////////////// Execution ///////////////\nif testPeriod()\n    strategy.entry("L", strategy.long, when=long)\n    strategy.entry("S", strategy.short, when=short)\n    strategy.exit("L SL", "L", stop = SL_type == "Fixed" ? long_sl : longStop1, when=since_longEntry > 0)\n    strategy.exit("S SL", "S", stop = SL_type == "Fixed" ? short_sl : shortStop1, when=since_shortEntry > 0)\n\n/////////////// Plotting /////////////// \nbgcolor(long_signal ? color.lime : short_signal ? color.red : na, transp=30)\nbgcolor(isMoving() ? dir == 1 ? color.lime : color.red : color.white , transp=80)'

class SMCA83C9714E31ECAB(PinePortBase, IStrategy):
    source_id = "SM_ca83c9714e31ecab"
    source_file = '超级趋势日线反转策略Super-Trend-Daily-Reversal-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'_1': False, 'testStartYear': 2017, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31, '_2': False, 'length': 3, 'mult': 1.3, '_3': False, 'roclength': 30, 'pcntChange': 6, '_4': False, 'SL_type': 'Fixed', 'sl_inp': 6.0, 'atrLkb': 20, 'atrMult': 1.5}
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
