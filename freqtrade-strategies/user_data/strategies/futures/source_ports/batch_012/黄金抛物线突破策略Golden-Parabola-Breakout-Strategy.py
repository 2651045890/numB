"""batch_012 port of 黄金抛物线突破策略Golden-Parabola-Breakout-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-04 00:00:00\nend: 2024-02-03 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("5MABAND + GBS Buy & Sell Strategy", overlay=true)\n\n// Command 1 - 5MABAND Calculation\nlength = input(5, title="Number of Candles for Average")\navgHigh = ta.sma(high, length)\navgLow = ta.sma(low, length)\n\n// Plotting 5MABAND Bands\nplot(avgHigh, color=color.green, title="5MABAND High Line", linewidth=1)\nplot(avgLow, color=color.red, title="5MABAND Low Line", linewidth=1)\n\n// Command 2 - GBS concept Buy Entry\ngbsBuyCondition = close > open and high - close < close - open and open - low < close - open and close - open > close[1] - open[1] and close - open > close[2] - open[2] and close - open > close[3] - open[3] and close[1] < avgHigh and close[2] < avgHigh and close[3] < avgHigh and open[1] < avgHigh and open[2] < avgHigh and open[3] < avgHigh\n\n// Command 3 - GBS Concept Sell Entry\ngbsSellCondition = open - close > open[1] - close[1] and open - close > open[2] - close[2] and open - close > open[3] - close[3] and open[1] > avgLow and open[2] > avgLow and open[3] > avgLow and open - close > open - low and open - close > high - open\n\n// Command 6 - 5MABAND Exit Trigger\nexitTriggerCandle_5MABAND_Buy = low < avgLow\nexitTriggerCandle_5MABAND_Sell = high > avgHigh\n\n// Exit Signals for 5MABAND\nexitBuySignal_5MABAND = close < avgLow\nexitSellSignal_5MABAND = close > avgHigh\n\n// Execute Buy and Sell Orders\nstrategy.entry("Buy", strategy.long, when = gbsBuyCondition)\nstrategy.close("Buy", when = exitBuySignal_5MABAND)\n\nstrategy.entry("Sell", strategy.short, when = gbsSellCondition)\nstrategy.close("Sell", when = exitSellSignal_5MABAND)\n\n// Exit Buy and Sell Orders for 5MABAND\nstrategy.close("Buy", when = exitTriggerCandle_5MABAND_Buy)\nstrategy.close("Sell", when = exitTriggerCandle_5MABAND_Sell)\n\n'

class SMGoldenParabolaBreakoutStrategy339cd1(PinePortBase, IStrategy):
    source_id = "SM_339cd10efa3c3226"
    source_file = '黄金抛物线突破策略Golden-Parabola-Breakout-Strategy.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'length': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
