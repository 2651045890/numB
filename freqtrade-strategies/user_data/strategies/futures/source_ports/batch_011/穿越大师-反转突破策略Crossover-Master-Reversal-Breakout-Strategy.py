"""batch_011 port of 穿越大师-反转突破策略Crossover-Master-Reversal-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-13 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("CDC Action Zone V.2 strategy", overlay=true)\n// Credit Script base from CDC Action Zone V.2 by piriya33\n// CDC ActionZone V2 29 Sep 2016\n// CDC ActionZone is based on a simple 2MA and is most suitable for use with medium volatility market\n// 11 Nov 2016 : Ported to Trading View with minor UI enhancement\n\nsrc = input(title="Data Array",defval=ohlc4)\nprd1=input(title="Short MA period",defval=12)\nprd2=input(title="Long MA period",defval=26)\nAP = ema(src,2)\nFast = ema(AP,prd1)\nSlow = ema(AP,prd2)\n\n// === INPUT BACKTEST RANGE ===\nFromYear  = input(defval = 2019, title = "From Year", minval = 2009)\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999, title = "To Year", minval = 2009)\nToMonth   = input(defval = 12, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 31, title = "To Day", minval = 1, maxval = 31)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false // create function "within window of time"\n\nBullish = Fast>Slow\nBearish = Fast<Slow\n\nGreen = Bullish and AP>Fast\nRed = Bearish and AP<Fast\nYellow = Bullish and AP<Fast\nBlue = Bearish and AP>Fast\n\n//Long Signal\nBuy = Green and Green[1]==0\nSell = Red and Red[1]==0\n\n//Short Signal\nShort = Red and Red[1]==0\nCover = Red[1] and Red==0\n\n//Plot\n\nl1=plot(Fast,"Fast", linewidth=1,color=red)\nl2=plot(Slow,"Slow", linewidth=2,color=blue)\nbcolor = Green ? lime : Red ? red : Yellow ? yellow : Blue ? blue : white\nbarcolor(color=bcolor)\nfill(l1,l2,bcolor)\n\nstrategy.entry("Buy",true,when=window() and Buy)\nstrategy.close_all(when=window() and Sell)\n'

class SM895B322C0E991333(PinePortBase, IStrategy):
    source_id = "SM_895b322c0e991333"
    source_file = '穿越大师-反转突破策略Crossover-Master-Reversal-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'prd1': 12, 'prd2': 26, 'FromYear': 2019, 'FromMonth': 1, 'FromDay': 1, 'ToYear': 9999, 'ToMonth': 12, 'ToDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
