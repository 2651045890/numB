"""batch_012 port of 高斯通道趋势跟踪与随机相对强弱指标交易策略-Gaussian-Channel-Trend-Following-with-Stochastic-RSI-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2025-02-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Gaussian Channel + Stoch RSI Strategy", overlay=true, margin_long=100, margin_short=100, initial_capital=100000, commission_type=strategy.commission.percent, commission_value=0.1, default_qty_type=strategy.percent_of_equity, default_qty_value=100, pyramiding=1)\n\n// User Inputs\nlength     = input.int(20, "Gaussian Length", minval=5)\nmultiplier = input.float(2.0, "Channel Multiplier", step=0.1)\nrsiLength  = input.int(14, "RSI Length", minval=1)\nstochLength= input.int(14, "Stoch RSI Length", minval=1)\nkLength    = input.int(3, "Stoch K Smoothing", minval=1)\ndLength    = input.int(3, "Stoch D Smoothing", minval=1)\n\n// Gaussian Weighted Moving Average Function\nf_gaussian(source, length) =>\n    half = (length - 1) / 2.0\n    sum = 0.0\n    norm = 0.0\n    // Gaussian standard deviation chosen as length/6 for a smooth curve\n    denom = (length / 6.0) * (length / 6.0)\n    for i = 0 to length - 1\n        x = i - half\n        w = math.exp(-(x * x) / (2 * denom))\n        sum += source[i] * w\n        norm += w\n    sum / norm\n\n// Gaussian Weighted Standard Deviation Function\nf_gaussian_std(source, length) =>\n    half = (length - 1) / 2.0\n    gavg = f_gaussian(source, length)\n    sum = 0.0\n    norm = 0.0\n    denom = (length / 6.0) * (length / 6.0)\n    for i = 0 to length - 1\n        x = i - half\n        w = math.exp(-(x * x)/(2*denom))\n        diff = source[i] - gavg\n        sum += diff * diff * w\n        norm += w\n    math.sqrt(sum/norm)\n\n// Compute Gaussian Channel\ngaussMid = f_gaussian(close, length)\ngaussStd = f_gaussian_std(close, length)\ngaussUpper = gaussMid + gaussStd * multiplier\ngaussLower = gaussMid - gaussStd * multiplier\n\n// Stochastic RSI Calculation\nrsi = ta.rsi(close, rsiLength)\nrsiLowest = ta.lowest(rsi, stochLength)\nrsiHighest = ta.highest(rsi, stochLength)\nstoch = 100 * (rsi - rsiLowest) / math.max(rsiHighest - rsiLowest, 1e-10)\nk = ta.sma(stoch, kLength)\nd = ta.sma(k, dLength)\n\n// Conditions\n// Long entry: Price closes above upper Gaussian line AND Stoch RSI K > D (stochastic is "up")\nlongCondition = close > gaussUpper and k > d\n\n// Exit condition: Price closes below upper Gaussian line\nexitCondition = close < gaussUpper\n\n// Only trade in the specified date range\ninDateRange = time >= timestamp("2018-01-01T00:00:00") and time < timestamp("2069-01-01T00:00:00")\n\n// Submit Orders\nif inDateRange\n    if longCondition and strategy.position_size <= 0\n        strategy.entry("Long", strategy.long)\n    if exitCondition and strategy.position_size > 0\n        strategy.close("Long")\n        \n// Plot Gaussian Channel\nplot(gaussMid, "Gaussian Mid", color=color.new(color.yellow, 0))\nplot(gaussUpper, "Gaussian Upper", color=color.new(color.green, 0))\nplot(gaussLower, "Gaussian Lower", color=color.new(color.red, 0))\n\n'

class SMGaussianChannelTrendFollowingwithStochasticRSITradingSt61d532(PinePortBase, IStrategy):
    source_id = "SM_61d532d4c7d6f2db"
    source_file = '高斯通道趋势跟踪与随机相对强弱指标交易策略-Gaussian-Channel-Trend-Following-with-Stochastic-RSI-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 20, 'multiplier': 2.0, 'rsiLength': 14, 'stochLength': 14, 'kLength': 3, 'dLength': 3}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 1
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
