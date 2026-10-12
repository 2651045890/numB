"""batch_012 port of 韦氏布林带交易策略Weis-Wave-Bollinger-Band-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-13 00:00:00\nend: 2023-09-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © sharatgbhat\n\n//@version=4\n// strategy("Weis BB Strategy", overlay=false, default_qty_type = strategy.percent_of_equity, default_qty_value = 10,max_lines_count = 500, max_labels_count = 500)\nmaxIdLossPcnt = input(1, "Max Intraday Loss(%)", type=input.float)\n// strategy.risk.max_intraday_loss(maxIdLossPcnt, strategy.percent_of_equity)\n\nmethod = input(defval="ATR", options=["ATR", "Traditional", "Part of Price"], title="Renko Assignment Method")\nmethodvalue = input(defval=14.0, type=input.float, minval=0, title="Value")\npricesource = input(defval="Close", options=["Close", "Open / Close", "High / Low"], title="Price Source")\nuseClose = pricesource == "Close"\nuseOpenClose = pricesource == "Open / Close" or useClose\nuseTrueRange = input(defval="Auto", options=["Always", "Auto", "Never"], title="Use True Range instead of Volume")\nisOscillating = input(defval=false, type=input.bool, title="Oscillating")\nnormalize = input(defval=false, type=input.bool, title="Normalize")\nvol = useTrueRange == "Always" or useTrueRange == "Auto" and na(volume) ? tr : volume\nop = useClose ? close : open\nhi = useOpenClose ? close >= op ? close : op : high\nlo = useOpenClose ? close <= op ? close : op : low\n\nif method == "ATR"\n    methodvalue := atr(round(methodvalue))\nif method == "Part of Price"\n    methodvalue := close / methodvalue\n\ncurrclose = float(na)\nprevclose = nz(currclose[1])\nprevhigh = prevclose + methodvalue\nprevlow = prevclose - methodvalue\ncurrclose := hi > prevhigh ? hi : lo < prevlow ? lo : prevclose\n\ndirection = int(na)\ndirection := currclose > prevclose ? 1 : currclose < prevclose ? -1 : nz(direction[1])\ndirectionHasChanged = change(direction) != 0\ndirectionIsUp = direction > 0\ndirectionIsDown = direction < 0\n\nbarcount = 1\nbarcount := not directionHasChanged and normalize ? barcount[1] + barcount : barcount\nvol := not directionHasChanged ? vol[1] + vol : vol\nres = barcount > 1 ? vol / barcount : vol\n\nplot(isOscillating and directionIsDown ? -res : res, style=plot.style_columns, color=directionIsUp ? color.green : color.red, transp=75, linewidth=3, title="Wave Volume")\n\nlength = input(14, minval=1)\nsrc = input(close, title="Source")\nmult = input(2, minval=0.001, maxval=50, title="StdDev")\nbasis = sma(src, length)\ndev = mult * stdev(src, length)\nupper = basis + dev\nlower = basis - dev\noffset = input(0, "Offset", type = input.integer, minval = -500, maxval = 500)\nplot(basis, "Basis", color=#FF6D00, offset = offset)\np1 = plot(upper, "Upper", color=#2962FF, offset = offset)\np2 = plot(lower, "Lower", color=#2962FF, offset = offset)\nfill(p1, p2, title = "Background", color=color.rgb(33, 150, 243, 95))\n\nMomentumBull = close>upper\nMomentumBear = close<lower\n\nif (MomentumBull and directionIsUp)\n\tstrategy.entry("Buy", strategy.long)\nif (MomentumBear and directionIsDown)\n\tstrategy.entry("Sell", strategy.short)\n    strategy.exit("exit","Buy",when=directionIsDown,qty_percent=100,profit=20,loss=10)\n    strategy.exit("exit","Sell",when=directionIsUp,qty_percent=100,profit=20,loss=10)\n    \n'

class SMWeisWaveBollingerBandTradingStrategy2cb10d(PinePortBase, IStrategy):
    source_id = "SM_2cb10d6020f82d78"
    source_file = '韦氏布林带交易策略Weis-Wave-Bollinger-Band-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'maxIdLossPcnt': 1, 'method': 'ATR', 'methodvalue': 14.0, 'pricesource': 'Close', 'useTrueRange': 'Auto', 'isOscillating': False, 'normalize': False, 'length': 14, 'src': 'close', 'mult': 2, 'offset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
