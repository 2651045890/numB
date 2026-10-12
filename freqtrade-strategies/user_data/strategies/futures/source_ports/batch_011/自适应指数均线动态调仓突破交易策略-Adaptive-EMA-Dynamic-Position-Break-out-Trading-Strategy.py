"""batch_011 port of 自适应指数均线动态调仓突破交易策略-Adaptive-EMA-Dynamic-Position-Break-out-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Crossover with TP and SL (Buy only) and Break-even", overlay=true)\n\n// EMA sozlamalari\nemaFastLength = input.int(25, title="Fast EMA Length")\nemaSlowLength = input.int(100, title="Slow EMA Length")\n\n// Hisoblash\nemaFast = ta.ema(close, emaFastLength)\nemaSlow = ta.ema(close, emaSlowLength)\n\n// Kesishishni aniqlash\nbullishCross = ta.crossover(emaFast, emaSlow) // EMA 25 EMA 100 ni yuqoriga kesib o\'tganda\n\n// EMA 100 tagidagi oxirgi qizil shamning tagini olish\nlastRedCandleLow = ta.valuewhen(close < open and close < emaSlow, low, 0) // EMA 100 pastidagi qizil shamning tagi\n\n// TP va SL darajalarini hisoblash\nlongSL = lastRedCandleLow\nlongTP = close + 3 * (close - longSL) // TP SL ga nisbatan 1:2 masofada\n\n// Savdoni ochish va 2% foyda bo\'lganda SLni break-even ga o‘zgartirish\nif (bullishCross)\n    strategy.entry("Buy", strategy.long)  // Buy pozitsiyasini ochish\n    strategy.exit("Exit Buy", "Buy", stop=longSL, limit=longTP)  // SL va TP qo\'yish\n\n    // 2% foyda bo\'lganda SLni break-even ga o\'zgartirish\n    if (strategy.position_size > 0)\n        profitPercentage = (close - strategy.position_avg_price) / strategy.position_avg_price * 100\n        if (profitPercentage >= 2)\n            strategy.exit("Exit Buy BE", "Buy", stop=strategy.position_avg_price) // SLni break-even ga o\'zgartirish\n\n// Signalni ko\'rsatish\nplotshape(bullishCross, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\n\n// // TP va SL chizish\n// if (bullishCross)\n//     line.new(x1=bar_index, y1=longSL, x2=bar_index+1, y2=longSL, color=color.red, width=1, extend=extend.none)\n//     line.new(x1=bar_index, y1=longTP, x2=bar_index+1, y2=longTP, color=color.green, width=1, extend=extend.none)\n//     label.new(bar_index, longSL, text="SL: " + str.tostring(longSL), style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)\n//     label.new(bar_index, longTP, text="TP: " + str.tostring(longTP), style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)\n\n// EMA chizish\nplot(emaFast, color=color.blue, title="Fast EMA (25)")\nplot(emaSlow, color=color.orange, title="Slow EMA (100)")\n\n// Alert qo\'shish\nalertcondition(bullishCross, title="Buy Signal Alert", message="EMA 25 crossed above EMA 100! Buy Signal!")\n'

class SMBB94E5AAF5D2A15D(PinePortBase, IStrategy):
    source_id = "SM_bb94e5aaf5d2a15d"
    source_file = '自适应指数均线动态调仓突破交易策略-Adaptive-EMA-Dynamic-Position-Break-out-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'emaFastLength': 25, 'emaSlowLength': 100}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
