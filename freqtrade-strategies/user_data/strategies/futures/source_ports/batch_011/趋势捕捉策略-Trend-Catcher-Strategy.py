"""batch_011 port of 趋势捕捉策略-Trend-Catcher-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-04-20 00:00:00\nend: 2024-04-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © faytterro\n\n//@version=5\nstrategy("Trend Catcher Strategy", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\nlen = input.int(10)\ntp = input.float(2.5, step = 0.1)\nsl = input.float(2.5, step = 0.1)\nmalen = input.int(5)\nlimit = input.int(50)\nma = ta.sma(close,malen)\nsum = 0.0\nfor i = 0 to len-1\n    sum := sum + high[i]-low[i]\nfrs = 100*(ta.highest(high,len)-ta.lowest(low,len))/sum\n//hline(50)\n//plot(frs, color = color.white)\nl = ta.crossover(frs,limit) and ma>ma[1]\ns = ta.crossover(frs,limit) and ma<ma[1]\ncl = ma<ma[1]\ncs = ma>ma[1]\nqty_balance=input.int(50, maxval = 100)\nif (l)\n    strategy.entry("My Long Entry Id", strategy.long)\n    strategy.exit("exit long", "My Long Entry Id", qty_percent = qty_balance, limit = close*(100+tp)/100, stop = close*(100-sl)/100)\n\nif (s)\n    strategy.entry("My Short Entry Id", strategy.short)\n    strategy.exit("exit short", "My Short Entry Id", qty_percent = qty_balance, limit = close*(100-tp)/100, stop = close*(100+sl)/100)\n\nif (cl)\n    strategy.close("My Long Entry Id")\nif (cs)\n    strategy.close("My Short Entry Id")\n\nl:= l and strategy.opentrades<1\ns:= s and strategy.opentrades<1\ntransp = strategy.opentrades>0? 0 : 100\npma=plot(ma, color = ma<ma[1]? color.rgb(255, 82, 82, transp) : color.rgb(76, 175, 79, transp))\nprice = open/2+close/2\npprice = plot(price, display = display.none)\nfill(pma,pprice, color = ma<ma[1]? color.rgb(255, 82, 82, transp+90) : color.rgb(76, 175, 79, transp+90))\n\nspm=plot(ta.valuewhen(s,close,0), color = (strategy.opentrades>0 and ma<ma[1] and ma[1]<ma[2])? color.white : color.rgb(1,1,1,100), offset=1)\nlpm=plot(ta.valuewhen(l,close,0), color = (strategy.opentrades>0 and ma>ma[1] and ma[1]>ma[2])? color.white : color.rgb(1,1,1,100), offset=1)\n\nltp=plot(ta.valuewhen(l,close,0)*(100+ta.valuewhen(l,tp,0))/100,  color = (strategy.opentrades>0 and ma>ma[1] and ma[1]>ma[2])? color.green : color.rgb(1,1,1,100), offset=1)\nlsl=plot(ta.valuewhen(l,close,0)*(100-ta.valuewhen(l,sl,0))/100,  color = (strategy.opentrades>0 and ma>ma[1] and ma[1]>ma[2])? color.red : color.rgb(1,1,1,100), offset=1)\n\nstp=plot(ta.valuewhen(s,close,0)*(100-ta.valuewhen(s,tp,0))/100, color = (strategy.opentrades>0 and ma<ma[1] and ma[1]<ma[2])? color.green : color.rgb(1,1,1,100), offset=1)\nssl=plot(ta.valuewhen(s,close,0)*(100+ta.valuewhen(s,sl,0))/100, color = (strategy.opentrades>0 and ma<ma[1] and ma[1]<ma[2])? color.red : color.rgb(1,1,1,100), offset=1)\nfill(stp,spm, color = (strategy.opentrades>0 and ma<ma[1] and ma[1]<ma[2])? color.rgb(76, 175, 79, 90) : color.rgb(1,1,1,100))\nfill(ssl,spm, color = (strategy.opentrades>0 and ma<ma[1] and ma[1]<ma[2])? color.rgb(255, 82, 82, 90) : color.rgb(1,1,1,100))\nfill(ltp,lpm, color = (strategy.opentrades>0 and ma>ma[1] and ma[1]>ma[2])? color.rgb(76, 175, 79, 90) : color.rgb(1,1,1,100))\nfill(lsl,lpm, color = (strategy.opentrades>0 and ma>ma[1] and ma[1]>ma[2])? color.rgb(255, 82, 82, 90) : color.rgb(1,1,1,100))'

class SM46988DFF709A9439(PinePortBase, IStrategy):
    source_id = "SM_46988dff709a9439"
    source_file = '趋势捕捉策略-Trend-Catcher-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'len': 10, 'tp': 2.5, 'sl': 2.5, 'malen': 5, 'limit': 50, 'qty_balance': 50}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['loop', 'broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
