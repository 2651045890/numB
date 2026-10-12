"""batch_011 port of 移动平均交叉策略-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Moving Average Crossover Strategy", overlay=true)\n\n// User-defined moving average periods\nma1Periods = input(5, title="First Moving Average Periods")\nma2Periods = input(20, title="Second Moving Average Periods")\n\n// Calculate moving averages\nma1 = sma(close, ma1Periods)\nma2 = sma(close, ma2Periods)\n\n// Plot moving averages\nplot(ma1, color=color.red, linewidth=2, title="First Moving Average")\nplot(ma2, color=color.blue, linewidth=2, title="Second Moving Average")\n\n// Detect crossovers and crossunders\nbullishCross = crossover(ma1, ma2)\nbearishCross = crossunder(ma1, ma2)\n\n// Define trading hours (8 AM to 2 PM UTC)\nstartHour = 8\nendHour = 20\nutcHour = hour(time, "UTC")\nisMarketOpen = true\n\n// Define profit target\nprofitTarget = 150\n\n// Check if the price has closed above/below the MA for the past 4 bars\naboveMa = close[4] > ma1[4] and close[3] > ma1[3] and close[2] > ma1[2] and close[1] > ma1[1]\nbelowMa = close[4] < ma1[4] and close[3] < ma1[3] and close[2] < ma1[2] and close[1] < ma1[1]\n\n// Create buy and sell signals\nif (bullishCross and isMarketOpen and aboveMa)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Sell", "Buy", profit=profitTarget)\nif (bearishCross and isMarketOpen and belowMa)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Cover", "Sell", profit=profitTarget)\n\n// Plot shapes on crossovers\nplotshape(series=bullishCross and isMarketOpen and aboveMa, location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\nplotshape(series=bearishCross and isMarketOpen and belowMa, location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")\n'

class SM1FD641EA375A11CB(PinePortBase, IStrategy):
    source_id = "SM_1fd641ea375a11cb"
    source_file = '移动平均交叉策略-Moving-Average-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'ma1Periods': 5, 'ma2Periods': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
