"""batch_011 port of 移动平均和随机指标交易策略-Moving-Average-and-Stochastic-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-25 00:00:00\nend: 2024-02-01 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Moving Average and Stochastic Strategy 80% ", overlay=true)\n\n// Moving Average Settings\nmaShortLength = input(5, title="Short MA Length")\nmaLongLength = input(20, title="Long MA Length")\n\n// Stochastic Settings\nstochLength = input(14, title="Stochastic Length")\nsmoothK = input(3, title="Stochastic %K")\nsmoothD = input(3, title="Stochastic %D")\nstochOverbought = 80\nstochOversold = 20\n\n// Profit Target Settings\nprofitTarget = input(1, title="Profit Target (%)") // 1% profit target\n\n// Calculate Moving Averages\nmaShort = sma(close, maShortLength)\nmaLong = sma(close, maLongLength)\n\n// Calculate Stochastic\nk = sma(stoch(close, high, low, stochLength), smoothK)\nd = sma(k, smoothD)\n\n// Entry Conditions\nlongConditionMA = crossover(maShort, maLong) and k < stochOversold\nshortConditionMA = crossunder(maShort, maLong) and k > stochOverbought\n\n// Opposite Conditions\noppositeLongConditionMA = crossunder(maShort, maLong) and k < stochOversold\noppositeShortConditionMA = crossover(maShort, maLong) and k > stochOverbought\n\n// Strategy Logic\nif (longConditionMA)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Exit Buy", "Buy", profit=close * (50 + profitTarget / 100))\n\nif (shortConditionMA)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Exit Sell", "Sell", profit=close * (20 - profitTarget / 100))\n\n// Opposite Strategy Logic\nif (oppositeLongConditionMA)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Exit Sell", "Sell", profit=close * (50 - profitTarget / 100))\n\nif (oppositeShortConditionMA)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Exit Buy", "Buy", profit=close * (20 + profitTarget / 100))\n\n// Plot Moving Averages\nplot(maShort, color=color.blue, title="Short MA")\nplot(maLong, color=color.red, title="Long MA")\n\n// Plot Stochastic\nhline(stochOverbought, "Overbought", color=color.red)\nhline(stochOversold, "Oversold", color=color.green)\nplot(k, color=color.black, title="Stochastic %K")'

class SMCC053F8B02DF8488(PinePortBase, IStrategy):
    source_id = "SM_cc053f8b02df8488"
    source_file = '移动平均和随机指标交易策略-Moving-Average-and-Stochastic-Trading-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'maShortLength': 5, 'maLongLength': 20, 'stochLength': 14, 'smoothK': 3, 'smoothD': 3, 'profitTarget': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
