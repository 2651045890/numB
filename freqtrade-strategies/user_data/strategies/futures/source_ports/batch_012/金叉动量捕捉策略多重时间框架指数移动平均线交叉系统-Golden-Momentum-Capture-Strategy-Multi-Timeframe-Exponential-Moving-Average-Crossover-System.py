"""batch_012 port of 金叉动量捕捉策略多重时间框架指数移动平均线交叉系统-Golden-Momentum-Capture-Strategy-Multi-Timeframe-Exponential-Moving-Average-Crossover-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-30 00:00:00\nend: 2024-07-30 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Golden Crossover", overlay=true)\n\n// Define EMA lengths\nema9_length = 9\nema26_length = 26\nema55_length = 55\n\n// Input parameters\ntimeFrame9 = input.timeframe(\'\', \'Time Frame - EMA 9\')\ntimeFrame26 = input.timeframe(\'\', \'Time Frame - EMA 26\')\ntimeFrame55 = input.timeframe(\'\', \'Time Frame - EMA 55\')\n\n// Request data from specified time frames\nema9 = request.security(syminfo.tickerid, timeFrame9, ta.ema(close, ema9_length))\nema26 = request.security(syminfo.tickerid, timeFrame26, ta.ema(close, ema26_length))\nema55 = request.security(syminfo.tickerid, timeFrame55, ta.ema(close, ema55_length))\n\n// Plot EMAs on the chart\nplot(ema9, color=color.black, title="EMA 9")\nplot(ema26, color=color.green, title="EMA 26")\nplot(ema55, color=color.red, title="EMA 55")\n\n// Define buy condition\nbuy_condition = ta.crossover(ema9, ema26) and ema26 > ema55 //and ema26 > ema55 // (We can activate additional condition to get more accurate signals)\n\n// Define sell condition\nsell_condition = ta.crossunder(ema9, ema26) and (ema26 < ema55) //and ema26 < ema55 // (We can activate additional condition to get more accurate signals)\n\n// Execute buy and sell orders\nif (buy_condition)\n    strategy.entry("Buy", strategy.long)\n\nif (sell_condition)\n    strategy.entry("Sell", strategy.short)\n\n// Optional: Plot buy and sell signals on the chart\nplotshape(series=buy_condition, location=location.belowbar, color=color.green, style=shape.arrowup, title="Buy")\nplotshape(series=sell_condition, location=location.abovebar, color=color.red, style=shape.arrowdown, title="Sell")\n'

class SMGoldenMomentumCaptureStrategyMultiTimeframeExponentialM7f58fe(PinePortBase, IStrategy):
    source_id = "SM_7f58fe20871f8490"
    source_file = '金叉动量捕捉策略多重时间框架指数移动平均线交叉系统-Golden-Momentum-Capture-Strategy-Multi-Timeframe-Exponential-Moving-Average-Crossover-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'timeFrame9': '', 'timeFrame26': '', 'timeFrame55': ''}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
