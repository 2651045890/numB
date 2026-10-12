"""batch_011 port of 窄幅震荡内收突破策略Narrow-Range-Inside-Day-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-11 00:00:00\nend: 2023-09-14 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("NR7ID: Narrow Range + Inside Day, Long Only Strategy (by ChartArt)", shorttitle="CA_-_NR7ID_Strat", overlay=true) // max_bars_back=5000\n\n// ChartArt\'s Narrow Range + Inside Day Strategy (Long Only)\n//\n// Version 1.0\n// Idea by ChartArt on Oktober 16, 2016.\n//\n// This long only strategy determines when there is both\n// a NR7 (narrow range 7, a trading day in which the range\n// is narrower than any of the previous six days), plus a\n// inside day (high of the current day is lower than the high\n// of the previous day and the low of the current day is higher\n// than the low of the previous day) both on the same trading day\n// and enters a long trade when the close is larger than the\n// open and the slope of the simple moving average is upwards, too.\n//\n// The strategy exits the long trade next time the close is\n// larger than the open in any of the next trading days.\n//\n// In addition the NR7ID can be colored (if close large open\n// colored in green, else in red) and the SMA can be drawn\n// with a color based on the direction of the SMA slope.\n//\n// List of my work: \n// https://www.tradingview.com/u/ChartArt/\n// \n//  __             __  ___       __  ___ \n// /  ` |__|  /\\  |__)  |   /\\  |__)  |  \n// \\__, |  | /~~\\ |  \\  |  /~~\\ |  \\  |  \n// \n// \n\n\n// NR7 Identifier\nshow_NR7=input(true, type=bool,title="Show Narrow Range 7 (NR7) ?")\nrange=(high-low)\nnr7=(range < range[1]) and (range < range[2]) and (range < range[3]) and (range < range[4]) and (range < range[5]) and (range < range[6])\nplotchar(show_NR7?nr7:na, char="7", location=location.abovebar, color=blue)\n\n// Inside Day Identifier\nshow_insidebar = input(true, type=bool,title="Show Inside Day (I) ?")\ninsidebar =  (high < high[1] and low > low[1])\nplotchar(show_insidebar?insidebar:na, char="i", location=location.abovebar, color=blue)\n\n// NR7 + Inside Day Identifier\nshow_NR7ID = input(true, type=bool,title="Show NR7ID (NR7 + Inside Day) colors ?")\nNR7ID = nr7 and insidebar\nNR7ID_color = NR7ID and open < close ? green : NR7ID and open > close ? red : gray\nbarcolor(show_NR7ID?NR7ID_color:na)\n\n// Simple Moving Average\nshow_ma = input(true, type=bool,title="Show SMA ?")\nma_length = input(14,title="SMA Length")\nma = sma(close,ma_length)\nma_change = change(ma) > 0\nma_change_color = change(ma) > 0 ? green : change(ma) < 0 ? red : blue\nplot(show_ma?ma:na,color=ma_change_color,linewidth=3)\n\n// (not enabled) Short Strategy: NR7 + Inside Day + close is smaller than open + change of SMA is downwards\n//strategy.entry("sell", strategy.short, when = NR7ID and open > close and ma_change == false, comment="Short")\n//strategy.close("sell", when = open > close )\n\n// Long Strategy: NR7 + Inside Day + close is larger than open + change of SMA is upwards\nstrategy.entry("long", strategy.long, when = NR7ID and open < close and ma_change == true, comment="Long")\nstrategy.close("long", when = open < close )'

class SM388917812021C5B1(PinePortBase, IStrategy):
    source_id = "SM_388917812021c5b1"
    source_file = '窄幅震荡内收突破策略Narrow-Range-Inside-Day-Breakout-Strategy.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'show_NR7': True, 'show_insidebar': True, 'show_NR7ID': True, 'show_ma': True, 'ma_length': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
