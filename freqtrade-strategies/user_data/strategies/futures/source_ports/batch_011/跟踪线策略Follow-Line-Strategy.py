"""batch_011 port of 跟踪线策略Follow-Line-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-23 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © Dreadblitz\n//@version=4\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nstrategy(title = " Strategy Follow Line Indicator ",\n         shorttitle = "S-FLI",\n         overlay = true,\n         precision = 8,\n         calc_on_order_fills = true,\n         calc_on_every_tick = true,\n         backtest_fill_limits_assumption = 0,\n         default_qty_type = strategy.fixed,\n         default_qty_value = 2,\n         initial_capital = 10000,\n         pyramiding=1,\n         currency = currency.USD,\n         linktoseries = true)\n\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nbackTestSectionFrom = input(title = "═══════════════ From ═══════════════", defval = true, type = input.bool)\n\nFromMonth         = input(defval = 1, title = "Month", minval = 1)\nFromDay           = input(defval = 1, title = "Day", minval = 1)\nFromYear          = input(defval = 2014, title = "Year", minval = 2000)\n\nbackTestSectionTo = input(title = "════════════════ To ════════════════", defval = true, type = input.bool)\nToMonth           = input(defval = 31, title = "Month", minval = 1)\nToDay             = input(defval = 12, title = "Day", minval = 1)\nToYear            = input(defval = 9999, title = "Year", minval = 2000)\n\nConfig            = input(title = "══════════════ Config ══════════════", defval = true, type = input.bool)\nBBperiod          = input(defval = 21,     title = "BB Period",    type = input.integer, minval = 1)\nBBdeviations      = input(defval = 1.00,     title = "BB Deviations",    type = input.float, minval = 0.1, step=0.05)\nUseATRfilter      = input(defval = true, title = "ATR Filter",  type = input.bool)\nATRperiod         = input(defval = 5,     title = "ATR Period",    type = input.integer, minval = 1)\nhl                = input(defval = false, title = "Hide Labels",  type = input.bool)\n\n\nbackTestPeriod() => true\n\n//\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nBBUpper=sma (close,BBperiod)+stdev(close, BBperiod)*BBdeviations\nBBLower=sma (close,BBperiod)-stdev(close, BBperiod)*BBdeviations\n//\nTrendLine = 0.0\niTrend = 0.0\nbuy = 0.0\nsell = 0.0\n//\nBBSignal = close>BBUpper? 1 : close<BBLower? -1 : 0\n// \nif BBSignal == 1 and UseATRfilter == 1\n    TrendLine:=low-atr(ATRperiod)\n    if TrendLine<TrendLine[1] \n        TrendLine:=TrendLine[1]\nif BBSignal == -1 and UseATRfilter == 1\n    TrendLine:=high+atr(ATRperiod)\n    if TrendLine>TrendLine[1]\n        TrendLine:=TrendLine[1]\nif BBSignal == 0 and UseATRfilter == 1\n    TrendLine:=TrendLine[1]\n//\nif BBSignal == 1 and UseATRfilter == 0\n    TrendLine:=low\n    if TrendLine<TrendLine[1] \n        TrendLine:=TrendLine[1]\nif BBSignal == -1 and UseATRfilter == 0\n    TrendLine:=high\n    if TrendLine>TrendLine[1]\n        TrendLine:=TrendLine[1]\nif BBSignal == 0 and UseATRfilter == 0\n    TrendLine:=TrendLine[1]\n//\niTrend:=iTrend[1]\nif TrendLine>TrendLine[1] \n    iTrend:=1\nif TrendLine<TrendLine[1] \n    iTrend:=-1\n//\nbuy:=iTrend[1]==-1 and iTrend==1 ? 1 : na\nsell:=iTrend[1]==1 and iTrend==-1? 1 : na\n//\nplot(TrendLine, color=iTrend > 0?color.blue:color.red ,style=plot.style_line,linewidth=2,transp=0,title="Trend Line") \nplotshape(buy == 1 and hl == false? TrendLine-atr(8) :na, text=\'?\', style= shape.labelup, location=location.absolute, color=color.blue, textcolor=color.white, offset=0, transp=0,size=size.auto)\nplotshape(sell == 1 and hl == false ?TrendLine+atr(8):na, text=\'?\', style=shape.labeldown, location=location.absolute, color=color.red, textcolor=color.white, offset=0, transp=0,size=size.auto)\n\n// Strategy Entry\nif (backTestPeriod())\n    strategy.entry("long", true, 1, when = buy == 1)\n    strategy.entry("short", false, 1, when = sell == 1) '

class SM49956BE2ACB3C1AD(PinePortBase, IStrategy):
    source_id = "SM_49956be2acb3c1ad"
    source_file = '跟踪线策略Follow-Line-Strategy.md'
    timeframe = '10m'
    can_short = False
    source_defaults = {'backTestSectionFrom': True, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2014, 'backTestSectionTo': True, 'ToMonth': 31, 'ToDay': 12, 'ToYear': 9999, 'Config': True, 'BBperiod': 21, 'BBdeviations': 1.0, 'UseATRfilter': True, 'ATRperiod': 5, 'hl': False}
    source_qty_type = 'fixed'
    source_qty_value = 2
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 10000
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
