"""batch_012 port of 量化交易中基于RSI与成交量的高级反转策略-Advanced-RSI-and-Volume-Based-Contrarian-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-01 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("RSI & Volume Contrarian Strategy", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10, pyramiding=0)\n\n//---------------------------\n// Inputs and Parameters\n//---------------------------\nrsiPeriod    = input.int(14, title="RSI Period", minval=1)\noversold     = input.int(30, title="RSI Oversold Level", minval=1, maxval=50)\noverbought   = input.int(70, title="RSI Overbought Level", minval=50, maxval=100)\nvolMAPeriod  = input.int(20, title="Volume MA Period", minval=1)\n\n//---------------------------\n// Indicator Calculations\n//---------------------------\nrsiValue = ta.rsi(close, rsiPeriod)\nvolMA    = ta.sma(volume, volMAPeriod)\n\n//---------------------------\n// Trade Logic\n//---------------------------\n\n// Long Entry: Look for oversold conditions (RSI < oversold)\n//            accompanied by above-average volume (volume > volMA)\n// In an uptrend, oversold conditions with high volume may signal a strong reversal opportunity.\nlongCondition = (rsiValue < oversold) and (volume > volMA)\n\n// Short Entry: When RSI > overbought and volume is above its moving average,\n//              the temporary strength in a downtrend can be exploited contrarily.\nshortCondition = (rsiValue > overbought) and (volume > volMA)\n\nif longCondition\n    strategy.entry("Long", strategy.long)\n\nif shortCondition\n    strategy.entry("Short", strategy.short)\n\n// Exit Logic:\n// Use a simple RSI midline crossover as an exit trigger.\n// For longs, if RSI crosses above 50 (indicating a recovery), exit the long.\n// For shorts, if RSI crosses below 50, exit the short.\nexitLong  = ta.crossover(rsiValue, 50)\nexitShort = ta.crossunder(rsiValue, 50)\n\nif strategy.position_size > 0 and exitLong\n    strategy.close("Long", comment="RSI midline exit")\n    log.info("strategy.position_size > 0 and exitLong")\n\nif strategy.position_size < 0 and exitShort\n    strategy.close("Short", comment="RSI midline exit")\n    log.info("strategy.position_size > 0 and exitLong")\n\n//---------------------------\n// Visualization\n//---------------------------\n\n// Plot the RSI on a separate pane for reference\nplot(rsiValue, title="RSI", color=color.blue, linewidth=2)\nhline(oversold, title="Oversold", color=color.green)\nhline(overbought, title="Overbought", color=color.red)\nhline(50, title="Midline", color=color.gray, linestyle=hline.style_dotted)\n\n// Optionally, you may plot the volume moving average on a hidden pane\nplot(volMA, title="Volume MA", color=color.purple, display=display.none)\n'

class SMRSIAdvancedRSIandVolumeBasedContrarianTradingStrategy05772d(PinePortBase, IStrategy):
    source_id = "SM_05772d9faf368ac1"
    source_file = '量化交易中基于RSI与成交量的高级反转策略-Advanced-RSI-and-Volume-Based-Contrarian-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rsiPeriod': 14, 'oversold': 30, 'overbought': 70, 'volMAPeriod': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
