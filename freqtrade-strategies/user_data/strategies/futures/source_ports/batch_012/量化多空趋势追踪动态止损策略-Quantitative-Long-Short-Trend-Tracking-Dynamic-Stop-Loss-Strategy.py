"""batch_012 port of 量化多空趋势追踪动态止损策略-Quantitative-Long-Short-Trend-Tracking-Dynamic-Stop-Loss-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-01 00:00:00\nend: 2025-04-02 00:00:00\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=6\nstrategy("ducanhmaster v1", overlay=true, commission_type=strategy.commission.percent, commission_value=0.1, slippage=3, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// Inputs\na = input.int(1, title="Key Value. \'This changes the sensitivity\'")\nc = input.int(10, title="ATR Period")\nh = input.bool(false, title="Signals from Heikin Ashi Candles")\n\nxATR  = ta.atr(c)\nnLoss = a * xATR\n\n// Compute Heikin Ashi values\nheikinAshiOpen = (open + close) / 2\nheikinAshiClose = (open + high + low + close) / 4\nheikinAshiHigh = math.max(high, math.max(heikinAshiOpen, heikinAshiClose))\nheikinAshiLow = math.min(low, math.min(heikinAshiOpen, heikinAshiClose))\n\nsrc = h ? heikinAshiClose : close\n\n// Declare xATRTrailingStop as a float variable and initialize it with \'na\'\nvar float xATRTrailingStop = na\nif (src > nz(xATRTrailingStop[1], 0) and src[1] > nz(xATRTrailingStop[1], 0))\n    xATRTrailingStop := math.max(nz(xATRTrailingStop[1]), src - nLoss)\nelse if (src < nz(xATRTrailingStop[1], 0) and src[1] < nz(xATRTrailingStop[1], 0))\n    xATRTrailingStop := math.min(nz(xATRTrailingStop[1]), src + nLoss)\nelse\n    xATRTrailingStop := src > nz(xATRTrailingStop[1], 0) ? src - nLoss : src + nLoss\n\n// Declare \'pos\' as an integer variable instead of leaving it undefined\nvar int pos = na\nif (src[1] < nz(xATRTrailingStop[1], 0) and src > nz(xATRTrailingStop[1], 0))\n    pos := 1\nelse if (src[1] > nz(xATRTrailingStop[1], 0) and src < nz(xATRTrailingStop[1], 0))\n    pos := -1\nelse\n    pos := nz(pos[1], 0)\n\nxcolor = pos == -1 ? color.red : pos == 1 ? color.green : color.blue\n\nema = ta.ema(src, 1)\nabove = ta.crossover(ema, xATRTrailingStop)\nbelow = ta.crossover(xATRTrailingStop, ema)\n\nbuy  = src > xATRTrailingStop and above\nsell = src < xATRTrailingStop and below\n\nbarbuy  = src > xATRTrailingStop\nbarsell = src < xATRTrailingStop\n\n// Plot buy/sell signals on the chart\nplotshape(buy, title="Buy", text=\'Buy\', style=shape.labelup, location=location.belowbar, color=color.new(color.green, 0), textcolor=color.white, size=size.tiny)\nplotshape(sell, title="Sell", text=\'Sell\', style=shape.labeldown, location=location.abovebar, color=color.new(color.red, 0), textcolor=color.white, size=size.tiny)\n\n// Change bar color when buy/sell conditions are met\nbarcolor(barbuy ? color.green : na)\nbarcolor(barsell ? color.red : na)\n\n// Enter a Long trade when a buy signal appears and exit when a sell signal appears\nif (buy)\n    strategy.entry("long", strategy.long)\n\nif (sell)\n    strategy.close("long")\n\n'

class SMQuantitativeLongShortTrendTrackingDynamicStopLossStrate53a182(PinePortBase, IStrategy):
    source_id = "SM_53a1822fe246724d"
    source_file = '量化多空趋势追踪动态止损策略-Quantitative-Long-Short-Trend-Tracking-Dynamic-Stop-Loss-Strategy.md'
    timeframe = '3h'
    can_short = False
    source_defaults = {'a': 1, 'c': 10, 'h': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
