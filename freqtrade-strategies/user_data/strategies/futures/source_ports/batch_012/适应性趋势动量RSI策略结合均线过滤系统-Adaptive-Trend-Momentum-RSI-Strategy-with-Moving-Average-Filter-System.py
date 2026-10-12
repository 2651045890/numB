"""batch_012 port of 适应性趋势动量RSI策略结合均线过滤系统-Adaptive-Trend-Momentum-RSI-Strategy-with-Moving-Average-Filter-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-11-11 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Simple RSI Strategy - Adjustable Levels with Lookback Limit and 30-Day MA", overlay=true)\n\n// Parameters\nrsi_length = input.int(12, title="RSI Length", minval=1)  // RSI period\nrsi_overbought = input.int(70, title="RSI Overbought Level", minval=1, maxval=100)  // Overbought level\nrsi_oversold = input.int(62, title="RSI Oversold Level", minval=1, maxval=100)  // Oversold level\nma_length = input.int(90, title="Moving Average Length", minval=1)  // Moving Average period\n\n// Calculate lookback period (2000 days)\nlookback_period = 2500\nstart_date = timestamp(year(timenow), month(timenow), dayofmonth(timenow) - lookback_period)\n\n// RSI Calculation\nrsi_value = ta.rsi(close, rsi_length)\n\n// 30-Day Moving Average Calculation\nma_value = ta.sma(close, ma_length)\n\n// Buy Condition: Buy when RSI is above the overbought level\nlong_condition = rsi_value > rsi_overbought\n\n// Sell Condition: Sell when RSI drops below the oversold level\nsell_condition = rsi_value < rsi_oversold\n\n// Check if current time is within the lookback period\nin_lookback_period = (time >= start_date)\n\n// Execute Buy with 100% equity if within lookback period\nif (long_condition and strategy.position_size == 0 and in_lookback_period)\n    strategy.entry("Buy", strategy.long, qty=strategy.equity / close)\n\nif (sell_condition and strategy.position_size > 0)\n    strategy.close("Buy")\n\n// Plot RSI on a separate chart for visualization\nhline(rsi_overbought, "Overbought", color=color.red)\nhline(rsi_oversold, "Oversold", color=color.green)\nplot(rsi_value, title="RSI", color=color.blue)\n\n// Plot the 30-Day Moving Average on the chart\nplot(ma_value, title="30-Day MA", color=color.orange, linewidth=2)\n\n'

class SMRSIAdaptiveTrendMomentumRSIStrategywithMovingAverageFilbe79d9(PinePortBase, IStrategy):
    source_id = "SM_be79d9bb8c6ccb98"
    source_file = '适应性趋势动量RSI策略结合均线过滤系统-Adaptive-Trend-Momentum-RSI-Strategy-with-Moving-Average-Filter-System.md'
    timeframe = '1d'
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
