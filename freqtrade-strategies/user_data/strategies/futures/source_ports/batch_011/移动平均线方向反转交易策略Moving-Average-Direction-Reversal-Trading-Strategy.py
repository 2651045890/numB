"""batch_011 port of 移动平均线方向反转交易策略Moving-Average-Direction-Reversal-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-21 00:00:00\nend: 2023-09-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Moving Average Consecutive Up/Down Strategy (by ChartArt)", overlay=true)\n\n// ChartArt\'s Moving Average Consecutive Up/Down Strategy\n//\n// Version 1.0\n// Idea by ChartArt on December 30, 2015.\n//\n// This strategy goes long (or short) if there are several\n// consecutive increasing (or decreasing) moving average\n// values in a row in the same direction.\n//\n// The bars can be colored using the raw moving average trend.\n// And the background can be colored using the consecutive\n// moving average trend setting. In addition a experimental\n// line of the moving average change can be drawn.\n//\n// The strategy is based upon the "Consecutive Up/Down Strategy"\n// created by Tradingview.\n\n\n// Input\nSwitch1 = input(true, title="Enable Bar Color?")\nSwitch2 = input(true, title="Enable Background Color?")\nSwitch3 = input(false, title="Enable Moving Average Trend Line?")\n\nConsecutiveBars = input(4,title="Consecutive Trend in Bars",minval=1)\n\n// MA Calculation\nMAlen = input(1,title="Moving Average Length: (1 = off)",minval=1)\nSelectMA = input(2, minval=1, maxval=4, title=\'Moving Average: (1 = SMA), (2 = EMA), (3 = WMA), (4 = Linear)\')\nPrice = input(close, title="Price Source")\nCurrent =\n SelectMA == 1 ? sma(Price, MAlen) :\n SelectMA == 2 ? ema(Price, MAlen) :\n SelectMA == 3 ? wma(Price, MAlen) :\n SelectMA == 4 ? linreg(Price, MAlen,0) :\n na\nLast =\n SelectMA == 1 ? sma(Price[1], MAlen) :\n SelectMA == 2 ? ema(Price[1], MAlen) :\n SelectMA == 3 ? wma(Price[1], MAlen) :\n SelectMA == 4 ? linreg(Price[1], MAlen,0) :\n na\n\n// Calculation\nMovingAverageTrend = if Current > Last\n    1\nelse\n    0\n\nConsecutiveBarsUp = MovingAverageTrend > 0.5 ? nz(ConsecutiveBarsUp[1]) + 1 : 0\nConsecutiveBarsDown = MovingAverageTrend < 0.5 ? nz(ConsecutiveBarsDown[1]) + 1 : 0\nBarColor = MovingAverageTrend > 0.5 ? green : MovingAverageTrend < 0.5 ? red : blue\nBackgroundColor = ConsecutiveBarsUp >= ConsecutiveBars ? green : ConsecutiveBarsDown >= ConsecutiveBars ? red : gray\nMovingAverageLine = change(MovingAverageTrend) != 0 ? close : na\n\n// Strategy\nif (ConsecutiveBarsUp >= ConsecutiveBars)\n    strategy.entry("ConsUpLE", strategy.long, comment="Bullish")\n    \nif (ConsecutiveBarsDown >= ConsecutiveBars)\n    strategy.entry("ConsDnSE", strategy.short, comment="Bearish")\n\n// output\nbarcolor(Switch1?BarColor:na)\nbgcolor(Switch2?BackgroundColor:na)\nplot(Switch3?MovingAverageLine:na, color=change(MovingAverageTrend)<0?green:red, linewidth=4)\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

class SMDBBE2CE40AB33CFE(PinePortBase, IStrategy):
    source_id = "SM_dbbe2ce40ab33cfe"
    source_file = '移动平均线方向反转交易策略Moving-Average-Direction-Reversal-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Switch1': True, 'Switch2': True, 'Switch3': False, 'ConsecutiveBars': 4, 'MAlen': 1, 'SelectMA': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
