"""batch_012 port of 高级双均线动量趋势跟踪交易系统Advanced-Dual-Moving-Average-Momentum-Trend-Following-Trading-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-10-01 00:00:00\nend: 2024-10-31 23:59:59\nperiod: 3h\nbasePeriod: 3h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n\nstrategy(\'Nifty 30m SMA Crossover Long\', overlay=true)\n\nstart = timestamp(2020, 1, 1, 0, 0)\nend = timestamp(2024, 12, 31, 0, 0)\n\nSlowSma = ta.sma(close, 31)\nFastSma = ta.sma(close, 11)\nFilterSma = ta.sma(close, 5)\n\nplot(SlowSma, title=\'Sma 31\', color=color.new(color.green, 0))\nplot(FastSma, title=\'Sma 11\', color=color.new(color.red, 0))\nplot(FilterSma, title=\'Filter Sma 5\', color=color.new(color.black, 0))\n\n// strategy \nLongEntry = FastSma > SlowSma and close > FilterSma\nLongExit = FastSma < SlowSma\n\nMyQty = 10000000 / close\n\n// // Plot signals to chart\n// plotshape(not LongExit and strategy.position_size > 0 and bIndicator, title=\'Hold\', location=location.abovebar, color=color.new(color.blue, 0), style=shape.square, text=\'Hold\', textcolor=color.new(color.blue, 0))\n// plotshape(LongExit and bIndicator and strategy.position_size > 0, title=\'Exit\', location=location.belowbar, color=color.new(color.red, 0), style=shape.triangledown, text=\'Sell\', textcolor=color.new(color.red, 0))\n// plotshape(LongEntry and strategy.position_size == 0 and bIndicator, \'\', shape.arrowup, location.abovebar, color.new(color.green, 0), text=\'Buy\', textcolor=color.new(color.green, 0))\n// plotshape(not LongEntry and strategy.position_size == 0 and bIndicator, \'\', shape.circle, location.belowbar, color.new(color.yellow, 0), text=\'Wait\', textcolor=color.new(color.black, 0))\n\n\nif time >= start and time < end\n    strategy.entry(\'Enter Long\', strategy.long, qty=1, when=LongEntry)\n    strategy.close(\'Enter Long\', when=LongExit)\n\n\n'

class SMAdvancedDualMovingAverageMomentumTrendFollowingTradingSbdb325(PinePortBase, IStrategy):
    source_id = "SM_bdb325dc85fa5f2b"
    source_file = '高级双均线动量趋势跟踪交易系统Advanced-Dual-Moving-Average-Momentum-Trend-Following-Trading-System.md'
    timeframe = '3h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
