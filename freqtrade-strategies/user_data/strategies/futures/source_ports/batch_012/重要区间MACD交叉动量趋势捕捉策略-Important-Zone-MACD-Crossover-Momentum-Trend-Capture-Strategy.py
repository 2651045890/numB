"""batch_012 port of 重要区间MACD交叉动量趋势捕捉策略-Important-Zone-MACD-Crossover-Momentum-Trend-Capture-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-04-03 00:00:00\nend: 2025-04-02 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=5\nstrategy("MACD Crossover Strategy", overlay=false)\n\n// MACD parameters\nfastLength = input(12, "Fast Length")\nslowLength = input(26, "Slow Length")\nsignalLength = input(9, "Signal Length")\n\n// Important zone parameters\nlowerThreshold = input.float(-0.5, "Lower Threshold", step=0.1)\nupperThreshold = input.float(0.5, "Upper Threshold", step=0.1)\n\n// Calculate MACD\n[macdLine, signalLine, _] = ta.macd(close, fastLength, slowLength, signalLength)\n\n// Plot MACD lines\nplot(macdLine, color=color.blue, title="MACD Line")\nplot(signalLine, color=color.orange, title="Signal Line")\nplot(0, color=color.white, title="Zero Line")\nplot(upperThreshold, color=color.gray, style=plot.style_linebr, title="Upper Threshold")\nplot(lowerThreshold, color=color.gray, style=plot.style_linebr, title="Lower Threshold")\n\n// Define crossover conditions\ncrossOverUp = ta.crossover(macdLine, signalLine)\ncrossOverDown = ta.crossunder(macdLine, signalLine)\n\n// Define important crossover zone\nisImportantZone = macdLine >= lowerThreshold and macdLine <= upperThreshold\n\n// Strategy entries\nif (crossOverUp and isImportantZone)\n    strategy.entry("Long", strategy.long)\n\nif (crossOverDown and isImportantZone)\n    strategy.entry("Short", strategy.short)\n\n// Optional: Add exits based on opposite signals\nif (crossOverDown)\n    strategy.close("Long")\n\nif (crossOverUp)\n    strategy.close("Short")\n\n// Plot buy/sell signals\nplotshape(series=crossOverUp and isImportantZone, title="Buy Signal", location=location.bottom, color=color.green, style=shape.triangleup, size=size.small)\nplotshape(series=crossOverDown and isImportantZone, title="Sell Signal", location=location.top, color=color.red, style=shape.triangledown, size=size.small)\n\n'

class SMMACDImportantZoneMACDCrossoverMomentumTrendCaptureStratb751f4(PinePortBase, IStrategy):
    source_id = "SM_b751f49978ced0f0"
    source_file = '重要区间MACD交叉动量趋势捕捉策略-Important-Zone-MACD-Crossover-Momentum-Trend-Capture-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9, 'lowerThreshold': -0.5, 'upperThreshold': 0.5}
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
