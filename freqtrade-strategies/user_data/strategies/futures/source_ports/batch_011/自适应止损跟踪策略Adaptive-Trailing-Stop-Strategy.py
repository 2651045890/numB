"""batch_011 port of 自适应止损跟踪策略Adaptive-Trailing-Stop-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-07 00:00:00\nend: 2023-10-07 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="UT Bot Strategy", overlay = true)\n//CREDITS to HPotter for the orginal code. The guy trying to sell this as his own is a scammer lol. \n\n// Inputs\na = input(1,     title = "Key Vaule. \'This changes the sensitivity\'")\nc = input(10,    title = "ATR Period")\nh = input(false, title = "Signals from Heikin Ashi Candles")\n\n////////////////////////////////////////////////////////////////////////////////\n// BACKTESTING RANGE\n \n// From Date Inputs\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2019, title = "From Year", minval = 1970)\n \n// To Date Inputs\ntoDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2100, title = "To Year", minval = 1970)\n \n// Calculate start/end date and time condition\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n \n////////////////////////////////////////////////////////////////////////////////\n\n\nxATR  = atr(c)\nnLoss = a * xATR\n\nsrc = h ? security(heikinashi(syminfo.tickerid), timeframe.period, close, lookahead = false) : close\n\nxATRTrailingStop = 0.0\nxATRTrailingStop := iff(src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0), max(nz(xATRTrailingStop[1]), src - nLoss),\n   iff(src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0), min(nz(xATRTrailingStop[1]), src + nLoss), \n   iff(src > nz(xATRTrailingStop[1], 0), src - nLoss, src + nLoss)))\n \npos = 0   \npos :=\tiff(src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0), 1,\n   iff(src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0), -1, nz(pos[1], 0))) \n   \nxcolor = pos == -1 ? color.red: pos == 1 ? color.green : color.blue \n\nema   = ema(src,1)\nabove = crossover(ema, xATRTrailingStop)\nbelow = crossover(xATRTrailingStop, ema)\n\nbuy  = src > xATRTrailingStop and above \nsell = src < xATRTrailingStop and below\n\nbarbuy  = src > xATRTrailingStop \nbarsell = src < xATRTrailingStop \n\nplotshape(buy,  title = "Buy",  text = \'Buy\',  style = shape.labelup,   location = location.belowbar, color= color.green, textcolor = color.white, transp = 0, size = size.tiny)\nplotshape(sell, title = "Sell", text = \'Sell\', style = shape.labeldown, location = location.abovebar, color= color.red,   textcolor = color.white, transp = 0, size = size.tiny)\n\nbarcolor(barbuy  ? color.green : na)\nbarcolor(barsell ? color.red   : na)\n\nstrategy.entry("long",   true, when = buy  and time_cond)\nstrategy.entry("short", false, when = sell and time_cond)'

class SM059F77F7359B1DBA(PinePortBase, IStrategy):
    source_id = "SM_059f77f7359b1dba"
    source_file = '自适应止损跟踪策略Adaptive-Trailing-Stop-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'a': 1, 'c': 10, 'h': False, 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2019, 'toDay': 1, 'toMonth': 1, 'toYear': 2100}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
