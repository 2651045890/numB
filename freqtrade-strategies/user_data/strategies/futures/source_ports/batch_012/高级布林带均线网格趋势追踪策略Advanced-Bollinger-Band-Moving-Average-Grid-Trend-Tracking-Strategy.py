"""batch_012 port of 高级布林带均线网格趋势追踪策略Advanced-Bollinger-Band-Moving-Average-Grid-Trend-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-24 00:00:00\nend: 2023-11-23 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Aayonga\n\n//@version=5\nstrategy("fib trend grid@Aa", overlay=true)\n\n//回测时间\nuseDateFilter=input.bool(true,title = "启用回测时间范围限定(backtest)", group = "回测范围(backtest)")\nbacktesStarDate=input(timestamp("1 Jan 2015"),title = "开始时间(Start)", group = "回测范围(backtest)")\nbacktestEndDate=input(timestamp("1 Jan 2040"),title = "结束时间(finish)",group = "回测范围(backtest)")\ninTradeWindow=true\n\n\n//入场位 entry\nbolllen=input.int(defval=20,minval=1,title="布林长度,(boll length)",group = "入场位(entry)")\nsma=ta.sma(close,bolllen)\navg=ta.atr(bolllen)\nfib1=input(defval=1.236,title="Fib 1",group = "入场位(entry)")\nfib2=input(defval=2.382,title="Fib 2",group = "入场位(entry)")\nfib3=input(defval=3.618,title="fib 3",group = "入场位(entry)")\nfib4=input(defval=4.236,title="Fib 4",group = "入场位(entry)")\nr1=avg*fib1\nr2=avg*fib2\nr3=avg*fib3\nr4=avg*fib4\ntop4=sma+r4\ntop3=sma+r3\ntop2=sma+r2\ntop1=sma+r1\nbott1=sma-r1\nbott2=sma-r2\nbott3=sma-r3\nbott4=sma-r4\n\n\n\n//趋势 plot\n\nt4=plot(top4,title="卖 (sell)4",color=color.rgb(244, 9, 9))\nt3=plot(top3,title = "卖(sell) 3",color=color.rgb(211, 8, 8))\nt2=plot(top2,title="卖 (sell)2",color=color.rgb(146, 13, 13))\nt1=plot(top1,title="卖(sell) 1",color=color.rgb(100, 3, 3))\n\nb1=plot(bott1,title="买(buy1)1",color=color.rgb(4, 81, 40))\nb2=plot(bott2,title="买(buy)2",color=color.rgb(15, 117, 46))\nb3=plot(bott3,title = "买(buy)3",color =color.rgb(8, 176, 42) )\nb4=plot(bott4,title="买(buy)4",color=color.rgb(15, 226, 103))\nplot(sma,style=plot.style_cross,title="SMA",color=color.rgb(47, 16, 225))\n\n//趋势\nLengthF=input(defval = 25,title = "快线长度(fastlength)")\nLengthS=input(defval=200,title = "慢线长度(slowlength)")\nemaF=ta.ema(close,LengthF)\nsmaS=ta.sma(close,LengthS)\nlongTrend=emaF>smaS\nlongb=ta.crossover(emaF,smaS)\nbgcolor(longb ? color.new(color.green,40):na,title = "多头强势(bull trend)")\nshortTrend=smaS>emaF\nshortb=ta.crossunder(emaF,smaS)\nbgcolor(shortb ? color.new(#951313, 40):na,title = "空头强势(bear trend)")\n\n//pinbar\nbullPinBar = ((close > open) and ((open - low) > 0.6* (high - low))) or ((close < open) and ((close - low) > 0.9 * (high - low)))\n//plotshape(bullPinBar  , text ="pinbar", textcolor=color.rgb(9, 168, 144),location=location.belowbar, color=color.rgb(29, 103, 67), size=size.tiny)\nbearPinBar = ((close > open) and ((high - close) > 0.7 * (high - low))) or ((close < open) and ((high - open) > 0.7 * (high - low)))\n//plotshape(bearPinBar  , text ="pinbar", textcolor=color.rgb(219, 12, 12),location=location.abovebar, color=color.rgb(146, 7, 7), size=size.tiny)\n\nbuy1=ta.crossunder(close,bott1) and longTrend and close>ta.ema(close,100)\nbuy2=ta.crossunder(close,bott2) and longTrend \nbuy3=ta.crossunder(close,bott3) and longTrend \nbuy4=ta.crossunder(close,bott4) and longTrend \nbuyclose=bearPinBar or ta.crossunder(close,smaS)\n\n\n\n\nif buy2 or buy3 or buy4 or buy1 and inTradeWindow\n    strategy.order("多(buy)",strategy.long)\n\nif buyclose  and inTradeWindow\n    strategy.close("多(buy)")\n\nsell1=ta.crossover(close,top1) and shortTrend and close<ta.ema(close,200)\nsell2=ta.crossover(close,top2) and shortTrend and close<ta.ema(close,200)\nsell3=ta.crossover(close,top3) and shortTrend and close<ta.ema(close,200)\nsell4=ta.crossover(close,top4) and shortTrend and close<ta.ema(close,200)\nsellclose=bullPinBar or ta.crossover(close,ta.sma(close,220))\n\nif  sell1 or sell2 or sell3 or sell4 and inTradeWindow\n    strategy.order("空(sell)",strategy.short)\n\nif sellclose  and inTradeWindow\n    strategy.close("空(sell)")\n     \n'

class SMAdvancedBollingerBandMovingAverageGridTrendTrackingStrafce9ef(PinePortBase, IStrategy):
    source_id = "SM_fce9ef8a747799e9"
    source_file = '高级布林带均线网格趋势追踪策略Advanced-Bollinger-Band-Moving-Average-Grid-Trend-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'useDateFilter': True, 'backtesStarDate': 'timestamp("1 Jan 2015")', 'backtestEndDate': 'timestamp("1 Jan 2040")', 'bolllen': 20, 'fib1': 1.236, 'fib2': 2.382, 'fib3': 3.618, 'fib4': 4.236, 'LengthF': 25, 'LengthS': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
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
