"""batch_012 port of 通道突破均线跟踪策略Trend-Following-Channel-Breakout-Strategy-with-Moving-Average-and-Trailing-Stop.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-21 23:59:59\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Generalized SSL Backtest w/ TSSL", shorttitle="GSSL Backtest", overlay=true )\n// Generalized SSL:\n//  This is the very first time the SSL indicator, whose acronym I ignore, is on Tradingview. \n//  It is based on moving averages of the highs and lows. \n//  Similar channel indicators can be found, whereas \n//  this one implements the persistency inside the channel, which is rather tricky.\n//  The green line is the base line which decides entries and exits, possibly with trailing stops.\n//  With respect to the original version, here one can play with different moving averages.\n//  The default settings are (10,SMA)\n//\n// Vitelot/Yanez/Vts March 2019\n\nlb = input(10, title="Lb", minval=1)\nmaType = input( defval="SMA", title="MA Type", options=["SMA","EMA","HMA","McG","WMA","Tenkan"])\n\nfixedSL = input(title="SL Activation", defval=300)\ntrailSL = input(title="SL Trigger", defval=1)\nfixedTP = input(title="TP Activation", defval=150)\ntrailTP = input(title="TP Trigger", defval=1)\n\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2019, title = "From Year", minval = 2017)\nToMonth   = input(defval = 6, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 19, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 2020, title = "To Year", minval = 2017)\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nstartTimeOk()  => true // create function "within window of time" if statement true\n// QUANDL:BCHAIN/ETRVU is USD-denominated daily transaction value on BTC blockchain\n// QUANDL:BCHAIN/MKTCP is USD-denominated Bitcoin marketcap\n\nhma(sig, n) => // Hull moving average definition\n    wma( 2*wma(sig,round(n/2))-wma(sig,n), round(sqrt(n)))\n\nmcg(sig,length) => // Mc Ginley MA definition\n    mg = 0.0\n    mg := na(mg[1]) ? ema(sig, length) : mg[1] + (sig - mg[1]) / (length * pow(sig/mg[1], 4))\n\ntenkan(sig,len) =>\n    0.5*(highest(sig,len)+lowest(sig,len))\n\nma(t,sig,len) =>\n    sss=na\n    if t =="SMA"\n        sss := sma(sig,len)\n    if t == "EMA"\n        sss := ema(sig,len)\n    if t == "HMA"\n        sss := hma(sig,len)\n    if t == "McG" // Mc Ginley\n        sss := mcg(sig,len)\n    if t == "Tenkan"\n        sss := tenkan(sig,len)\n    if t == "WMA"\n        sss := wma(sig,len)\n    sss\n\nbase(mah, mal) =>\n    bbb = na\n    inChannel = close<mah and close>mal\n    belowChannel = close<mah and close<mal\n    bbb := inChannel? bbb[1]: belowChannel? -1: 1\n    uuu = bbb==1? mal: mah\n    ddd = bbb==1? mah: mal\n    [uuu, ddd]\n\nmaH = ma(maType, high, lb)\nmaL = ma(maType, low, lb)\n\n[up, dn] = base(maH,maL)\n\nplot(up, title="High MA", color=lime, linewidth=3)\nplot(dn, title="Low MA", color=orange, linewidth=3)\n\nlong = crossover(dn,up)\nshort = crossover(up,dn)\n\n// === STRATEGY - LONG POSITION EXECUTION ===\nstrategy.entry("Long", strategy.long, when= long and startTimeOk())\nstrategy.exit("Exit", qty_percent = 100, loss=fixedSL, trail_offset=trailTP, trail_points=fixedTP) \nstrategy.exit("Exit", when= short)\n// === STRATEGY - SHORT POSITION EXECUTION ===\nstrategy.entry("Short", strategy.short, when= short and startTimeOk())\nstrategy.exit("Exit", qty_percent = 100, loss=fixedSL, trail_offset=trailTP, trail_points=fixedTP)\nstrategy.exit("Exit", when= long)\n'

class SMTrendFollowingChannelBreakoutStrategywithMovingAveragea3aebec(PinePortBase, IStrategy):
    source_id = "SM_3aebecee43a07ffe"
    source_file = '通道突破均线跟踪策略Trend-Following-Channel-Breakout-Strategy-with-Moving-Average-and-Trailing-Stop.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'lb': 10, 'maType': 'SMA', 'fixedSL': 300, 'trailSL': 1, 'fixedTP': 150, 'trailTP': 1, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2019, 'ToMonth': 6, 'ToDay': 19, 'ToYear': 2020}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
