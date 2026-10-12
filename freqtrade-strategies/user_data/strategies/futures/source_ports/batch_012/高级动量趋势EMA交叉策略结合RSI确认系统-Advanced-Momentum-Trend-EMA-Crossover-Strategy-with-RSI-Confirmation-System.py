"""batch_012 port of 高级动量趋势EMA交叉策略结合RSI确认系统-Advanced-Momentum-Trend-EMA-Crossover-Strategy-with-RSI-Confirmation-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-24 00:00:00\nend: 2025-03-23 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=5\nstrategy("ema crossover with rsi confirm", overlay=true, initial_capital=100000, currency=currency.USD, calc_on_order_fills=true, calc_on_every_tick=true)\n\n// User Inputs for EMAs and RSI\nshortEmaLength = input.int(9, title="Short EMA Length", minval=1)\nlongEmaLength  = input.int(21, title="Long EMA Length", minval=1)\nrsiPeriod      = input.int(14, title="RSI Period")\n\n// Risk Management Inputs\nstopLossPerc   = input.float(1.0, title="Stop Loss (%)", minval=0.1, step=0.1)\ntakeProfitPerc = input.float(2.0, title="Take Profit (%)", minval=0.1, step=0.1)\n\n// Calculations\nemaShort = ta.ema(close, shortEmaLength)\nemaLong  = ta.ema(close, longEmaLength)\nrsiValue = ta.rsi(close, rsiPeriod)\n\n// Plotting EMAs\nplot(emaShort, color=color.blue, title="Short EMA")\nplot(emaLong, color=color.red,  title="Long EMA")\n\n// Entry Conditions\nlongCondition  = ta.crossover(emaShort, emaLong) and rsiValue > 50\nshortCondition = ta.crossunder(emaShort, emaLong) and rsiValue < 50\n\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n\n// Risk Management Exit Orders\nif (strategy.position_size > 0)\n    strategy.exit("Exit Long", from_entry="Long", \n                  stop=close * (1 - stopLossPerc / 100), \n                  limit=close * (1 + takeProfitPerc / 100))\nif (strategy.position_size < 0)\n    strategy.exit("Exit Short", from_entry="Short", \n                  stop=close * (1 + stopLossPerc / 100), \n                  limit=close * (1 - takeProfitPerc / 100))\n\n// Additional Exit Conditions on Signal Reversal\nif (ta.crossunder(emaShort, emaLong))\n    strategy.close("Long")\nif (ta.crossover(emaShort, emaLong))\n    strategy.close("Short")\n\n'

class SMEMARSIAdvancedMomentumTrendEMACrossoverStrategywithRSIC9e6eb6(PinePortBase, IStrategy):
    source_id = "SM_9e6eb6415d4af1e8"
    source_file = '高级动量趋势EMA交叉策略结合RSI确认系统-Advanced-Momentum-Trend-EMA-Crossover-Strategy-with-RSI-Confirmation-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'shortEmaLength': 9, 'longEmaLength': 21, 'rsiPeriod': 14, 'stopLossPerc': 1.0, 'takeProfitPerc': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
