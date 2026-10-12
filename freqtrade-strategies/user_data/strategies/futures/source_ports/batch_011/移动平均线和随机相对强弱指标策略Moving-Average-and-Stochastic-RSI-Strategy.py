"""batch_011 port of 移动平均线和随机相对强弱指标策略Moving-Average-and-Stochastic-RSI-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-25 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Moving Average and Stochastic RSI Strategy", shorttitle="MA+Stoch RSI", overlay=true)\n\n// Input variables\nma1_length = input.int(20, title="MA1 Length")\nma2_length = input.int(50, title="MA2 Length")\nstoch_length = input.int(14, title="Stochastic RSI Length")\noverbought = input.int(80, title="Overbought Level")\noversold = input.int(20, title="Oversold Level")\nrisk_percentage = input.float(2.0, title="Risk Percentage")\n\n// Calculate moving averages\nma1 = ta.sma(close, ma1_length)\nma2 = ta.sma(close, ma2_length)\n\n// Calculate Stochastic RSI\nrsi1 = ta.rsi(close, stoch_length)\nrsiH = ta.highest(rsi1, stoch_length)\nrsiL = ta.lowest(rsi1, stoch_length)\nstoch = (rsi1 - rsiL) / (rsiH - rsiL) * 100\n\n// Determine buy and sell signals based on Stochastic RSI\nbuySignal = ta.crossover(stoch, oversold)\nsellSignal = ta.crossunder(stoch, overbought)\n\n// Plot signals on the chart\nplotshape(buySignal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small)\nplotshape(sellSignal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small)\n\n// Calculate position size based on equity and risk percentage\nequity = strategy.equity\nriskAmount = equity * risk_percentage / 100\npositionSize = riskAmount / ta.atr(14)\n\n// Entry and exit conditions\nvar float stopLoss = na\nvar float takeProfit = na\n\nif buySignal\n    stopLoss := low\n    takeProfit := high\n    strategy.entry("Buy", strategy.long)\nelse if sellSignal\n    strategy.exit("Sell", from_entry="Buy", stop=stopLoss, limit=takeProfit)\n'

class SM2B2B8E4E43131FE7(PinePortBase, IStrategy):
    source_id = "SM_2b2b8e4e43131fe7"
    source_file = '移动平均线和随机相对强弱指标策略Moving-Average-and-Stochastic-RSI-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'ma1_length': 20, 'ma2_length': 50, 'stoch_length': 14, 'overbought': 80, 'oversold': 20, 'risk_percentage': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
