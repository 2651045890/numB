"""batch_012 port of 高级均值回归交易策略基于标准差的动态区间突破系统-Advanced-Mean-Reversion-Trading-Strategy-Dynamic-Range-Breakout-System-Based-on-Standard-Deviation.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-01 00:00:00\nend: 2024-06-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Simple Mean Reversion Strategy [nn1]", overlay=true)\n\n// Input parameters\nlength = input.int(30, "SMA Length", minval=1)\nstd_dev_threshold = input.float(2, "Standard Deviation Threshold", minval=0.1, step=0.1)\n\n// Calculate SMA and Standard Deviation\nsma = ta.sma(close, length)\nstd_dev = ta.stdev(close, length)\n\n// Calculate upper and lower bands\nupper_band = sma + std_dev * std_dev_threshold\nlower_band = sma - std_dev * std_dev_threshold\n\n// Plot SMA and bands\nplot(sma, "SMA", color.blue)\nplot(upper_band, "Upper Band", color.red)\nplot(lower_band, "Lower Band", color.green)\n\n// Trading logic\nif (close <= lower_band)\n    strategy.entry("Long", strategy.long)\nelse if (close >= upper_band)\n    strategy.entry("Short", strategy.short)\n\n// Exit logic\nif (ta.crossover(close, sma))\n    strategy.close("Long")\nif (ta.crossunder(close, sma))\n    strategy.close("Short")\n\n'

class SMAdvancedMeanReversionTradingStrategyDynamicRangeBreakou778462(PinePortBase, IStrategy):
    source_id = "SM_7784628493257320"
    source_file = '高级均值回归交易策略基于标准差的动态区间突破系统-Advanced-Mean-Reversion-Trading-Strategy-Dynamic-Range-Breakout-System-Based-on-Standard-Deviation.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 30, 'std_dev_threshold': 2}
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
