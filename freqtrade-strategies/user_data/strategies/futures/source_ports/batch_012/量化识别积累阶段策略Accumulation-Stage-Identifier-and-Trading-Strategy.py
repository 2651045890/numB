"""batch_012 port of 量化识别积累阶段策略Accumulation-Stage-Identifier-and-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-13 00:00:00\nend: 2024-02-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © stocktechbot\n\n//@version=5\nstrategy("Accumulate", overlay = true)\nlookback = input(defval = 21, title = \'Lookback\')\noffset = input.int(title="Offset", defval=0, minval=-500, maxval=500)\n//SMA Tredline\nout = ta.sma(close, 200)\noutf = ta.sma(close, 50)\noutn = ta.sma(close, 90)\noutt = ta.sma(close, 21)\n//sma plot\nplot(out, color=color.blue, title="MA200", offset=offset)\nplot(outf, color=color.maroon, title="MA50", offset=offset)\nplot(outn, color=color.orange, title="MA90", offset=offset)\nplot(outt, color=color.olive, title="MA21", offset=offset)\n\n//MarketCap Calculation\n//MarketCap = 0.0\n//TSO = request.financial(syminfo.tickerid, "TOTAL_SHARES_OUTSTANDING", "FQ", ignore_invalid_symbol = true)\n\n\n//if str.tostring(TSO) != \'na\'\n//    if ta.barssince(TSO != TSO[1] and TSO > TSO[1])==0\n//        MarketCap := TSO * close\n//       \n//    if barstate.islast and MarketCap == 0\n//        runtime.error("No MarketCap is provided by the data vendor.")\n//    \n//momlen = 100\n//msrc = MarketCap\n//mom = msrc - msrc[momlen]\n//plotmom = if (mom > mom[1])\n//    true\n//else\n//   false\n\n//OBV with sma on macd\nobv = ta.cum(math.sign(ta.change(close)) * volume)\nsmoothingLength = 5\nsmoothingLine = ta.sma(obv,5)\n[macdLine, signalLine, histLine] = ta.macd(ta.pvt, 12, 26, 9)\nsellvolhigh = macdLine < signalLine\nbuyvolhigh = macdLine > signalLine\n//Buy Signal\nmafentry =ta.sma(close, 50) > ta.sma(close, 90)\n//matentry = ta.sma(close, 21) > ta.sma(close, 50)\nmatwohun = close > ta.sma(close, 200)\nhigheshigh = ta.rising(high, 2)\nhigheslow = ta.rising(low, 2 )\ntwohunraise = ta.rising(out, 2)\n//highvol =  ta.crossover(volume, ta.sma(volume, lookback))\nhighvol = ta.rising(volume,2)\nfourlow = ta.lowest(close, lookback)\nfourhig = ta.highest(close, lookback)\nchange =  (((fourhig - fourlow) / fourlow) * 100) <= 30\ngreen = close > open\nallup = false\nlineabove = ta.cross(close, ta.sma(close, input(defval = 21, title = \'Entry Line\')))\nif matwohun and mafentry and higheshigh and twohunraise and buyvolhigh\n//if higheshigh and higheslow and highvol\n    allup := true\n\nplotshape(allup, style=shape.arrowup,location=location.belowbar, color=color.green, title = "Buy Signal")\n\nbarsSinceLastEntry() =>\n    strategy.opentrades > 0 ? bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) : na\n    \n//Sell Signal\nmafexit =ta.sma(close, 50) < ta.sma(close, 90)\nmatexit = ta.sma(close, 21) < ta.sma(close, 50)\nmatwohund = close < ta.sma(close, 200)\nlinebreak = ta.sma(close, input(defval = 21, title = \'Exit Line\')) > close\nlowesthigh = ta.falling(high, 3)\nlowestlow = ta.falling(low, 2 )\ntwohunfall = ta.falling(out, 3)\ntwentyfall = ta.falling(outt, 2)\nhighvole =  ta.crossover(volume, ta.sma(volume, 5))\n//fourlow = ta.lowest(close, lookback)\n//fourhig = ta.highest(close, lookback)\nchanged =  (((fourhig - close) / close) * 100) >= 10\nred = close < open\natr = ta.atr(14)\n//atrsmalen = int(bar_index - strategy.opentrades.entry_bar_index(strategy.opentrades - 1) )\natrsmalen = barsSinceLastEntry()\natrsma = false\natrlen = 5\nif str.tostring(atrsmalen) != \'NaN\' and atrsmalen > 0\n    atrlen := atrsmalen\n\n    \natrsma := atr > ta.sma(atr,50)\n\n\nalldwn = false\nif sellvolhigh and lowestlow and (close < close[1] and close < open)\n//if higheshigh and higheslow and highvol\n    alldwn := true\n\nplotshape(alldwn, style=shape.arrowdown,location=location.abovebar, color=color.red, title = "Sell Signal")\n\n\nlongCondition = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))\nif (allup)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))\nif (alldwn)\n    strategy.entry("My Short Entry Id", strategy.short)\n\n'

class SMAccumulationStageIdentifierandTradingStrategyc92a7e(PinePortBase, IStrategy):
    source_id = "SM_c92a7e47a0b7dc98"
    source_file = '量化识别积累阶段策略Accumulation-Stage-Identifier-and-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lookback': 21, 'offset': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
