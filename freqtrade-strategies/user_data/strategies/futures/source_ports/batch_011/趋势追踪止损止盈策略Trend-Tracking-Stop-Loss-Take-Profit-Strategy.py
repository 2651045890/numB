"""batch_011 port of 趋势追踪止损止盈策略Trend-Tracking-Stop-Loss-Take-Profit-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © zhuenrong\n\n// © Dreadblitz\n//@version=4\nstrategy(shorttitle="FLI", title="Follow Line Indicator", overlay=true)\n// \nBBperiod      = input(defval = 21,     title = "BB Period",    type = input.integer, minval = 1)\nBBdeviations  = input(defval = 1.00,     title = "BB Deviations",    type = input.float, minval = 0.1, step=0.05)\nUseATRfilter  = input(defval = true, title = "ATR Filter",  type = input.bool)\nATRperiod     = input(defval = 5,     title = "ATR Period",    type = input.integer, minval = 1)\nhl            = input(defval = false, title = "Hide Labels",  type = input.bool)\n//\nBBUpper=sma (close,BBperiod)+stdev(close, BBperiod)*BBdeviations\nBBLower=sma (close,BBperiod)-stdev(close, BBperiod)*BBdeviations\n//\nTrendLine = 0.0\niTrend = 0.0\nbuy = 0.0\nsell = 0.0\n//\nBBSignal = close>BBUpper? 1 : close<BBLower? -1 : 0\n// \nif BBSignal == 1 and UseATRfilter == 1\n    TrendLine:=low-atr(ATRperiod)\n    if TrendLine<TrendLine[1] \n        TrendLine:=TrendLine[1]\nif BBSignal == -1 and UseATRfilter == 1\n    TrendLine:=high+atr(ATRperiod)\n    if TrendLine>TrendLine[1]\n        TrendLine:=TrendLine[1]\nif BBSignal == 0 and UseATRfilter == 1\n    TrendLine:=TrendLine[1]\n//\nif BBSignal == 1 and UseATRfilter == 0\n    TrendLine:=low\n    if TrendLine<TrendLine[1] \n        TrendLine:=TrendLine[1]\nif BBSignal == -1 and UseATRfilter == 0\n    TrendLine:=high\n    if TrendLine>TrendLine[1]\n        TrendLine:=TrendLine[1]\nif BBSignal == 0 and UseATRfilter == 0\n    TrendLine:=TrendLine[1]\n//\niTrend:=iTrend[1]\nif TrendLine>TrendLine[1] \n    iTrend:=1\nif TrendLine<TrendLine[1] \n    iTrend:=-1\n//\nbuy:=iTrend[1]==-1 and iTrend==1 ? 1 : na\nsell:=iTrend[1]==1 and iTrend==-1? 1 : na\n//\nplot(TrendLine, color=iTrend > 0?color.blue:color.red ,style=plot.style_line,linewidth=2,transp=0,title="Trend Line") \nplotshape(buy == 1 and hl == false? TrendLine-atr(8) :na, text=\'?\', style= shape.labelup, location=location.absolute, color=color.blue, textcolor=color.white, offset=0, transp=0,size=size.auto)\nplotshape(sell == 1 and hl == false ?TrendLine+atr(8):na, text=\'?\', style=shape.labeldown, location=location.absolute, color=color.red, textcolor=color.white, offset=0, transp=0,size=size.auto)\n//\nalertcondition(sell == 1 ,title="Sell",message="Sell")\nalertcondition(buy == 1 ,title="Buy",message="Buy")\nalertcondition(buy == 1 or sell == 1 ,title="Buy/Sell",message="Buy/Sell")\nif (buy==1)\n    strategy.entry("Buy", strategy.long)\nif (sell==1)\n    strategy.entry("Sell", strategy.short)\n// === Stop LOSS ===\n\nif strategy.position_size>0\n    strategy.exit("Stop Loss/Profit Long","Buy", stop=strategy.position_avg_price*100, limit=strategy.position_avg_price*1.1)\nif strategy.position_size<0\n    strategy.exit("Stop Loss/Profit Short","Sell", stop=strategy.position_avg_price*100, limit=strategy.position_avg_price*0.9)'

class SM9F37A9D7FE5DECDE(PinePortBase, IStrategy):
    source_id = "SM_9f37a9d7fe5decde"
    source_file = '趋势追踪止损止盈策略Trend-Tracking-Stop-Loss-Take-Profit-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'BBperiod': 21, 'BBdeviations': 1.0, 'UseATRfilter': True, 'ATRperiod': 5, 'hl': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
