"""batch_011 port of 趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-26 00:00:00\nend: 2025-03-25 00:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA Cross Strategy (20MA & 89EMA with 200MA Filter)", overlay=true, initial_capital=10000, currency=currency.USD)\n\n// 1. Moving Average Calculation\nma20  = ta.sma(close, 20)\nema89 = ta.ema(close, 89)\nma200 = ta.sma(close, 200)\n\n// 2. Plot Moving Averages\nplot(ma20, title="20MA", color=color.orange)\nplot(ema89, title="89EMA", color=color.red)\nplot(ma200, title="200MA", color=color.blue)\n\n// 3. ATR and Multipliers\natrValue = ta.atr(14)\nstopLossMultiplier  = 2.0   // Stop Loss: ATR × 2\ntakeProfitMultiplier = 3.0   // Take Profit: ATR × 3\n\n// 4. Entry Signal Conditions\n// Long Signal: Price is above the 200MA and 20MA crosses above 89EMA\nlongSignal  = (close > ma200) and (strategy.position_size == 0) and ta.crossover(ma20, ema89)\n// Short Signal: Price is below the 200MA and 20MA crosses below 89EMA\nshortSignal = (close < ma200) and (strategy.position_size == 0) and ta.crossunder(ma20, ema89)\n\n// Plot Entry Signals (Circles for Reference)\nplotshape(longSignal, title="Long Signal", style=shape.circle, location=location.belowbar, color=color.green, size=size.normal)\nplotshape(shortSignal, title="Short Signal", style=shape.circle, location=location.abovebar, color=color.red, size=size.normal)\n\n// 5. Position Entry and SL/TP Setup (Fixed ATR at Entry)\nif longSignal\n    entryPrice = close\n    lockedATR  = atrValue\n    longStopPrice = entryPrice - lockedATR * stopLossMultiplier\n    longTakeProfitPrice = entryPrice + lockedATR * takeProfitMultiplier\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long_Exit", "Long", stop=longStopPrice, limit=longTakeProfitPrice)\n\nif shortSignal\n    entryPrice = close\n    lockedATR  = atrValue\n    shortStopPrice = entryPrice + lockedATR * stopLossMultiplier\n    shortTakeProfitPrice = entryPrice - lockedATR * takeProfitMultiplier\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short_Exit", "Short", stop=shortStopPrice, limit=shortTakeProfitPrice)\n'

class SM81AA7E251F25A5E2(PinePortBase, IStrategy):
    source_id = "SM_81aa7e251f25a5e2"
    source_file = '趋势过滤多均线交叉ATR风控量化策略-Multi-Moving-Average-Crossover-Strategy-with-Trend-Filter-and-ATR-Risk-Management.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
