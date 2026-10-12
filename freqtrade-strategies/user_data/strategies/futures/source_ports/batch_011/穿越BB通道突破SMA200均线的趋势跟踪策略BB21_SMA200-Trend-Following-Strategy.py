"""batch_011 port of 穿越BB通道突破SMA200均线的趋势跟踪策略BB21_SMA200-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-09 00:00:00\nend: 2023-11-15 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © mohanee\n\n//@version=4\nstrategy(title="BB9_MA200_Strategy", overlay=true, pyramiding=1,     default_qty_type=strategy.cash,  initial_capital=10000, currency=currency.USD)  //default_qty_value=10, default_qty_type=strategy.fixed, \n\n\nvar stopLossVal=0.00\n\n//variables BEGIN\nsmaLength=input(200,title="MA Length")\nbbLength=input(21,title="BB Length")  \n\nbbsrc = input(close, title="BB Source")\nmult = input(2.0, minval=0.001, maxval=50, title="StdDev")\n\n\nstopLoss = input(title="Stop Loss%", defval=5, minval=1)\n\nriskCapital = input(title="Risk % of capital  == Based on this trade size is claculated    numberOfShares = (AvailableCapital*risk/100) / stopLossPoints", defval=10, minval=1)\n\n\nsma200=ema(close,smaLength)\n\nplot(sma200, title="SMA 200", color=color.orange)\n\n\n//bollinger calculation\nbasis = sma(bbsrc, bbLength)\ndev = mult * stdev(bbsrc, bbLength)\nupperBand = basis + dev\nlowerBand = basis - dev\noffset = input(0, "Offset", type = input.integer, minval = -500, maxval = 500)\n\n//plot bb\nplot(basis, "Basis", color=color.teal, style=plot.style_circles , offset = offset)\np1 = plot(upperBand, "Upper", color=color.teal, offset = offset)\np2 = plot(lowerBand, "Lower", color=color.teal, offset = offset)\nfill(p1, p2, title = "Background", color=color.teal, transp=95)\n\n\nstrategy.initial_capital = 50000\n\n//Entry---\n\nstrategy.entry(id="LE", comment="LE capital="+tostring(strategy.initial_capital + strategy.netprofit ,"######.##"), qty=( (strategy.initial_capital + strategy.netprofit ) * riskCapital / 100)/(close*stopLoss/100) , long=true,  when=strategy.position_size<1 and upperBand>sma200 and lowerBand > sma200 and crossover(close, basis) )     //  // aroonOsc<0  //(strategy.initial_capital * 0.10)/close\n\n\nbarcolor(color=strategy.position_size>=1? color.blue: na)\n\n//partial Exit\ntpVal=strategy.position_size>1 ? strategy.position_avg_price * (1+(stopLoss/100) ) : 0.00\nstrategy.close(id="LE", comment="Partial points="+tostring(close - strategy.position_avg_price, "####.##"),  qty_percent=30 , when=abs(strategy.position_size)>=1 and close>tpVal and crossunder(lowerBand, sma200)   )   //close<ema55 and rsi5Val<20 //ema34<ema55\n\n\n//close All on stop loss\n//stoploss\nstopLossVal:=   strategy.position_size>1 ? strategy.position_avg_price * (1-(stopLoss/100) ) : 0.00\n\nstrategy.close_all( comment="SL Exit points="+tostring(close - strategy.position_avg_price, "####.##"),  when=abs(strategy.position_size)>=1 and close < stopLossVal  )  //close<ema55 and rsi5Val<20 //ema34<ema55  //close<ema89//\n\nstrategy.close_all( comment="BB9 X SMA200 points="+tostring(close - strategy.position_avg_price, "####.##"),  when=abs(strategy.position_size)>=1 and  crossunder(basis, sma200)  )  //close<ema55 and rsi5Val<20 //ema34<ema55  //close<ema89\n    '

class SM394B13FDBF61AC2A(PinePortBase, IStrategy):
    source_id = "SM_394b13fdbf61ac2a"
    source_file = '穿越BB通道突破SMA200均线的趋势跟踪策略BB21_SMA200-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'smaLength': 200, 'bbLength': 21, 'mult': 2.0, 'stopLoss': 5, 'riskCapital': 10, 'offset': 0}
    source_qty_type = 'cash'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
