"""batch_011 port of 趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2025-01-20 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("RSI + ADX + ML-like Strategy (5min)", overlay=true)\n\n// ———— 1. Inputs ————\nrsiLength = input(14, "RSI Length")\nadxLength = input(14, "ADX Length")\nmlLookback = input(20, "ML Lookback (Bars)")\n\n// ———— 2. Calculate Indicators ————\n// RSI\nrsi = ta.rsi(close, rsiLength)\n\n// ADX\n[diPlus, diMinus, adx] = ta.dmi(adxLength, adxLength)\n\n// ———— 3. Simplified ML-like Component (Linear Regression) ————\nvar float predictedClose = na\nsumX = math.sum(bar_index, mlLookback)          // FIXED: Using math.sum()\nsumY = math.sum(close, mlLookback)              // FIXED: Using math.sum()\nsumXY = math.sum(bar_index * close, mlLookback) // FIXED: Using math.sum()\nsumX2 = math.sum(bar_index * bar_index, mlLookback)\n\nslope = (mlLookback * sumXY - sumX * sumY) / (mlLookback * sumX2 - sumX * sumX)\nintercept = (sumY - slope * sumX) / mlLookback\npredictedClose := slope * bar_index + intercept\n\n// ———— 4. Strategy Logic ————\nmlBullish = predictedClose > close\nmlBearish = predictedClose < close\n\nenterLong = ta.crossover(rsi, 30) and adx > 25 and mlBullish\nenterShort = ta.crossunder(rsi, 70) and adx > 25 and mlBearish\n\n// ———— 5. Execute Orders ————\nstrategy.entry("Long", strategy.long, when=enterLong)\nstrategy.entry("Short", strategy.short, when=enterShort)\n\n// ———— 6. Plotting ————\nplot(predictedClose, "Predicted Close", color=color.purple)\nplotshape(enterLong, "Buy", shape.triangleup, location.belowbar, color=color.green)\nplotshape(enterShort, "Sell", shape.triangledown, location.abovebar, color=color.red)'

class SM9EF8ECEF5F90FD3F(PinePortBase, IStrategy):
    source_id = "SM_9ef8ecef5f90fd3f"
    source_file = '趋势增强型RSI-ADX线性回归预测交易策略-Enhanced-Trend-RSI-ADX-Linear-Regression-Prediction-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsiLength': 14, 'adxLength': 14, 'mlLookback': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
