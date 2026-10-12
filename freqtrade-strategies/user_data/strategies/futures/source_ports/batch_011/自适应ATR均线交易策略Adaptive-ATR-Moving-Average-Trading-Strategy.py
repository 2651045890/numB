"""batch_011 port of 自适应ATR均线交易策略Adaptive-ATR-Moving-Average-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-26 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("ATR(Hull)", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, calc_on_order_fills= false, calc_on_every_tick=true, pyramiding=0)\nlength = input(title="Length", defval=14, minval=1)\nprice = input(close)\nSL = input(50, title="Stop loss")\nTP = input(150, title="Take profit")\nFromMonth = input(defval = 9, title = "From Month", minval = 1, maxval = 12) \nFromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31) \nFromYear = input(defval = 2018, title = "From Year", minval = 2017) \nToMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12) \nToDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31) \nToYear = input(defval = 9999, title = "To Year", minval = 2017) \nstart = timestamp(FromYear, FromMonth, FromDay, 00, 00) \nfinish = timestamp(ToYear, ToMonth, ToDay, 23, 59) \nwindow() => true\np=price[1]\nfunc_hma(style, length)=>\n    return = wma((2*wma(p,length/2))-wma(p,length),round(sqrt(length)))\nATR=func_hma(tr(true), length)    \nplot(ATR[0], title="ATR1",color=green,transp=0)\nplot(ATR[1], title="ATR2",color=red,transp=0)\nif (ATR>ATR[1])\n    strategy.entry("long",strategy.long,comment="Long",when=window())\nif (ATR<ATR[1])\n    strategy.entry("short",strategy.short,comment="Short",when=window())\n//strategy.close_all(when=strategy.openprofit<-eqSL and window())\n//strategy.close_all(when=strategy.openprofit>eqTP and window())\nstrategy.exit("exit", "long", profit = TP, loss = SL)\nstrategy.exit("exit", "short", profit = TP, loss = SL)'

class SMA2ABAA8B82845E86(PinePortBase, IStrategy):
    source_id = "SM_a2abaa8b82845e86"
    source_file = '自适应ATR均线交易策略Adaptive-ATR-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'SL': 50, 'TP': 150, 'FromMonth': 9, 'FromDay': 1, 'FromYear': 2018, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
