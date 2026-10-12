"""batch_012 port of 金叉死叉长线多因子策略Golden-Cross-Death-Cross-Long-term-Multi-factor-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-16 00:00:00\nend: 2024-01-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Long Only Multi-Indicator Strategy", shorttitle="LOMIS", overlay=true)\n\n// Inputs\nlengthMAFast = input(10, title="Fast MA Length")\nlengthMASlow = input(50, title="Slow MA Length")\nrsiLength = input(14, title="RSI Length")\nrsiOverbought = input(70, title="RSI Overbought Level")\nrsiOversold = input(30, title="RSI Oversold Level")\natrLength = input(14, title="ATR Length")\nriskMultiplier = input(1.5, title="Risk Multiplier for SL and TP")\n\n// Moving averages\nmaFast = sma(close, lengthMAFast)\nmaSlow = sma(close, lengthMASlow)\n\n// RSI\nrsi = rsi(close, rsiLength)\n\n// ATR\natr = atr(atrLength)\n\n// Long condition\nlongCondition = crossover(maFast, maSlow) and rsi < rsiOverbought\n\n// Entering long trades\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    slLong = close - atr * riskMultiplier\n    tpLong = close + atr * riskMultiplier * 2\n    strategy.exit("SL Long", "Long", stop=slLong)\n    strategy.exit("TP Long", "Long", limit=tpLong)\n\n// Plotting\nplot(maFast, color=color.red)\nplot(maSlow, color=color.blue)\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.blue)\n\n'

class SMGoldenCrossDeathCrossLongtermMultifactorStrategy599d06(PinePortBase, IStrategy):
    source_id = "SM_599d064cfa5ccb9a"
    source_file = '金叉死叉长线多因子策略Golden-Cross-Death-Cross-Long-term-Multi-factor-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'lengthMAFast': 10, 'lengthMASlow': 50, 'rsiLength': 14, 'rsiOverbought': 70, 'rsiOversold': 30, 'atrLength': 14, 'riskMultiplier': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
