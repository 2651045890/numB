"""batch_011 port of 移动平均线反弹策略Exponential-Moving-Average-Bounce-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-01 00:00:00\nend: 2023-12-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © tweakerID\n\n// Simple strategy that checks for price bounces over an Exponential Moving Average. If the CLOSE of the candle bounces\n// back from having it\'s LOW below the EMA, then it\'s a Bull Bounce. If the CLOSE of the candle bounces down from having it\'s\n// high above the EMA, then it\'s a Bear Bounce. This logic can be reverted.\n\n//@version=4\nstrategy("EMA Bounce", overlay=true, \n     default_qty_type=strategy.percent_of_equity, \n     default_qty_value=100, \n     initial_capital=10000, \n     commission_value=0.04, \n     calc_on_every_tick=false, \n     slippage=0)\n\ndirection = input(0, title = "Strategy Direction", type=input.integer, minval=-1, maxval=1)\nstrategy.risk.allow_entry_in(direction == 0 ? strategy.direction.all : (direction < 0 ? strategy.direction.short : strategy.direction.long))\n\n/////////////////////// STRATEGY INPUTS ////////////////////////////////////////\ntitle1=input(true, "-----------------Strategy Inputs-------------------")  \n\ni_EMA=input(20, title="EMA Length")\n\n/////////////////////// BACKTESTER /////////////////////////////////////////////\ntitle2=input(true, "-----------------General Inputs-------------------")  \n\n// Backtester General Inputs\ni_SL=input(true, title="Use Swing Stop Loss and Take Profit")\ni_SPL=input(defval=10, title="Swing Point Loopback")\ni_PercIncrement=input(defval=.2, step=.1, title="Swing Point SL Perc Increment")*0.01\ni_TPRRR = input(1.2, step=.1, title="Take Profit Risk Reward Ratio")\n\n// Bought and Sold Boolean Signal\nbought = strategy.position_size > strategy.position_size[1] \n or strategy.position_size < strategy.position_size[1]\n\n// Price Action Stop and Take Profit\nLL=(lowest(i_SPL))*(1-i_PercIncrement)\nHH=(highest(i_SPL))*(1+i_PercIncrement)\nLL_price = valuewhen(bought, LL, 0)\nHH_price = valuewhen(bought, HH, 0)\nentry_LL_price = strategy.position_size > 0 ? LL_price : na \nentry_HH_price = strategy.position_size < 0 ? HH_price : na \ntp=strategy.position_avg_price + (strategy.position_avg_price - entry_LL_price)*i_TPRRR\nstp=strategy.position_avg_price - (entry_HH_price - strategy.position_avg_price)*i_TPRRR\n\n\n/////////////////////// STRATEGY LOGIC /////////////////////////////////////////\n\nEMA=ema(close, i_EMA)\nLowAboveEMA=low > EMA\nLowBelowEMA=low < EMA\nHighAboveEMA=high > EMA\nHighBelowEMA=high < EMA\nBullBounce=LowAboveEMA[1] and LowBelowEMA and close > EMA //and close > open\nBearBounce=HighBelowEMA[1] and HighAboveEMA and close < EMA //and close < open\nplot(EMA)\n\nBUY=BullBounce\nSELL=BearBounce\n\n//Inputs\nDPR=input(false, "Allow Direct Position Reverse")\nreverse=input(false, "Reverse Trades")\n\n// Entries\nif reverse\n    if not DPR\n        strategy.entry("long", strategy.long, when=SELL and strategy.position_size == 0)\n        strategy.entry("short", strategy.short, when=BUY and strategy.position_size == 0)\n    else     \n        strategy.entry("long", strategy.long, when=SELL)\n        strategy.entry("short", strategy.short, when=BUY)\nelse\n    if not DPR \n        strategy.entry("long", strategy.long, when=BUY and strategy.position_size == 0)\n        strategy.entry("short", strategy.short, when=SELL and strategy.position_size == 0)\n    else\n        strategy.entry("long", strategy.long, when=BUY)\n        strategy.entry("short", strategy.short, when=SELL)\n\n\nSL=entry_LL_price\nSSL=entry_HH_price\nTP=tp\nSTP=stp\n\nstrategy.exit("TP & SL", "long", limit=TP, stop=SL, when=i_SL)\nstrategy.exit("TP & SL", "short", limit=STP, stop=SSL, when=i_SL)\n\n/////////////////////// PLOTS //////////////////////////////////////////////////\n\nplot(strategy.position_size > 0 ? SL : na , title=\'SL\', style=plot.style_cross, color=color.red)\nplot(strategy.position_size < 0 ? SSL : na , title=\'SSL\', style=plot.style_cross, color=color.red)\nplot(strategy.position_size > 0 ? TP : na, title=\'TP\', style=plot.style_cross, color=color.green)\nplot(strategy.position_size < 0 ? STP : na, title=\'STP\', style=plot.style_cross, color=color.green)\n// Draw price action setup arrows\nplotshape(BUY ? 1 : na, style=shape.triangleup, location=location.belowbar, \n color=color.green, title="Bullish Setup", transp=80, size=size.auto)\nplotshape(SELL ? 1 : na, style=shape.triangledown, location=location.abovebar, \n color=color.red, title="Bearish Setup", transp=80, size=size.auto)\n'

class SMAE9A457A6B56918C(PinePortBase, IStrategy):
    source_id = "SM_ae9a457a6b56918c"
    source_file = '移动平均线反弹策略Exponential-Moving-Average-Bounce-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'direction': 0, 'title1': True, 'i_EMA': 20, 'title2': True, 'i_SL': True, 'i_SPL': 10, 'i_PercIncrement': 0.2, 'i_TPRRR': 1.2, 'DPR': False, 'reverse': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.04
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
