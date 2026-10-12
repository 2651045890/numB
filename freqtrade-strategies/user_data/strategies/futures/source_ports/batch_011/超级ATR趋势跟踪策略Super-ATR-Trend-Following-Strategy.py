"""batch_011 port of 超级ATR趋势跟踪策略Super-ATR-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-12 00:00:00\nend: 2024-02-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'B厂长 @超级趋势精简优化版\', overlay=true)\nPeriods = input(title=\'ATR周期\', defval=10)\nsrc = input(hl2, title=\'价格数据源\')\nMultiplier = input.float(title=\'ATR 乘数\', step=0.1, defval=3.0)\nchangeATR = input(title=\'更改ATR计算方法\', defval=true,tooltip = \'默认为art否则sma(ta.tr,ATR周期)\')\nshowsignals = input(title=\'显示买入/卖出信号\', defval=false)\natr2 = ta.sma(ta.tr, Periods)\natr = changeATR ? ta.atr(Periods) : atr2\nup = src - Multiplier * atr\nup1 = nz(up[1], up)\nup := close[1] > up1 ? math.max(up, up1) : up\ndn = src + Multiplier * atr\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? math.min(dn, dn1) : dn\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\nupPlot = plot(trend == 1 ? up : na, title=\'上涨趋势\', style=plot.style_linebr, linewidth=2, color=color.new(color.green, 0))\nbuySignal = trend == 1 and trend[1] == -1\nplotshape(buySignal and showsignals ? up : na, title=\'买点\', text=\'买点\', location=location.absolute, style=shape.labelup, size=size.tiny, color=color.new(color.green, 0), textcolor=color.new(color.white, 0))\ndnPlot = plot(trend == 1 ? na : dn, title=\'下跌趋势\', style=plot.style_linebr, linewidth=2, color=color.new(color.red, 0))\nsellSignal = trend == -1 and trend[1] == 1\nplotshape(sellSignal and showsignals ? dn : na, title=\'卖点\', text=\'卖点\', location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.new(color.red, 0), textcolor=color.new(color.white, 0))\nFromMonth = input.int(defval=9, title=\'From Month\', minval=1, maxval=12)\nFromDay = input.int(defval=1, title=\'From Day\', minval=1, maxval=31)\nFromYear = input.int(defval=2018, title=\'From Year\', minval=999)\nToMonth = input.int(defval=1, title=\'To Month\', minval=1, maxval=12)\nToDay = input.int(defval=1, title=\'To Day\', minval=1, maxval=31)\nToYear = input.int(defval=9999, title=\'To Year\', minval=999)\nstart = timestamp(FromYear, FromMonth, FromDay, 00, 00)\nfinish = timestamp(ToYear, ToMonth, ToDay, 23, 59)\nwindow() =>\n    time >= start and time <= finish ? true : false\nlongCondition = buySignal\nif longCondition and window()\n    strategy.entry(\'BUY\', strategy.long, comment = \'做多\')\nshortCondition = sellSignal\nif shortCondition and window()\n    strategy.entry(\'SAL\', strategy.short, comment = \'做空\')\n\nbuy1 = ta.barssince(buySignal)\nsell1 = ta.barssince(sellSignal)\ncolor1 = buy1[1] < sell1[1] ? color.green : buy1[1] > sell1[1] ? color.red : na\n\n'

class SM3351C434A520B922(PinePortBase, IStrategy):
    source_id = "SM_3351c434a520b922"
    source_file = '超级ATR趋势跟踪策略Super-ATR-Trend-Following-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Periods': 10, 'Multiplier': 3.0, 'changeATR': True, 'showsignals': False, 'FromMonth': 9, 'FromDay': 1, 'FromYear': 2018, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
