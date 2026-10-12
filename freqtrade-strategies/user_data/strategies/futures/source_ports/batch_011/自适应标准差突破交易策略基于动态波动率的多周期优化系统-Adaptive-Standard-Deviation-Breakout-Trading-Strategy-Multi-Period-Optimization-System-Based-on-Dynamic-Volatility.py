"""batch_011 port of 自适应标准差突破交易策略基于动态波动率的多周期优化系统-Adaptive-Standard-Deviation-Breakout-Trading-Strategy-Multi-Period-Optimization-System-Based-on-Dynamic-Volatility.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-01 00:00:00\nend: 2024-06-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("MikEy Scali 3 STD Dev Buy Strategy with TP and SL", overlay=true)\n\n// Input parameters for the strategy\nlength = input.int(20, title="Standard Deviation Length", minval=1)\nsrc = input(close, title="Source")\nmult = input.float(3.0, title="Standard Deviation Multiplier", step=0.1)\n\n// Input for the take profit and stop loss percentages\ntakeProfitPerc = input.float(1.0, title="Take Profit Percentage", step=0.1) / 100\nstopLossPerc = input.float(0.5, title="Stop Loss Percentage", step=0.1) / 100\n\n// Input parameters for the backtesting range\ntestStartYear = input.int(2023, title="Backtest Start Year", minval=2000)\ntestStartMonth = input.int(1, title="Backtest Start Month", minval=1, maxval=12)\ntestStartDay = input.int(1, title="Backtest Start Day", minval=1, maxval=31)\n\ntestEndYear = input.int(2024, title="Backtest End Year", minval=2000)\ntestEndMonth = input.int(12, title="Backtest End Month", minval=1, maxval=12)\ntestEndDay = input.int(31, title="Backtest End Day", minval=1, maxval=31)\n\n// Define the backtesting range\ntestStartTime = timestamp(testStartYear, testStartMonth, testStartDay, 00, 00)\ntestEndTime = timestamp(testEndYear, testEndMonth, testEndDay, 23, 59)\n\n// Determine if the current bar is within the backtesting range\ninBacktestRange = (time >= testStartTime) and (time <= testEndTime)\n\n// Calculate the moving average and standard deviation\nma = ta.sma(src, length)\nstd_dev = ta.stdev(src, length)\n\n// Calculate upper and lower bands\nupper_band = ma + (std_dev * mult)\nlower_band = ma - (std_dev * mult)\n\n// Buy condition within the backtesting range\nbuyCondition = inBacktestRange and ta.crossover(src, lower_band)\n\n// Plot the buy signal on the chart\nplotshape(series=buyCondition, location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\n\n// Execute buy orders based on the condition within the backtesting range\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\n// Calculate the take profit and stop loss prices when a position is opened\nentryPrice = na(strategy.opentrades.entry_price(0)) ? src : strategy.opentrades.entry_price(0)\ntakeProfitPrice = entryPrice * (1 + takeProfitPerc)\nstopLossPrice = entryPrice * (1 - stopLossPerc)\n\n// Take profit condition\ntakeProfitCondition = strategy.position_size > 0 and close >= takeProfitPrice\n\n// Stop loss condition\nstopLossCondition = strategy.position_size > 0 and close <= stopLossPrice\n\n// Execute sell order when take profit condition is met within the backtesting range\nif (takeProfitCondition and inBacktestRange)\n    strategy.close("Buy", "Take Profit")\n\n// Execute sell order when stop loss condition is met within the backtesting range\nif (stopLossCondition and inBacktestRange)\n    strategy.close("Buy", "Stop Loss")\n\n// Plot the moving average and the bands\nplot(ma, color=color.blue, title="Moving Average")\nplot(upper_band, color=color.red, title="Upper Band (3 STD)")\nplot(lower_band, color=color.green, title="Lower Band (3 STD)")\n\n// Optional: Plot the source\nplot(src, color=color.gray, title="Source")\n\n// Add labels for clarity\nbgcolor(buyCondition ? color.new(color.green, 90) : na, offset=-1, title="Buy Signal Background")\n\n// Optional: Highlight the backtesting range on the chart\nbgcolor(inBacktestRange ? color.new(color.blue, 90) : na, title="Backtest Range Background")\n\n// Plot the take profit and stop loss levels if a position is open\nplot(strategy.position_size > 0 ? takeProfitPrice : na, color=color.orange, title="Take Profit Level")\nplot(strategy.position_size > 0 ? stopLossPrice : na, color=color.red, title="Stop Loss Level")'

class SM50AA95D5F7CE275B(PinePortBase, IStrategy):
    source_id = "SM_50aa95d5f7ce275b"
    source_file = '自适应标准差突破交易策略基于动态波动率的多周期优化系统-Adaptive-Standard-Deviation-Breakout-Trading-Strategy-Multi-Period-Optimization-System-Based-on-Dynamic-Volatility.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'length': 20, 'mult': 3.0, 'takeProfitPerc': 1.0, 'stopLossPerc': 0.5, 'testStartYear': 2023, 'testStartMonth': 1, 'testStartDay': 1, 'testEndYear': 2024, 'testEndMonth': 12, 'testEndDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
