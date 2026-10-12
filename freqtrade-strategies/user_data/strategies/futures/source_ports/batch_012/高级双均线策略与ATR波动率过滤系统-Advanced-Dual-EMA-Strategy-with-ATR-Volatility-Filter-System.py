"""batch_012 port of 高级双均线策略与ATR波动率过滤系统-Advanced-Dual-EMA-Strategy-with-ATR-Volatility-Filter-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-27 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover with ATR Filter", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// Inputs for Moving Averages\nfastLength = input.int(50, title="Fast EMA Length")\nslowLength = input.int(200, title="Slow EMA Length")\n\n// Inputs for ATR Filter\natrLength = input.int(14, title="ATR Length")\natrMultiplier = input.float(1.5, title="ATR Multiplier")\natrThreshold = input.float(0.02, title="ATR Threshold (%)")\n\n// Calculate EMAs\nfastEMA = ta.ema(close, fastLength)\nslowEMA = ta.ema(close, slowLength)\n\n// Calculate ATR\natr = ta.atr(atrLength)\n\n// Convert ATR to a percentage of price\natrPct = atr / close\n\n// Define Long Condition (Cross and ATR filter)\nlongCondition = ta.crossover(fastEMA, slowEMA) and atrPct > atrThreshold / 100\n\n// Define Short Condition\nshortCondition = ta.crossunder(fastEMA, slowEMA) and atrPct > atrThreshold / 100\n\n// Define Exit Conditions\nexitConditionLong = ta.crossunder(fastEMA, slowEMA)\nexitConditionShort = ta.crossover(fastEMA, slowEMA)\n\n// Long Entry\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short Entry\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Long Exit\nif (exitConditionLong)\n    strategy.close("Long")\n\n// Short Exit\nif (exitConditionShort)\n    strategy.close("Short")\n\n// Plot EMAs for visual reference\nplot(fastEMA, title="50 EMA", color=color.blue)\nplot(slowEMA, title="200 EMA", color=color.red)\n\n// Plot ATR for reference\nplot(atrPct, title="ATR Percentage", color=color.orange, style=plot.style_line)\nhline(atrThreshold / 100, "ATR Threshold", color=color.green)\n'

class SMATRAdvancedDualEMAStrategywithATRVolatilityFilterSystema82fec(PinePortBase, IStrategy):
    source_id = "SM_a82fec4bf9215a46"
    source_file = '高级双均线策略与ATR波动率过滤系统-Advanced-Dual-EMA-Strategy-with-ATR-Volatility-Filter-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 50, 'slowLength': 200, 'atrLength': 14, 'atrMultiplier': 1.5, 'atrThreshold': 0.02}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
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
