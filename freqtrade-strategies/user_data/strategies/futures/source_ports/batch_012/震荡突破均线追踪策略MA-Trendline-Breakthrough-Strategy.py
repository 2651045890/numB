"""batch_012 port of 震荡突破均线追踪策略MA-Trendline-Breakthrough-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-23 00:00:00\nend: 2023-03-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n\n//@version=5\n\n//exapple bot\nstrategy(\'RIPO BOT\', shorttitle=\'RIPO BOT\', overlay=true, process_orders_on_close=true, calc_on_order_fills=false, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\nsl_inp = input(0.1, title=\'Stop Loss %\') / 100\ntp_inp = input(0.33, title=\'Take Profit %\') / 100\n\nlength = input(defval=21)\nupper = ta.highest(length)\nlower = ta.lowest(length)\n\nlengthChop = input.int(14, minval=1)\nci = 100 * math.log10(math.sum(ta.atr(1), lengthChop) / (ta.highest(lengthChop) - ta.lowest(lengthChop))) / math.log10(lengthChop)\noffset = input.int(0, "Offset",  minval = -500, maxval = 500)\nplot(ci, "CHOP", color=#2962FF, offset = offset)\nband1 = hline(61.8, "Upper Band", color=#787B86, linestyle=hline.style_dashed)\nhline(50, "Middle Band", color=color.new(#787B86, 50))\nband0 = hline(38.2, "Lower Band", color=#787B86, linestyle=hline.style_dashed)\nfill(band1, band0, color = color.rgb(33, 150, 243, 90), title = "Background")\n\nrsi = ta.rsi(close, 14)\n\nvar float entry_price = na\n\noutput = 100 * (close - upper) / (upper - lower)\nema = ta.ema(output, input(defval=13, title=\'EMA\'))\n\nma(src, len) =>\n    ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), math.round(math.sqrt(len)))\nBBMC = ma(close, 60)\nrangema = ta.ema(ta.tr, 60)\nupperk = BBMC + rangema * 0.2\nlowerk = BBMC - rangema * 0.2\ncolor_bar = close > upperk ? color.blue : close < lowerk ? color.fuchsia : color.gray\n\nExitHigh = ma(high, 15)\nExitLow = ma(low, 15)\nHlv3 = int(na)\nHlv3 := close > ExitHigh ? 1 : close < ExitLow ? -1 : Hlv3[1]\nsslExit = Hlv3 < 0 ? ExitHigh : ExitLow\nbase_cross_Long = ta.crossover(close, sslExit)\nbase_cross_Short = ta.crossover(sslExit, close)\ncodiff = base_cross_Long ? 1 : base_cross_Short ? -1 : na\nentry_long = false\n\nentry_short = false\n\n    \nif ta.crossover(close, BBMC) and output > ema\n    entry_long := true\n    \nif ta.crossunder(close, BBMC) and output < ema\n    entry_short := true\n\nif entry_long and strategy.position_size == 0\n    entry_price := close\n    strategy.entry(\'enter long\', strategy.long, comment=\'ENTER-LONG_BYBIT_MATICUSDT_BOT-NAME_1M_85915e4dc80fb663\')\nif strategy.position_size > 0\n    strategy.exit(\'Stop Loss/TP long\', \'enter long\', limit=entry_price * (1 + tp_inp), stop = color_bar == color.fuchsia ? BBMC : na, comment=\'EXIT-LONG_BYBIT_MATICUSDT_BOT-NAME_1M_85915e4dc80fb663\')\nplot(entry_price * (1 + tp_inp), color=color.new(color.green, 0))\n\n\n//if entry_short and strategy.position_size == 0\n    //entry_price := close\n    //strategy.entry(\'enter short\', strategy.short, comment=\'ENTER-SHORT_BYBIT_MATICUSDT_BOT-NAME_1M_85915e4dc80fb663\')\nif strategy.position_size < 0\n    strategy.exit(\'Stop Loss/TP short\', \'enter short\', limit=entry_price * (1 - tp_inp), stop = color_bar == color.blue ? BBMC : na, comment=\'EXIT-SHORT_BYBIT_MATICUSDT_BOT-NAME_1M_85915e4dc80fb663\')\nplot(entry_price * (1 + tp_inp), color=color.new(color.green, 0))\n// plot(entry_price * (1 - sl_inp), color=color.new(color.red, 0))\n\nplot(rsi, color=color.yellow)\n\nplot(output, title=\'%R\', color=color.new(color.yellow, 0), linewidth=2)\nplot(ema, title=\'EMA\', color=color.new(color.aqua, 0), linewidth=2)\n\nplotarrow(codiff, colorup=color.new(color.blue, 35), colordown=color.new(color.fuchsia, 35), title=\'Exit Arrows\', maxheight=20, offset=0)\nplot(BBMC, color=color_bar, linewidth=4, title=\'MA Trendline\')\n\n\n\n\n'

class SMMATrendlineBreakthroughStrategy361c46(PinePortBase, IStrategy):
    source_id = "SM_361c4645f48f658f"
    source_file = '震荡突破均线追踪策略MA-Trendline-Breakthrough-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 21, 'lengthChop': 14, 'offset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
