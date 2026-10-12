"""batch_012 port of 金叉死叉动态止损策略Trend-Following-Strategy-with-Dynamic-Stops.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-25 00:00:00\nend: 2023-10-31 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="UT Bot Strategy", overlay = true)\n//CREDITS to HPotter for the orginal code. The guy trying to sell this as his own is a scammer lol. \n\n// Inputs\na = input(1,     title = "Key Vaule. \'This changes the sensitivity\'")\nc = input(10,    title = "ATR Period")\nh = input(false, title = "Signals from Heikin Ashi Candles")\n\nxATR  = atr(c)\nnLoss = a * xATR\n\nsrc = h ? security(heikinashi(syminfo.tickerid), timeframe.period, close, lookahead = false) : close\n\nxATRTrailingStop = 0.0\nxATRTrailingStop := iff(src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0), max(nz(xATRTrailingStop[1]), src - nLoss),\n   iff(src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0), min(nz(xATRTrailingStop[1]), src + nLoss), \n   iff(src > nz(xATRTrailingStop[1], 0), src - nLoss, src + nLoss)))\n \npos = 0   \npos :=\tiff(src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0), 1,\n   iff(src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0), -1, nz(pos[1], 0))) \n   \nxcolor = pos == -1 ? color.red: pos == 1 ? color.green : color.blue \n\nema   = ema(src,1)\nabove = crossover(ema, xATRTrailingStop)\nbelow = crossover(xATRTrailingStop, ema)\n\nbuy  = src > xATRTrailingStop and above \nsell = src < xATRTrailingStop and below\n\nbarbuy  = src > xATRTrailingStop \nbarsell = src < xATRTrailingStop \n\nplotshape(buy,  title = "Buy",  text = \'Buy\',  style = shape.labelup,   location = location.belowbar, color= color.green, textcolor = color.white, transp = 0, size = size.tiny)\nplotshape(sell, title = "Sell", text = \'Sell\', style = shape.labeldown, location = location.abovebar, color= color.red,   textcolor = color.white, transp = 0, size = size.tiny)\n\nbarcolor(barbuy  ? color.green : na)\nbarcolor(barsell ? color.red   : na)\n\nstrategy.entry("long",   true, when = buy)\nstrategy.entry("short", false, when = sell)\n'

class SMTrendFollowingStrategywithDynamicStops599f3c(PinePortBase, IStrategy):
    source_id = "SM_599f3c6dbef1aa00"
    source_file = '金叉死叉动态止损策略Trend-Following-Strategy-with-Dynamic-Stops.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'a': 1, 'c': 10, 'h': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
