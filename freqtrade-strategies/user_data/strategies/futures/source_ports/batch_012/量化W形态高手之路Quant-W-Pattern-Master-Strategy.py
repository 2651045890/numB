"""batch_012 port of 量化W形态高手之路Quant-W-Pattern-Master-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Combined Strategy", overlay=true)\n\n// Input parameters for the W pattern with high volume\nwBottomDepth_W = input.int(3, title="W Bottom Depth", minval=1)\nvolumeMultiplier_W = input.int(2, title="Volume Multiplier", minval=1)\n\n// Calculate moving averages for the W pattern\nmaShort = ta.sma(close, 10)\nmaLong = ta.sma(close, 30)\n\n// Find W pattern\nwBottom = ta.crossover(maShort, maLong) and ta.crossover(maShort[1], maLong[1])\n\n// Check for high volume\nisHighVolume = volume > volumeMultiplier_W * ta.sma(volume, 20)\n\n// Strategy logic for the W pattern with high volume\nif (wBottom and isHighVolume)\n    strategy.entry("W Pattern Buy", strategy.long)\n\n// Plot shapes to highlight W pattern and high volume\nplotshape(series=wBottom and isHighVolume, title="W Bottom with High Volume", color=color.new(color.green, 0), style=shape.triangleup, location=location.belowbar, size=size.small)\n\n// Strategy logic for the second strategy\nlongCondition_My = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))\nif (longCondition_My)\n    strategy.entry("Long Entry", strategy.long)\n\nshortCondition_My = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))\nif (shortCondition_My)\n    strategy.entry("Short Entry", strategy.short)\n\n'

class SMWQuantWPatternMasterStrategy7ebae4(PinePortBase, IStrategy):
    source_id = "SM_7ebae47587d3f7b0"
    source_file = '量化W形态高手之路Quant-W-Pattern-Master-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'wBottomDepth_W': 3, 'volumeMultiplier_W': 2}
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
