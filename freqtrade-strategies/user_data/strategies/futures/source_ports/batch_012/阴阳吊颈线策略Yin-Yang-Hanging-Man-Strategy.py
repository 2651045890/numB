"""batch_012 port of 阴阳吊颈线策略Yin-Yang-Hanging-Man-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-24 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Doji Candlestick Strategy", shorttitle="Doji", overlay=true)\n\n// Calculate body and shadow sizes\nbodySize = close > open ? close - open : open - close\nupperShadow = high - (open > close ? open : close)\nlowerShadow = (open > close ? close : open) - low\n\n// Define thresholds for identifying different Doji types\ndojiThreshold = 0.05\nlongLeggedDojiThreshold = 0.02\n\n// Buy conditions for different Doji types\ndojiCondition = bodySize <= dojiThreshold and upperShadow > bodySize * 2 and lowerShadow > bodySize * 2\ndragonflyDojiCondition = bodySize <= dojiThreshold and upperShadow > bodySize * 2 and lowerShadow <= bodySize * 0.5\ngravestoneDojiCondition = bodySize <= dojiThreshold and upperShadow <= bodySize * 0.5 and lowerShadow > bodySize * 2\nlongLeggedDojiCondition = bodySize <= longLeggedDojiThreshold and upperShadow > bodySize * 2 and lowerShadow > bodySize * 2\n\n// Buy signal\nbuyCondition = dojiCondition or dragonflyDojiCondition or gravestoneDojiCondition or longLeggedDojiCondition\n\n// Strategy orders\nstrategy.entry("Buy", strategy.long, when=buyCondition)\n\n// Plotting\nplotshape(series=buyCondition, title="Buy Signal", color=color.green, style=shape.triangleup, location=location.belowbar, size=size.small)\n\n'

class SMYinYangHangingManStrategya63470(PinePortBase, IStrategy):
    source_id = "SM_a6347036ad131a1e"
    source_file = '阴阳吊颈线策略Yin-Yang-Hanging-Man-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {}
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
