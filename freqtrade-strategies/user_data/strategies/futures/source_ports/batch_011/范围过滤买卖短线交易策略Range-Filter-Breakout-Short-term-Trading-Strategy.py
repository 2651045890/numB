"""batch_011 port of 范围过滤买卖短线交易策略Range-Filter-Breakout-Short-term-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-21 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="Range Filter Buy and Sell 5min [Strategy]", overlay=true, commission_type=strategy.commission.percent, commission_value=0.025, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000, slippage=0)\n\n// === INPUT BACKTEST RANGE ===\nuseDate = input(true,     title=\'---------------- Use Date ----------------\', type=bool)\nFromMonth = input(defval = 7, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 25, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2019, title = "From Year", minval = 2017)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999, title = "To Year", minval = 2017)\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nwindow()  => true  // create function "within window of time"\n// === INPUT BACKTEST RANGE ===\n\n\nsources = input(defval=close, title="Source")\nisHA = input(false, "Use HA Candles", bool)\nsrc = isHA ? security(heikenashi(tickerid), period, sources) : sources\n// Sampling Period\n// Settings for 5min chart, BTCUSDC. For Other coin, change the paremeters\n\nper = input(defval=50, minval=1, title="Sampling Period")\n\n// Range Multiplier\n\nmult = input(defval=3.0, minval=0.1, title="Range Multiplier")\n\n// Smooth Average Range\n\nsmoothrng(x, t, m)=>\n    wper      = (t*2) - 1\n    avrng     = ema(abs(x - x[1]), t)\n    smoothrng = ema(avrng, wper)*m\n    smoothrng\nsmrng = smoothrng(src, per, mult)\n\n// Range Filter\n\nrngfilt(x, r)=>\n    rngfilt  = x\n    rngfilt := x > nz(rngfilt[1]) ? ((x - r) < nz(rngfilt[1]) ? nz(rngfilt[1]) : (x - r)) : ((x + r) > nz(rngfilt[1]) ? nz(rngfilt[1]) : (x + r))\n    rngfilt\nfilt = rngfilt(src, smrng)\n\n// Filter Direction\n\nupward   = 0.0\nupward  := filt > filt[1] ? nz(upward[1]) + 1 : filt < filt[1] ? 0 : nz(upward[1])\ndownward = 0.0\ndownward := filt < filt[1] ? nz(downward[1]) + 1 : filt > filt[1] ? 0 : nz(downward[1])\n\n// Target Bands\n\nhband = filt + smrng\nlband = filt - smrng\n\n// Colors\n\nfiltcolor = upward > 0 ? lime : downward > 0 ? red : orange\nbarcolor  = (src > filt) and (src > src[1]) and (upward > 0) ? lime : (src > filt) and (src < src[1]) and (upward > 0) ? green : \n   (src < filt) and (src < src[1]) and (downward > 0) ? red : (src < filt) and (src > src[1]) and (downward > 0) ? maroon : orange\n\nfiltplot = plot(filt, color=filtcolor, linewidth=3, title="Range Filter")\n\n// Target\n\nhbandplot = plot(hband, color=aqua, transp=100, title="High Target")\nlbandplot = plot(lband, color=fuchsia, transp=100, title="Low Target")\n\n// Fills\n\nfill(hbandplot, filtplot, color=aqua, title="High Target Range")\nfill(lbandplot, filtplot, color=fuchsia, title="Low Target Range")\n\n// Bar Color\n\n//barcolor(barcolor)\n\n// Break Outs \n\nlongCond = na\nshortCond = na\nlongCond := ((src > filt) and (src > src[1]) and (upward > 0)) or ((src > filt) and (src < src[1]) and (upward > 0)) \nshortCond := ((src < filt) and (src < src[1]) and (downward > 0)) or ((src < filt) and (src > src[1]) and (downward > 0))\n\nCondIni = 0\nCondIni := longCond ? 1 : shortCond ? -1 : CondIni[1]\nlongCondition = longCond and CondIni[1] == -1\nshortCondition = shortCond and CondIni[1] == 1\n\n//Alerts\n\nplotshape(longCondition, title = "Buy Signal", text ="BUY", textcolor = white, style=shape.labelup, size = size.normal, location=location.belowbar, color = green, transp = 0)\nplotshape(shortCondition, title = "Sell Signal", text ="SELL", textcolor = white, style=shape.labeldown, size = size.normal, location=location.abovebar, color = red, transp = 0)\n\n//strategy.entry("Long", strategy.long, stop = hband, when = window() , comment="Long")\n//strategy.entry("Short", strategy.short, stop = lband, when = window() , comment="Short")\n\nstrategy.entry("Long", strategy.long, when = longCondition and window() , comment="Long")\nstrategy.entry("Short", strategy.short, when = shortCondition and window() , comment="Short")\n\n\n\n// === Stop LOSS ===\nuseStopLoss = input(false, title=\'----- Use Stop Loss / Take profit -----\', type=bool)\nsl_inp = input(100, title=\'Stop Loss %\', type=float, step=0.25)/100\ntp_inp = input(1.5, title=\'Take Profit %\', type=float, step=0.25)/100\nstop_level = strategy.position_avg_price * (1 - sl_inp)\ntake_level = strategy.position_avg_price * (1 + tp_inp)\nstop_level_short = strategy.position_avg_price * (1 + sl_inp)\ntake_level_short = strategy.position_avg_price * (1 - tp_inp)\n// === Stop LOSS ===\n\nif useStopLoss\n    strategy.exit("Stop Loss/Profit Long","Long", stop=stop_level, limit=take_level)\n    strategy.exit("Stop Loss/Profit Short","Short", stop=stop_level_short, limit=take_level_short)\n'

class SMD426C4DFC8638571(PinePortBase, IStrategy):
    source_id = "SM_d426c4dfc8638571"
    source_file = '范围过滤买卖短线交易策略Range-Filter-Breakout-Short-term-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'useDate': True, 'FromMonth': 7, 'FromDay': 25, 'FromYear': 2019, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999, 'isHA': False, 'per': 50, 'mult': 3.0, 'useStopLoss': False, 'sl_inp': 100, 'tp_inp': 1.5}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0.025
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'func', 'broker_state', 'entry_price_order', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
