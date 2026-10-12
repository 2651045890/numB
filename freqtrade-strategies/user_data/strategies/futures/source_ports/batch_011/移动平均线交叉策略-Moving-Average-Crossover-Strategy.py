"""batch_011 port of 移动平均线交叉策略-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-06 00:00:00\nend: 2024-06-13 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © okolienicholas\n\n//@version=5\nstrategy("Moving Average Crossover Strategy", overlay=true)\n\n// Input parameters\nfast_length = input(9, title="Fast MA Length")\nslow_length = input(21, title="Slow MA Length")\nsource = close\naccount_balance = input(100, title="Account Balance") // Add your account balance here\n\n// Calculate moving averages\nfast_ma = ta.sma(source, fast_length)\nslow_ma = ta.sma(source, slow_length)\n\n// Plot moving averages\nplot(fast_ma, color=color.blue, title="Fast MA")\nplot(slow_ma, color=color.red, title="Slow MA")\n\n// Generate buy/sell signals\nbuy_signal = ta.crossover(fast_ma, slow_ma)\nsell_signal = ta.crossunder(fast_ma, slow_ma)\n\n// Plot buy/sell signals\nplotshape(buy_signal, style=shape.triangleup, location=location.belowbar, color=color.green, size=size.small, title="Buy Signal")\nplotshape(sell_signal, style=shape.triangledown, location=location.abovebar, color=color.red, size=size.small, title="Sell Signal")\n\n// Calculate the risk per trade\nrisk_per_trade = account_balance * 0.01\n\n// Calculate the number of shares to buy\nshares_to_buy = risk_per_trade / (high - low)\n\n// Calculate the profit or loss\nprofit_or_loss = strategy.netprofit\n\n// Adjust the position size based on the profit or loss\nif (profit_or_loss > 0)\n    shares_to_buy = shares_to_buy * 1.1 // Increase the position size by 10% when in profit\nelse\n    shares_to_buy = shares_to_buy * 0.9 // Decrease the position size by 10% when in loss\n\n// Execute orders\nif (buy_signal)\n    strategy.entry("Buy", strategy.long, qty=shares_to_buy)\n    \nif (sell_signal)\n    strategy.entry("Sell", strategy.short, qty=shares_to_buy)\n'

class SM6AAE68A2B16581AF(PinePortBase, IStrategy):
    source_id = "SM_6aae68a2b16581af"
    source_file = '移动平均线交叉策略-Moving-Average-Crossover-Strategy.md'
    timeframe = '5m'
    can_short = True
    source_defaults = {'fast_length': 9, 'slow_length': 21, 'account_balance': 100}
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
