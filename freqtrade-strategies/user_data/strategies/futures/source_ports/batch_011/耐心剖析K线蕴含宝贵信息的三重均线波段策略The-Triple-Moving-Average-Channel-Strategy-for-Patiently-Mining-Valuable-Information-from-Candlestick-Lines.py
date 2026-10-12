"""batch_011 port of 耐心剖析K线蕴含宝贵信息的三重均线波段策略The-Triple-Moving-Average-Channel-Strategy-for-Patiently-Mining-Valuable-Information-from-Candlestick-Lines.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-25 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//╭╮╱╱╭╮╭╮╱╱╭╮\n//┃╰╮╭╯┃┃┃╱╱┃┃\n//╰╮┃┃╭┻╯┣╮╭┫╰━┳╮╭┳━━╮\n//╱┃╰╯┃╭╮┃┃┃┃╭╮┃┃┃┃━━┫\n//╱╰╮╭┫╰╯┃╰╯┃╰╯┃╰╯┣━━┃\n//╱╱╰╯╰━━┻━━┻━━┻━━┻━━╯\n//╭━━━┳╮╱╱╱╱╱╱╱╭╮\n//┃╭━╮┃┃╱╱╱╱╱╱╱┃┃\n//┃┃╱╰┫╰━┳━━┳━╮╭━╮╭━━┫┃\n//┃┃╱╭┫╭╮┃╭╮┃╭╮┫╭╮┫┃━┫┃\n//┃╰━╯┃┃┃┃╭╮┃┃┃┃┃┃┃┃━┫╰╮\n//╰━━━┻╯╰┻╯╰┻╯╰┻╯╰┻━━┻━╯\n//━╯\n// http://www.vdubus.co.uk/\nstrategy(title=\'Vdub FX SniperVX3 / Strategy  v3\', shorttitle=\'Vdub_FX_SniperVX3_Strategy\', overlay=true, pyramiding=0, initial_capital=1000, currency=currency.USD)\n\n//Candle body resistance Channel-----------------------------//\nlen = 34\nsrc = input(close, title="Candle body resistance Channel")\nout = sma(src, len)\nlast8h = highest(close, 13)\nlastl8 = lowest(close, 13)\nbearish = cross(close,out) == 1 and falling(close, 1)\nbullish = cross(close,out) == 1 and rising(close, 1)\nchannel2=input(false, title="Bar Channel On/Off")\nul2=plot(channel2?last8h:last8h==nz(last8h[1])?last8h:na, color=black, linewidth=1, style=linebr, title="Candle body resistance level top", offset=0)\nll2=plot(channel2?lastl8:lastl8==nz(lastl8[1])?lastl8:na, color=black, linewidth=1, style=linebr, title="Candle body resistance level bottom", offset=0)\n//fill(ul2, ll2, color=black, transp=95, title="Candle body resistance Channel")\n\n//-----------------Support and Resistance \nRST = input(title=\'Support / Resistance length:\', defval=10) \nRSTT = valuewhen(high >= highest(high, RST), high, 0)\nRSTB = valuewhen(low <= lowest(low, RST), low, 0)\nRT2 = plot(RSTT, color=RSTT != RSTT[1] ? na : red, linewidth=1, offset=+0)\nRB2 = plot(RSTB, color=RSTB != RSTB[1] ? na : green, linewidth=1, offset=0)\n\n//--------------------Trend colour ema------------------------------------------------// \nsrc0 = close, len0 = input(13, minval=1, title="EMA 1")\nema0 = ema(src0, len0)\ndirection = rising(ema0, 2) ? +1 : falling(ema0, 2) ? -1 : 0\nplot_color = direction > 0  ? lime: direction < 0 ? red : na\nplot(ema0, title="EMA", style=line, linewidth=1, color = plot_color)\n\n//-------------------- ema 2------------------------------------------------//\nsrc02 = close, len02 = input(21, minval=1, title="EMA 2")\nema02 = ema(src02, len02)\ndirection2 = rising(ema02, 2) ? +1 : falling(ema02, 2) ? -1 : 0\nplot_color2 = direction2 > 0  ? lime: direction2 < 0 ? red : na\nplot(ema02, title="EMA Signal 2", style=line, linewidth=1, color = plot_color2)\n\n//=============Hull MA//\nshow_hma = input(false, title="Display Hull MA Set:")\nhma_src = input(close, title="Hull MA\'s Source:")\nhma_base_length = input(8, minval=1, title="Hull MA\'s Base Length:")\nhma_length_scalar = input(5, minval=0, title="Hull MA\'s Length Scalar:")\nhullma(src, length)=>wma(2*wma(src, length/2)-wma(src, length), round(sqrt(length)))\nplot(not show_hma ? na : hullma(hma_src, hma_base_length+hma_length_scalar*6), color=black, linewidth=2, title="Hull MA")\n\n//============ signal Generator ==================================//\nPiriod=input(\'720\')\nch1 = request.security(syminfo.tickerid, Piriod, open)\nch2 = request.security(syminfo.tickerid, Piriod, close)\nlongCondition = crossover(request.security(syminfo.tickerid, Piriod, close),request.security(syminfo.tickerid, Piriod, open))\nif (longCondition)\n    strategy.entry("BUY", strategy.long)\nshortCondition = crossunder(request.security(syminfo.tickerid, Piriod, close),request.security(syminfo.tickerid, Piriod, open))\nif (shortCondition)\n    strategy.entry("SELL", strategy.short)\n\n///////////////////////////////////////////////////////////////////////////////////////////'

class SM14E4B221A0159DD9(PinePortBase, IStrategy):
    source_id = "SM_14e4b221a0159dd9"
    source_file = '耐心剖析K线蕴含宝贵信息的三重均线波段策略The-Triple-Moving-Average-Channel-Strategy-for-Patiently-Mining-Valuable-Information-from-Candlestick-Lines.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'channel2': False, 'RST': 10, 'show_hma': False, 'hma_base_length': 8, 'hma_length_scalar': 5, 'Piriod': '720'}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
