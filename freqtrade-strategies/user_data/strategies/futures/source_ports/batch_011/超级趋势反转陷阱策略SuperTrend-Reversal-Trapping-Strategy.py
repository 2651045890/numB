"""batch_011 port of 超级趋势反转陷阱策略SuperTrend-Reversal-Trapping-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-17 00:00:00\nend: 2023-09-24 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SuperTrend Trapping Candle Strategy", shorttitle="ST", margin_long=1, margin_short=1, overlay=true)\n\n\n// Inputs\natrPeriod = input.int(10, "ATR Length")\nfactor = input.int(2, "Factor")\ncandleDivider = input.float(0.003, "Candle Height", step=0.0001)\n\n\n// Supertrend\n[supertrend, direction] = ta.supertrend(factor, atrPeriod)\nplot(direction < 0 ? supertrend : na, "Up Trend", color = color.green, style=plot.style_linebr)\nplot(direction < 0? na : supertrend, "Down Trend", color = color.red, style=plot.style_linebr)\n\n\n//Trapping canlde\nisUptrend = direction < 0\nisDowntrend = direction > 0\nisBullsStrengthDecreasing = volume < volume[1] and volume[1] < volume[2] and close > close[1] and close[1] > close[2] and open > open[1] and open[1] > open[2]\nisBearsStrengthDecreasing = volume < volume[1] and volume[1] < volume[2] and close < close[1] and close[1] < close[2] and open < open[1] and open[1] < open[2]\nisStrongVolume = (volume > volume[1]) or isBullsStrengthDecreasing or isBearsStrengthDecreasing\nisSmallCandle = (high - low) < close * candleDivider\nisUptrendTrapping = isUptrend and close < open and isStrongVolume and isSmallCandle\nisDowntrendTrapping = isDowntrend and close > open and isStrongVolume and isSmallCandle\n\nplotshape(isUptrendTrapping, style=shape.triangleup, location=location.belowbar, color=color.green)\nplotshape(isDowntrendTrapping, style=shape.triangledown, location=location.abovebar, color=color.orange)\n\n\n// Signals\nlongCondition = isUptrendTrapping\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n\nshortCondition = isDowntrendTrapping\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\nif open < close\n    alert("Seller Trapped.", alert.freq_all)\nif close > open\n    alert("Buyer Trapped.", alert.freq_all)\n\n'

class SMC497DA64BE933FF1(PinePortBase, IStrategy):
    source_id = "SM_c497da64be933ff1"
    source_file = '超级趋势反转陷阱策略SuperTrend-Reversal-Trapping-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'atrPeriod': 10, 'factor': 2, 'candleDivider': 0.003}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
