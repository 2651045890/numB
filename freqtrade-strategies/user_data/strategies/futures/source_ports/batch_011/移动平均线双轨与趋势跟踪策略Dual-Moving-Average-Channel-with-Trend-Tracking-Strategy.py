"""batch_011 port of 移动平均线双轨与趋势跟踪策略Dual-Moving-Average-Channel-with-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-01 00:00:00\nend: 2023-10-31 23:59:59\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// author: codachang0726\nstrategy(title = "(S)MA+ADX+DI+time", shorttitle = "(S)MA+ADX+DI+time", overlay = true)\n\n// === INPUT MA LENGTHS ===\nfastMA    = input(defval = 7,   title = "FastMA",          minval = 1, step = 1)\nslowMA    = input(defval = 14,   title = "SlowMA",          minval = 1, step = 1)\n\n// === INPUT BACKTEST RANGE ===\nfromMonth = input(defval = 9,    title = "From Month",      minval = 1, maxval = 12)\nfromDay   = input(defval = 1,    title = "From Day",        minval = 1, maxval = 31)\nfromYear  = input(defval = 2020, title = "From Year",       minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        minval = 1, maxval = 31)\nthruYear  = input(defval = 2022, title = "Thru Year",       minval = 1970)\n\n// === INPUT SHOW PLOT ===\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true       // create function "within window of time"\n\n// === MA LOGIC ===\ncrossOv   =  sma(close, fastMA) > sma(close, slowMA)     // true when fastMA over slowMA\ncrossUn   =  sma(close, fastMA) < sma(close, slowMA)     // true when fastMA under slowMA\n\n// DI+ADX\nadxlen      = input(14, title="ADX Smoothing")\ndilen       = input(14, title="DI Period")\nkeyLevel    = input(20, title="Keylevel for ADX")\n[diplus, diminus, adx] = dmi(dilen, adxlen)\ndi = (diplus - diminus)\n\nbuy = di > 0 and crossOv and adx > keyLevel\nsell = di < 0 and crossUn and adx > keyLevel\n\nbuy_time = buy and not buy[1]\nsell_time = sell and not sell[1]\n\n// === EXECUTION ===\nstrategy.entry("L", strategy.long, when = window() and buy_time)    // enter long when "within window of time" AND crossover\nstrategy.close("L", when = window() and sell_time)                   // exit long when "within window of time" AND crossunder         \n\n// === PLOTTING ===\nbgcolor(color = showDate and window() ? color.gray : na, transp = 90)                                     // plot "within window of time"\nplot(sma(close, fastMA), title = \'FastMA\', color = color.yellow, linewidth = 2, style = plot.style_line)  // plot FastMA\nplot(sma(close, slowMA), title = \'SlowMA\', color = color.aqua,   linewidth = 2, style = plot.style_line)  // plot SlowMA\n'

class SM8B0B4AF482DF1CF4(PinePortBase, IStrategy):
    source_id = "SM_8b0b4af482df1cf4"
    source_file = '移动平均线双轨与趋势跟踪策略Dual-Moving-Average-Channel-with-Trend-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fastMA': 7, 'slowMA': 14, 'fromMonth': 9, 'fromDay': 1, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2022, 'showDate': True, 'adxlen': 14, 'dilen': 14, 'keyLevel': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
