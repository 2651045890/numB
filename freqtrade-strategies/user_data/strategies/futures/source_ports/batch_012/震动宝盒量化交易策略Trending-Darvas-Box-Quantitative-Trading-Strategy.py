"""batch_012 port of 震动宝盒量化交易策略Trending-Darvas-Box-Quantitative-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-26 00:00:00\nend: 2023-12-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © xxy_theone\n// https://www.youtube.com/watch?v=YYxlnFOX9sQ\n// This strategy script has been made to backtest the strategy explained in the video above\n\n\n//@version=5\nstrategy(shorttitle = "Darvas Box Test", title="TradeIQ Darvas Box Test", overlay=true, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=100, currency=currency.USD)\n\n// === INPUT BACKTEST RANGE ===\nvar GRP1 = "Backtest Range"\nfromDate = input(timestamp("7 Mar 2022 00:00 +0000"), "From", group=GRP1)\ntoDate = input(timestamp("19 Mar 2022 23:59 +0000"), "To", group=GRP1)\nwindow() =>  true\n\n\nvar GRP3 = "Darvas Box"\nboxp=input(5, "Box Length", group=GRP3)\n\nLL = ta.lowest(low,boxp)\nk1=ta.highest(high,boxp)\nk2=ta.highest(high,boxp-1)\nk3=ta.highest(high,boxp-2)\n\nNH =  ta.valuewhen(high>k1[1],high,0)\nbox1 =k3<k2\nTopBox = ta.valuewhen(ta.barssince(high>k1[1])==boxp-2 and box1, NH, 0)\nBottomBox = ta.valuewhen(ta.barssince(high>k1[1])==boxp-2 and box1, LL, 0)\n\n\nplot(TopBox, linewidth=3, color=color.green, title="TBbox") \nplot(BottomBox, linewidth=3, color=color.red, title="BBbox")\n\n\nvar GRP4 = "MavilimW"\n\nfmal=input(3,"First Moving Average length", group=GRP4)\nsmal=input(5,"Second Moving Average length", group=GRP4)\ntmal=fmal+smal\nFmal=smal+tmal\nFtmal=tmal+Fmal\nSmal=Fmal+Ftmal\n\nM1= ta.wma(close, fmal)\nM2= ta.wma(M1, smal)\nM3= ta.wma(M2, tmal)\nM4= ta.wma(M3, Fmal)\nM5= ta.wma(M4, Ftmal)\nMAVW= ta.wma(M5, Smal)\ncol1= MAVW>MAVW[1]\ncol3= MAVW<MAVW[1]\ncolorM = col1 ? color.blue : col3 ? color.red : color.yellow\n\nplot(MAVW, color=colorM, linewidth=2, title="MAVW")\n\n\nvar GRP5 = "Relative Vigor Index"\nlen = input.int(10, title="Length", minval=1, group=GRP5)\nrvi = math.sum(ta.swma(close-open), len)/math.sum(ta.swma(high-low),len)\nsig = ta.swma(rvi)\noffset = input.int(0, "Offset", minval = -500, maxval = 500, group=GRP5)\n//plot(rvi, color=#008000, title="RVGI", offset = offset)\n//plot(sig, color=#FF0000, title="Signal", offset = offset)\n\n\nvar longStopSet = false\n\nlong = ta.crossover(close,TopBox) and close > MAVW ? true : false\nlongClose = strategy.opentrades.profit(strategy.opentrades-1)>0 and ta.crossunder(rvi,sig) ? true : false\nstrategy.entry("Long Position", strategy.long, when = long and window() and strategy.position_size==0 and strategy.closedtrades<100)\nif(longStopSet==false and strategy.position_size > 0)\n    strategy.exit("exit", "Long Position", stop=BottomBox)\n    longStopSet := true\nif(strategy.position_size==0)\n    longStopSet := false\nstrategy.close("Long Position", when = longClose)\n\nvar shortStopSet = false\n\nshort = ta.crossunder(close,BottomBox) and close < MAVW ? true : false\nshortClose = strategy.opentrades.profit(strategy.opentrades-1)>0 and ta.crossover(rvi,sig) ? true : false\nstrategy.entry("Short Position", strategy.short, when = short and window() and strategy.position_size==0 and strategy.closedtrades<100)\nif(shortStopSet==false and strategy.position_size < 0)\n    strategy.exit("exit", "Short Position", stop=TopBox)\n    shortStopSet := true\nif(strategy.position_size==0)\n    shortStopSet := false\nstrategy.close("Short Position", when = shortClose)\n\n'

class SMTrendingDarvasBoxQuantitativeTradingStrategy87c0d1(PinePortBase, IStrategy):
    source_id = "SM_87c0d1966f33abeb"
    source_file = '震动宝盒量化交易策略Trending-Darvas-Box-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fromDate': 'timestamp("7 Mar 2022 00:00 +0000")', 'toDate': 'timestamp("19 Mar 2022 23:59 +0000")', 'boxp': 5, 'fmal': 3, 'smal': 5, 'len': 10, 'offset': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100
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
