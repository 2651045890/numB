"""batch_011 port of 移动平均线双轨道交易策略Dual-Moving-Average-Channel-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-29 00:00:00\nend: 2024-02-28 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © gpadihar\n\n//@version=4\nstrategy("SL1 Pips after TP1 (MA)", commission_type=strategy.commission.cash_per_order, overlay=true)\n\n// Strategy\nBuy  = input(true)\nSell = input(true)\n\n// Date Range\nstart_year    = input(title=\'Start year\'   ,defval=2020)\nstart_month   = input(title=\'Start month\'  ,defval=1)\nstart_day     = input(title=\'Start day\'    ,defval=1)\nstart_hour    = input(title=\'Start hour\'   ,defval=0)\nstart_minute  = input(title=\'Start minute\' ,defval=0)\nend_time      = input(title=\'set end time?\',defval=false)\nend_year      = input(title=\'end year\'     ,defval=3019)\nend_month     = input(title=\'end month\'    ,defval=12)\nend_day       = input(title=\'end day\'      ,defval=31)\nend_hour      = input(title=\'end hour\'     ,defval=23)\nend_minute    = input(title=\'end minute\'   ,defval=59)\n\n// MA\nema_period = input(title=\'EMA period\',defval=10)\nwma_period = input(title=\'WMA period\',defval=20)\nema        = ema(close,ema_period)\nwma        = wma(close,wma_period)\n\n// Entry Condition\nbuy =\n crossover(ema,wma) and\n nz(strategy.position_size) == 0 and Buy and\n time > timestamp(start_year, start_month, start_day, start_hour, start_minute) and\n (end_time?(time < timestamp(end_year, end_month, end_day, end_hour, end_minute)):true)\n \nsell =\n crossunder(ema,wma) and\n nz(strategy.position_size) == 0 and Sell and\n time > timestamp(start_year, start_month, start_day, start_hour, start_minute) and\n (end_time?(time < timestamp(end_year, end_month, end_day, end_hour, end_minute)):true)\n\n// Pips\npip = input(20)*10*syminfo.mintick\n\n// Trading parameters //\nvar bool  LS  = na\nvar bool  SS  = na\nvar float EP  = na\nvar float TVL = na\nvar float TVS = na\nvar float TSL = na\nvar float TSS = na\nvar float TP1 = na\nvar float TP2 = na\nvar float SL1 = na\nvar float SL2 = na\n\nif buy or sell and strategy.position_size == 0\n    EP  := close\n    SL1 := EP - pip     * (sell?-1:1)\n    SL2 := EP - pip     * (sell?-1:1)\n    TP1 := EP + pip     * (sell?-1:1)\n    TP2 := EP + pip * 2 * (sell?-1:1) \n   \n// current trade direction    \nLS := buy  or strategy.position_size > 0\nSS := sell or strategy.position_size < 0\n\n// adjust trade parameters and trailing stop calculations\nTVL := max(TP1,open) - pip[1]\nTVS := min(TP1,open) + pip[1]\nTSL := open[1] > TSL[1] ? max(TVL,TSL[1]):TVL \nTSS := open[1] < TSS[1] ? min(TVS,TSS[1]):TVS\n\nif LS and high > TP1\n    if open <= TP1\n        SL2:=min(EP,TSL)\n    \nif SS and low < TP1\n    if open >= TP1\n        SL2:=max(EP,TSS)\n\n// Closing conditions\nclose_long  = LS and open < SL2\nclose_short = SS and open > SL2\n\n// Buy\nstrategy.entry("buy"  , strategy.long, when=buy and not SS)\nstrategy.exit ("exit1", from_entry="buy", stop=SL1, limit=TP1, qty_percent=50)\nstrategy.exit ("exit2", from_entry="buy", stop=SL2, limit=TP2)\n\n// Sell\nstrategy.entry("sell" , strategy.short, when=sell and not LS)\nstrategy.exit ("exit3", from_entry="sell", stop=SL1, limit=TP1, qty_percent=50)\nstrategy.exit ("exit4", from_entry="sell", stop=SL2, limit=TP2)\n\n// Plots\na=plot(strategy.position_size >  0 ? SL1 : na, color=#dc143c, style=plot.style_linebr)\nb=plot(strategy.position_size <  0 ? SL1 : na, color=#dc143c, style=plot.style_linebr) \nc=plot(strategy.position_size >  0 ? TP1 : na, color=#00ced1, style=plot.style_linebr) \nd=plot(strategy.position_size <  0 ? TP1 : na, color=#00ced1, style=plot.style_linebr) \ne=plot(strategy.position_size >  0 ? TP2 : na, color=#00ced1, style=plot.style_linebr) \nf=plot(strategy.position_size <  0 ? TP2 : na, color=#00ced1, style=plot.style_linebr) \ng=plot(strategy.position_size >= 0 ? na  : EP, color=#ffffff, style=plot.style_linebr) \nh=plot(strategy.position_size <= 0 ? na  : EP, color=#ffffff, style=plot.style_linebr) \n\nplot(ema,title="ema",color=#fff176)\nplot(wma,title="wma",color=#00ced1)\n\n'

class SM9745D502AF8DA2D7(PinePortBase, IStrategy):
    source_id = "SM_9745d502af8da2d7"
    source_file = '移动平均线双轨道交易策略Dual-Moving-Average-Channel-Trading-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'Buy': True, 'Sell': True, 'start_year': 2020, 'start_month': 1, 'start_day': 1, 'start_hour': 0, 'start_minute': 0, 'end_time': False, 'end_year': 3019, 'end_month': 12, 'end_day': 31, 'end_hour': 23, 'end_minute': 59, 'ema_period': 10, 'wma_period': 20, 'pip': 20}
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
