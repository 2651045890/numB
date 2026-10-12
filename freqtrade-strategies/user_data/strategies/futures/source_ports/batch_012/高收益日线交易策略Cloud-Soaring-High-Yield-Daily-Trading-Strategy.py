"""batch_012 port of 高收益日线交易策略Cloud-Soaring-High-Yield-Daily-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-23 00:00:00\nend: 2023-11-22 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("High Yield Ichimoku Cloud Strategy", shorttitle="HY Ichimoku", overlay=true)\n\n// Ichimoku Cloud settings\ntenkanPeriods = input(9, title="Tenkan Sen Periods")\nkijunPeriods = input(26, title="Kijun Sen Periods")\nsenkouSpanBPeriods = input(52, title="Senkou Span B Periods")\ndisplacement = input(26, title="Displacement")\n\n// Calculating the Ichimoku lines\ntenkanSen = (highest(high, tenkanPeriods) + lowest(low, tenkanPeriods)) / 2\nkijunSen = (highest(high, kijunPeriods) + lowest(low, kijunPeriods)) / 2\nsenkouSpanA = (tenkanSen + kijunSen) / 2\nsenkouSpanB = (highest(high, senkouSpanBPeriods) + lowest(low, senkouSpanBPeriods)) / 2\nchikouSpan = close[displacement]\n\n// Plotting the Ichimoku Cloud\np1 = plot(tenkanSen, color=color.red, title="Tenkan Sen")\np2 = plot(kijunSen, color=color.blue, title="Kijun Sen")\np3 = plot(senkouSpanA, color=color.green, title="Senkou Span A", offset=displacement)\np4 = plot(senkouSpanB, color=color.orange, title="Senkou Span B", offset=displacement)\nfill(p1, p2, color=color.purple, transp=80, title="Cloud")\n\n// Buy and Sell conditions\nbuyCondition = crossover(tenkanSen, kijunSen) and close > max(senkouSpanA, senkouSpanB)[displacement]\nsellCondition = crossunder(tenkanSen, kijunSen) and close < min(senkouSpanA, senkouSpanB)[displacement]\n\n// Execute trade if conditions are met\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n    \nif (sellCondition)\n    strategy.close("Buy")\n\n// Strategy exit conditions\nstrategy.close("Buy", when = crossunder(tenkanSen, kijunSen) or close < min(senkouSpanA, senkouSpanB)[displacement])\n\n// Plot buy/sell signals\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sellCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n\n'

class SMCloudSoaringHighYieldDailyTradingStrategyf9d85e(PinePortBase, IStrategy):
    source_id = "SM_f9d85e10a73b0d24"
    source_file = '高收益日线交易策略Cloud-Soaring-High-Yield-Daily-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'tenkanPeriods': 9, 'kijunPeriods': 26, 'senkouSpanBPeriods': 52, 'displacement': 26}
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
