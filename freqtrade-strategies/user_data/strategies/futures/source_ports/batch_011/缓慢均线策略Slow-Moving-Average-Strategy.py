"""batch_011 port of 缓慢均线策略Slow-Moving-Average-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-06 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Mysteriown\n\n//@version=4\n\nstrategy("Lagged Donchian Channel + EMA", overlay = true)\n\n//tradePeriod = time(timeframe.period,"0000-0000:1234567")?true:false\n\n\n// ------------------------------------------ //\n// ----------------- Inputs ----------------- //\n// ------------------------------------------ //\n\nperiod = input(24, title="Channel\'s periods")\nPema = input(200, title="EMA\'s periods ?")\nratio = input(3, title="Ratio TP", type=input.float)\nloss = input(20, title="Risk Loss ($)")\nlev = input(5, title="Leverage *...")\nchan = input(title="Plot channel ?", type=input.bool, defval=false)\nBpos = input(title="Plot Bull positions ?", type=input.bool, defval=false)\nbpos = input(title="Plot Bear positions ?", type=input.bool, defval=false)\nlabels = input(title="Plot labels of bets ?", type=input.bool, defval=true)\nsupp = input(title="Delete last labels ?", type=input.bool, defval=true)\n\n\n// ------------------------------------------ //\n// ---------- Canal, EMA and arrow ---------- //\n// ------------------------------------------ //\n\npema = ema(close,Pema)\nplot(pema, title="EMA", color=color.blue)\n\ncanalhaut = highest(period)[1]\ncanalbas = lowest(period)[1]\n\nbear = close[1] > canalhaut[1] and close < open and high > pema\nbull = close[1] < canalbas[1] and open < close and low < pema\n\ncanalhautplot = plot(chan? canalhaut:na, color=color.yellow)\ncanalbasplot = plot(chan? canalbas:na, color=color.yellow)\n\nplotshape(bear, title=\'Bear\', style=shape.triangledown, location=location.abovebar, color=color.red, offset=0)\nplotshape(bull, title=\'Bull\', style=shape.triangleup, location=location.belowbar, color=color.green, offset=0)\n\n\n// ------------------------------------------ //\n// ------------- Position Short ------------- //\n// ------------------------------------------ //\n\nSlShort = highest(3)\nBidShort = close[1]\n\nTpShort = BidShort-((SlShort-BidShort)*ratio)\ndeltaShort = (SlShort-BidShort)/BidShort\nbetShort = round(loss/(lev*deltaShort)*100)/100\ncryptShort = round(betShort*lev/BidShort*1000)/1000\n\n// if bear[1] and labels //and low < low[1]\n//     Lbear = label.new(bar_index, na, text="SHORT\\n\\nSL: " + tostring(SlShort) + "\\n\\nBid: " + tostring(BidShort) + "\\n\\nTP: " + tostring(TpShort) + "\\n\\nMise: " + tostring(betShort) + "\\n\\nCryptos: " + tostring(cryptShort), color=color.red, textcolor=color.white, style=label.style_labeldown, yloc=yloc.abovebar)\n//     label.delete(supp ? Lbear[1] : na)\n\nvar bentry=0.0\nvar bsl=0.0\nvar btp=0.0\n\nif bear[1] and low < low[1]\n    bentry:=BidShort\n    bsl:=SlShort\n    btp:=TpShort\n    \npbentry = plot(bpos? bentry:na, color=color.orange)\nplot(bpos? (bentry+btp)/2:na, color=color.gray)\npbsl = plot(bpos? bsl:na, color=color.red)\npbtp = plot(bpos? btp:na, color=color.green)\n\nfill(pbentry,pbsl, color.red, transp=70)\nfill(pbentry,pbtp, color.green, transp=70)\n\n\n// ------------------------------------------ //\n// ------------- Position Long -------------- //\n// ------------------------------------------ //\n\nSlLong = lowest(3)\nBidLong = close[1]\n\nTpLong = BidLong + ((BidLong - SlLong) * ratio)\ndeltaBull = (BidLong - SlLong)/BidLong\nbetLong = round(loss/(lev*deltaBull)*100)/100\ncryptLong = round(betLong*lev/BidLong*1000)/1000\n\n// if bull[1] and labels //and high > high[1]\n//     Lbull = label.new(bar_index, na, text="LONG\\n\\nSL: " + tostring(SlLong) + "\\n\\nBid: " + tostring(BidLong) + "\\n\\nTP: " + tostring(TpLong) + "\\n\\nMise: " + tostring(betLong) + "\\n\\nCryptos: " + tostring(cryptLong), color=color.green, textcolor=color.white, style=label.style_labelup, yloc=yloc.belowbar)\n//     label.delete(supp ? Lbull[1] : na)\n\nvar Bentry=0.0\nvar Bsl=0.0\nvar Btp=0.0\n\nif bull[1] and high > high[1]\n    Bentry:=BidLong\n    Bsl:=SlLong\n    Btp:=TpLong\n    \npBentry = plot(Bpos?Bentry:na, color=color.orange)\nplot(Bpos?(Bentry+Btp)/2:na, color=color.gray)\npBsl = plot(Bpos?Bsl:na, color=color.red)\npBtp = plot(Bpos?Btp:na, color=color.green)\n\nfill(pBentry,pBsl, color.red, transp=70)\nfill(pBentry,pBtp, color.green, transp=70)\n\n\n// ------------------------------------------ //\n// --------------- Strategie ---------------- //\n// ------------------------------------------ //\n\nBear = bear[1] and low < low[1]\nBull = bull[1] and high > high[1]\n\nif (Bear and strategy.opentrades==0)\n    strategy.order("short", false, 1, limit=BidShort)\n    strategy.exit("exit", "short", limit = TpShort, stop = SlShort)\n\nstrategy.cancel("short", when = high > SlShort or low < (BidShort+TpShort)/2)\nstrategy.close("short", when=bull)\n\nif (Bull and strategy.opentrades==0)\n    strategy.order("long", true, 1, limit=BidLong)\n    strategy.exit("exit", "long", limit = TpLong, stop = SlLong)\n    \nstrategy.cancel("long", when = low < SlLong or high > (BidLong+TpLong)/2)\nstrategy.close("long", when=bear)\n'

class SM52E977F0830A9594(PinePortBase, IStrategy):
    source_id = "SM_52e977f0830a9594"
    source_file = '缓慢均线策略Slow-Moving-Average-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'period': 24, 'Pema': 200, 'ratio': 3, 'loss': 20, 'lev': 5, 'chan': False, 'Bpos': False, 'bpos': False, 'labels': True, 'supp': True}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order', 'var_state', 'timeframe', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
