"""batch_012 port of 量化动量交易VWAP-MACD双指标趋势跟踪策略-Quantitative-Momentum-Trading-VWAP-MACD-Dual-Indicator-Trend-Following-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-08 00:00:00\nend: 2025-02-06 08:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("VWAP + MACD Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=200)\n\n// VWAP Calculation\nvwapValue = ta.vwap(close)\n\n// MACD Settings\nfastLength = input.int(12, title="MACD Fast Length")\nslowLength = input.int(26, title="MACD Slow Length")\nsignalSmoothing = input.int(9, title="MACD Signal Smoothing")\n\n// MACD Calculation\n[macdLine, signalLine, _] = ta.macd(close, fastLength, slowLength, signalSmoothing)\nmacdHistogram = macdLine - signalLine\n\n// Plot VWAP\nplot(vwapValue, color=color.orange, title="VWAP")\n\n// Plot MACD\nhline(0, "Zero Line", color=color.gray)\nplot(macdLine, color=color.blue, title="MACD Line")\nplot(signalLine, color=color.red, title="Signal Line")\nplot(macdHistogram, color=(macdHistogram >= 0 ? color.green : color.red), style=plot.style_histogram, title="MACD Histogram")\n\n// Long Condition: MACD crosses above Signal and price is above VWAP\nlongCondition = ta.crossover(macdLine, signalLine) and close > vwapValue\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n\n// Short Condition: MACD crosses below Signal and price is below VWAP\nshortCondition = ta.crossunder(macdLine, signalLine) and close < vwapValue\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Exit Long: MACD crosses below Signal or price crosses below VWAP\nexitLong = ta.crossunder(macdLine, signalLine) or close < vwapValue\nif (exitLong)\n    strategy.close("Long")\n\n// Exit Short: MACD crosses above Signal or price crosses above VWAP\nexitShort = ta.crossover(macdLine, signalLine) or close > vwapValue\nif (exitShort)\n    strategy.close("Short")\n\n'

class SMVWAPMACDQuantitativeMomentumTradingVWAPMACDDualIndicato0a8af5(PinePortBase, IStrategy):
    source_id = "SM_0a8af5bfe19c1f00"
    source_file = '量化动量交易VWAP-MACD双指标趋势跟踪策略-Quantitative-Momentum-Trading-VWAP-MACD-Dual-Indicator-Trend-Following-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalSmoothing': 9}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 200
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
