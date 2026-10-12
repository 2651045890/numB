"""batch_012 port of 量化追踪牛市策略Quant-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-27 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Combined Strategy", overlay=true)\n\n// Input variables for EMA Crossover\nema13_length = input(13, title="EMA 13 Length")\nema50_length = input(50, title="EMA 50 Length")\nema100_length = input(100, title="EMA 100 Length")\nema200_length = input(200, title="EMA 200 Length")\n\n// Calculate EMAs for EMA Crossover\nema13 = ema(close, ema13_length)\nema50 = ema(close, ema50_length)\nema100 = ema(close, ema100_length)\nema200 = ema(close, ema200_length)\n\n// Plot EMAs for EMA Crossover\nplot(ema13, color=color.blue, title="EMA 13")\nplot(ema50, color=color.orange, title="EMA 50")\nplot(ema100, color=color.green, title="EMA 100")\nplot(ema200, color=color.red, title="EMA 200")\n\n// Input variables for LinReg Candles\nsignal_length = input(title="Signal Smoothing", type=input.integer, minval=1, maxval=200, defval=11)\nsma_signal = input(title="Simple MA (Signal Line)", type=input.bool, defval=true)\n\nlin_reg = input(title="Lin Reg", type=input.bool, defval=true)\nlinreg_length = input(title="Linear Regression Length", type=input.integer, minval=1, maxval=200, defval=11)\n\n// Calculate LinReg Candles\nbopen = lin_reg ? linreg(open, linreg_length, 0) : open\nbhigh = lin_reg ? linreg(high, linreg_length, 0) : high\nblow = lin_reg ? linreg(low, linreg_length, 0) : low\nbclose = lin_reg ? linreg(close, linreg_length, 0) : close\n\nr = bopen < bclose\n\nsignal = sma_signal ? sma(bclose, signal_length) : ema(bclose, signal_length)\n\nplotcandle(r ? bopen : na, r ? bhigh : na, r ? blow: na, r ? bclose : na, title="LinReg Candles", color=color.green, wickcolor=color.green, bordercolor=color.green, editable=true)\nplotcandle(r ? na : bopen, r ? na : bhigh, r ? na : blow, r ? na : bclose, title="LinReg Candles", color=color.red, wickcolor=color.red, bordercolor=color.red, editable=true)\n\nplot(signal, color=color.white)\n\n// Input variables for UT Bot Alerts\na = input(1, title="Key Value. \'This changes the sensitivity\'")\nc = input(10, title="ATR Period")\nh = input(false, title="Signals from Heikin Ashi Candles")\n\n// Calculate UT Bot Alerts\nxATR = atr(c)\nnLoss = a * xATR\n\nsrc = h ? security(heikinashi(syminfo.tickerid), timeframe.period, close, lookahead=false) : close\n\nxATRTrailingStop = 0.0\nxATRTrailingStop := iff(src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0), max(nz(xATRTrailingStop[1]), src - nLoss),\n   iff(src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0), min(nz(xATRTrailingStop[1]), src + nLoss), \n   iff(src > nz(xATRTrailingStop[1], 0), src - nLoss, src + nLoss)))\n\npos = 0   \npos := iff(src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0), 1,\n   iff(src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0), -1, nz(pos[1], 0))) \n\nxcolor = pos == -1 ? color.red: pos == 1 ? color.green : color.blue \n\nema = ema(src,1)\nabove = crossover(ema, xATRTrailingStop)\nbelow = crossover(xATRTrailingStop, ema)\n\nbuy = src > xATRTrailingStop and above \nsell = src < xATRTrailingStop and below\n\nbarbuy = src > xATRTrailingStop \nbarsell = src < xATRTrailingStop \n\nstrategy.entry("Buy", strategy.long, when=buy)\nstrategy.close("Buy", when=sell)\nstrategy.entry("Sell", strategy.short, when=sell)\nstrategy.close("Sell", when=buy)\n\nplotshape(buy, title="Buy", text=\'Buy\', style=shape.labelup, location=location.belowbar, color=color.green, textcolor=color.white, transp=0, size=size.tiny)\nplotshape(sell, title="Sell", text=\'Sell\', style=shape.labeldown, location=location.abovebar, color=color.red, textcolor=color.white, transp=0, size=size.tiny)\n\nbarcolor(barbuy ? color.green : na)\nbarcolor(barsell ? color.red : na)\n\nalertcondition(buy, "UT Long", "UT Long")\nalertcondition(sell, "UT Short", "UT Short")\n\n'

class SMQuantTrendFollowingStrategy0182bc(PinePortBase, IStrategy):
    source_id = "SM_0182bcb3ef4a29d4"
    source_file = '量化追踪牛市策略Quant-Trend-Following-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'ema13_length': 13, 'ema50_length': 50, 'ema100_length': 100, 'ema200_length': 200, 'signal_length': 11, 'sma_signal': True, 'lin_reg': True, 'linreg_length': 11, 'a': 1, 'c': 10, 'h': False}
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
