"""batch_011 port of 趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-02-26 00:00:00\nend: 2025-03-05 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("TMA Strategy", shorttitle="TMA Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1)\n\n// Smoothed MAs Inputs\nlen1 = input.int(21, title="Length 1", group="Smoothed MA Inputs")\nsrc1 = input.source(close, title="Source 1", group="Smoothed MA Inputs")\nlen2 = input.int(50, title="Length 2", group="Smoothed MA Inputs")\nsrc2 = input.source(close, title="Source 2", group="Smoothed MA Inputs")\nh100 = input.bool(true, title="Show 100 Line", group="Smoothed MA Inputs")\nlen3 = input.int(100, title="Length 3", group="Smoothed MA Inputs")\nsrc3 = input.source(close, title="Source 3", group="Smoothed MA Inputs")\nlen4 = input.int(200, title="Length 4", group="Smoothed MA Inputs")\nsrc4 = input.source(close, title="Source 4", group="Smoothed MA Inputs")\n\n// Calculate Smoothed MAs\nsmma1 = ta.sma(src1, len1)\nplot(smma1, color=color.white, linewidth=2, title="21 SMMA")\n\nsmma2 = ta.sma(src2, len2)\nplot(smma2, color=color.green, linewidth=2, title="50 SMMA")\n\nsmma3 = ta.sma(src3, len3)\nplot(h100 ? smma3 : na, color=color.yellow, linewidth=2, title="100 SMMA")\n\nsmma4 = ta.sma(src4, len4)\nplot(smma4, color=color.red, linewidth=2, title="200 SMMA")\n\n// Trend Filter\nema2 = ta.ema(close, 2)\n\n// 3 Line Strike Signals\nbullSig = close[3] < open[3] and close[2] < open[2] and close[1] < open[1] and close > open[1]\nbearSig = close[3] > open[3] and close[2] > open[2] and close[1] > open[1] and close < open[1]\n\n// Engulfing Candles Signals\nbullishEngulfing = open <= close[1] and open < open[1] and close > open[1]\nbearishEngulfing = open >= close[1] and open > open[1] and close < open[1]\n\n// Trading Session Filter\nts = input.bool(true, title="Enable Session Filter", group="Trade Session")\ntz = input.string("America/Chicago", title="Timezone", options=["America/New_York", "America/Chicago", "Europe/London", "Europe/Frankfurt", "Asia/Tokyo", "Asia/Sydney", "UTC"], group="Trade Session")\nstartH = input.int(8, title="Session Start Hour", minval=0, maxval=23, group="Trade Session")\nstartM = input.int(30, title="Session Start Minute", minval=0, maxval=59, group="Trade Session")\nendH = input.int(12, title="Session End Hour", minval=0, maxval=23, group="Trade Session")\nendM = input.int(0, title="Session End Minute", minval=0, maxval=59, group="Trade Session")\n\nstartTime = timestamp(year, month, dayofmonth, startH, startM)\nendTime = timestamp(year, month, dayofmonth, endH, endM)\ninSession = (time >= startTime and time <= endTime)\n\n// Entry Conditions\nlongCondition = (bullishEngulfing or bullSig) and (ema2 > smma4) and (not ts or inSession)\nshortCondition = (bearishEngulfing or bearSig) and (ema2 < smma4) and (not ts or inSession)\n\n// Exit Conditions\nexitLong = ta.crossunder(ema2, smma4)\nexitShort = ta.crossover(ema2, smma4)\n\n// Strategy Execution\nif (longCondition)\n    strategy.entry("Long", strategy.long, comment="Long Entry")\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short, comment="Short Entry")\n\nif (exitLong)\n    strategy.close("Long", comment="Exit Long")\n\nif (exitShort)\n    strategy.close("Short", comment="Exit Short")\n\n// Debugging Plots\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, title="Long Signal")\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, title="Short Signal")\n\n// Visuals\nplot(ema2, color=color.blue, linewidth=1, title="EMA(2)")\nbgcolor(inSession and ts ? color.new(color.blue, 90) : na, title="Session Background")\n'

class SM498FA601C3838634(PinePortBase, IStrategy):
    source_id = "SM_498fa601c3838634"
    source_file = '趋势跟踪多周期平滑移动平均线结合K线形态确认策略-Multi-Timeframe-Smoothed-Moving-Average-Strategy-with-Candlestick-Pattern-Confirmation-for-Trend-Following.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'len1': 21, 'len2': 50, 'h100': True, 'len3': 100, 'len4': 200, 'ts': True, 'tz': 'America/Chicago', 'startH': 8, 'startM': 30, 'endH': 12, 'endM': 0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 10000
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
