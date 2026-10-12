"""batch_011 port of 趋势突破交易系统移动平均线突破策略-Trend-Breakout-Trading-System-with-Moving-Average-TBMA-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Trend Breakout with SL and TP", overlay=true)\n\n// Parametrlar\nlength = input(25, title="Length for SL Calculation")\ntrendLength = input(20, title="Trend Line Length")\n\n// Trend chizig\'ini hisoblash\ntrendLine = ta.sma(close, trendLength)\n\n// Yopilish narxi trend chizig\'ini yorib o\'tganda signal\nlongSignal = close > trendLine and close[1] <= trendLine\n\n// Oxirgi 7 shamning minimumini hisoblash\nlowestLow = ta.lowest(low, 7)\n\n// Stop Loss darajasini belgilash\nlongSL = lowestLow  // SL oxirgi 7 shamning minimumiga teng\n\n// Take Profit darajasini SL ga nisbatan 2 baravar ko\'p qilib belgilash\nlongTP = longSL + (close - longSL) * 2  // TP 2:1 nisbatida\n\n// Savdo bajarish\nif longSignal\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Take Profit", "Long", limit=longTP)\n    strategy.exit("Stop Loss", "Long", stop=longSL)\n\n// Grafikda trend chizig\'ini chizish\nplot(trendLine, title="Trend Line", color=color.blue, linewidth=2)\n\n// Signal chizish\nplotshape(longSignal, style=shape.labelup, location=location.belowbar, color=color.green, size=size.small, title="Buy Signal")\n\n// SL va TP darajalarini ko\'rsatish\n// if longSignal\n//     // SL chizig\'i\n//     line.new(bar_index, longSL, bar_index + 1, longSL, color=color.red, width=2, style=line.style_dashed)\n//     // TP chizig\'i\n//     line.new(bar_index, longTP, bar_index + 1, longTP, color=color.green, width=2, style=line.style_dashed)\n    \n//     // SL va TP label\'larini ko\'rsatish\n//     label.new(bar_index, longSL, "SL: " + str.tostring(longSL), color=color.red, style=label.style_label_down, textcolor=color.white, size=size.small)\n//     label.new(bar_index, longTP, "TP: " + str.tostring(longTP), color=color.green, style=label.style_label_up, textcolor=color.white, size=size.small)\n'

class SM247106ACA4D41821(PinePortBase, IStrategy):
    source_id = "SM_247106aca4d41821"
    source_file = '趋势突破交易系统移动平均线突破策略-Trend-Breakout-Trading-System-with-Moving-Average-TBMA-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 25, 'trendLength': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
