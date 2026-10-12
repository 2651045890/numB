"""batch_012 port of 长期趋势SMA均线交叉量化策略-Long-term-Trend-SMA-Crossover-Quantitative-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2025-01-04 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=6\nstrategy("Long-Term Growing Stock Strategy", overlay=true)\n// Date Range\n// STEP 1. Create inputs that configure the backtest\'s date range\nuseDateFilter = input.bool(true, title="Filter Date Range of Backtest",group="Backtest Time Period")\nbacktestStartDate = input(timestamp("1 Jan 2014"),title="Start Date", group="Backtest Time Period",tooltip="This start date is in the time zone of the exchange " + "where the chart\'s instrument trades. It doesn\'t use the time " +"zone of the chart or of your computer.")\nbacktestEndDate = input(timestamp("31 Dec 2024"), title="End Date", group="Backtest Time Period")\n// STEP 2. See if current bar falls inside the date range\ninTradeWindow = true\n\n\n// Calculate EMAs\n// ema20 = ta.ema(close, ema20_length)\n// ema60 = ta.ema(close, ema60_length)\n// ema120 = ta.ema(close, ema120_length)\nsma5 = ta.sma(close, 5)\nsma10 = ta.sma(close, 10)\nsma20 = ta.sma(close, 20)\nsma60 = ta.sma(close, 60)\nsma120 = ta.sma(close, 120)\n\n// Long-term growth condition: EMA 20 > EMA 60 > EMA 120\nlongTermGrowth = sma20 > sma60\n//  and ema60 > ema120\n\n// Entry condition: Stock closes below EMA 20 and then rises back above EMA 10\n\n// entryCondition = ta.crossover(close, ema20) or (close[1] < ema20[1] and close > ema20)\nentryCondition =  sma5[1] <= sma20[1] and sma5 > sma20\n// ta.crossover(sma5, sma20)\n\n// Exit condition: EMA 20 drops below EMA 60\n// exitCondition = ema5 < ema60 or (year == 2024 and month == 12 and dayofmonth == 30)\nexitCondition = ta.crossover(sma20, sma5)\n\n// Execute trades\nif entryCondition and inTradeWindow\n    strategy.entry("Long Entry", strategy.long)\n\nif exitCondition and inTradeWindow\n    strategy.close("Long Entry")\n// plotchar(true, char="sma5: " + str.tostring(sma5))\n// plotchar(true, char="sma5: " + sma20)\n// label.new(x=bar_index, y=high + 10, text="SMA 5: " + str.tostring(sma5), color=color.blue, style=label.style_label_down, textcolor=color.white, size=size.small)\n// label.new(x=bar_index, y=low, text="SMA 20: " + str.tostring(sma20), color=color.red, style=label.style_label_down, textcolor=color.white, size=size.small)\n\n\n// x = time + (time - time[1]) * offset_x\n\n//     var label lab = na\n//     label.delete(lab)\n//     lab := label.new(x=x, y=0, text=txt, xloc=xloc.bar_time, yloc=yloc.belowbar, color=color.red, textcolor=color.black, size=size.normal, style=label.style_label_up)\n//     label.set_x(lab, x)\n\n\n\n// Plot EMAs for visualization\n// plot(ema20, color=color.red, title="EMA 20")\n// plot(ema60, color=color.green, title="EMA 60")\n// plot(ema120, color=color.blue, title="EMA 120")\n'

class SMSMALongtermTrendSMACrossoverQuantitativeStrategya14a6c(PinePortBase, IStrategy):
    source_id = "SM_a14a6cb72aeafc0f"
    source_file = '长期趋势SMA均线交叉量化策略-Long-term-Trend-SMA-Crossover-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'useDateFilter': True, 'backtestStartDate': 'timestamp("1 Jan 2014")', 'backtestEndDate': 'timestamp("31 Dec 2024")'}
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
