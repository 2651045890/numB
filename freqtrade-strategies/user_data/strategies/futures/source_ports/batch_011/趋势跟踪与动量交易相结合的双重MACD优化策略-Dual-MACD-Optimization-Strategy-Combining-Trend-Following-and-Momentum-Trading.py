"""batch_011 port of 趋势跟踪与动量交易相结合的双重MACD优化策略-Dual-MACD-Optimization-Strategy-Combining-Trend-Following-and-Momentum-Trading.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-05-08 00:00:00\nend: 2024-05-13 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © sligetit\n\n//@version=5\nstrategy("Improved MACD_VXI Strategy", overlay=true)\n\n// Calculate MACD and Signal Line\nfastLength = input.int(13, title="Fast Length")\nslowLength = input.int(21, title="Slow Length")\nsignalLength = input.int(8, title="Signal Length")\n\nfastMA = ta.ema(close, fastLength)\nslowMA = ta.ema(close, slowLength)\nmacd = fastMA - slowMA\nsignal = ta.sma(macd, signalLength)\n\n// Plot MACD and Signal Line\nplot(macd, color=color.red, linewidth=1)\nplot(signal, color=color.blue, linewidth=2)\n\n// Calculate Cross Signals with Trend Confirmation\nsmaPeriod = input.int(50, title="SMA Period")\nsma = ta.sma(close, smaPeriod)\n\ntrendUp = close > sma\ntrendDown = close < sma\n\ncrossOver = ta.crossover(signal, macd)\ncrossUnder = ta.crossunder(signal, macd)\n\nbuySignal = crossOver and trendUp\nsellSignal = crossUnder and trendDown\n\n// Execute Buy/Sell Operations\nif buySignal\n    strategy.entry("Buy", strategy.long)\nif sellSignal\n    strategy.entry("Sell", strategy.short)\n\n// Extend Signal Confirmation Time Window\nlongSignal = crossOver[1] and trendUp[1]\nshortSignal = crossUnder[1] and trendDown[1]\n\nif longSignal\n    strategy.entry("Buy", strategy.long)\nif shortSignal\n    strategy.entry("Sell", strategy.short)\n\n// Set Fixed Percentage Stop Loss and Take Profit\nstopLossPercent = input.float(1, title="Stop Loss (%)") / 100\ntakeProfitPercent = input.float(2, title="Take Profit (%)") / 100\n\nstopLossPrice = strategy.position_avg_price * (1 - stopLossPercent)\ntakeProfitPrice = strategy.position_avg_price * (1 + takeProfitPercent)\n\nstrategy.exit("Stop Loss/Profit", "Buy", stop=stopLossPrice, limit=takeProfitPrice)\nstrategy.exit("Stop Loss/Profit", "Sell", stop=stopLossPrice, limit=takeProfitPrice)'

class SMBEC4515D278C72D3(PinePortBase, IStrategy):
    source_id = "SM_bec4515d278c72d3"
    source_file = '趋势跟踪与动量交易相结合的双重MACD优化策略-Dual-MACD-Optimization-Strategy-Combining-Trend-Following-and-Momentum-Trading.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 13, 'slowLength': 21, 'signalLength': 8, 'smaPeriod': 50, 'stopLossPercent': 1, 'takeProfitPercent': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
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
