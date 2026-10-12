"""batch_012 port of 量子量价策略Quantum-Volume-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-12 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Quantum Volume Strategy")\n\n// Quantum Volume indicator inputs\nqvPeriod = input(14, "Quantum Volume Period")\nqvThreshold = input(1.5, "Quantum Volume Threshold")\n\n// Calculate Quantum Volume\nqv = ta.sma(volume, qvPeriod) / ta.sma(volume, qvPeriod)[1]\n\n// Entry conditions\nenterLong = ta.crossover(qv, qvThreshold)\nenterShort = ta.crossunder(qv, qvThreshold)\n\n// Exit conditions\nexitLong = ta.crossunder(qv, qvThreshold)\nexitShort = ta.crossover(qv, qvThreshold)\n\n// Strategy orders\nif (enterLong)\n    strategy.entry("Long", strategy.long)\nif (enterShort)\n    strategy.entry("Short", strategy.short)\n\nif (exitLong)\n    strategy.close("Long")\nif (exitShort)\n    strategy.close("Short")\n\n// Plot Quantum Volume and threshold\nplot(qv, title = "Quantum Volume", color = color.blue)\nhline(qvThreshold, "Threshold", color = color.red)\n'

class SMQuantumVolumeStrategy3b15e3(PinePortBase, IStrategy):
    source_id = "SM_3b15e3c211fb732c"
    source_file = '量子量价策略Quantum-Volume-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'qvPeriod': 14, 'qvThreshold': 1.5}
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
