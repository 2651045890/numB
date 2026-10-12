"""batch_012 port of 黄金分割与相对强弱RSI策略Fibonacci-Golden-Ratio-and-Relative-Strength-RSI-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-26 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © MohamedYAbdelaziz\n\n// Intraday Trading\n// Best used for Short Timeframes [1-30 Minutes]\n// If you have any modifications please tell me to update it\n\n//@version=4\nstrategy(title="Fibonacci + RSI - Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100, initial_capital=10000, currency=currency.USD)\n\n// Inputs\ntimeFilter = year >= 2000\n    // Stop Loss %\nloss_percent = input(title="Stop Loss (%)", minval=0.0, step=0.1, defval=2) * 0.001\n    // RSI Inputs\nlen = input(title="[RSI] Length", minval=0, step=1, defval=14)\noverSold = input(title="[RSI] Over Sold %", defval=30)\noverBought = input(title="[RSI] Over Bought %", defval=70)\n    // Fibonacci Levels\nlength = input(title="[Fibonacci] Length", defval=200, minval=1)\nsrc = input(hlc3, title="[Fibonacci] Source")\nmult = input(title="[Fibonacci] Multiplier", defval=3.0, minval=0.001, maxval=50)\nlevel = input(title="[Fibonacci] Level", defval=764)\n\n\n// Calculate Fibonacci\nbasis = vwma(src, length)\ndev = mult * stdev(src, length)\nfu764= basis + (0.001*level*dev)\nfu1= basis + (1*dev)\nfd764= basis - (0.001*level*dev)\nfd1= basis - (1*dev)\n\n// Calculate RSI\nvrsi = rsi(close, len)\n\n// Calculate the Targets\ntargetUp = fd764\ntargetDown = fu764\n    // Actual Targets\nbought = strategy.position_size[0] > strategy.position_size[1]\nexit_long = valuewhen(bought, targetUp, 0)\nsold = strategy.position_size[0] < strategy.position_size[1]\nexit_short = valuewhen(sold, targetDown, 0)\n\n// Calculate Stop Losses\nstop_long = strategy.position_avg_price * (1 - loss_percent)\nstop_short = strategy.position_avg_price * (1 + loss_percent)\n\n// Conditions to Open Trades\nopenLong = low < fd1 and crossover(vrsi[1], overSold)\nopenShort = high > fu1 and crossunder(vrsi[1], overBought)\n\n// Conditions to Close Trades\ncloseLong = high > exit_long\ncloseShort = low < exit_short \n\n\n// Plots\nplot(basis, color=color.blue, linewidth=2, title="[Fibonacci Level] Basis")\nplot(fu764, color=color.white, linewidth=1, title="[Fibonacci Level] Short Target")\nplot(fu1, color=color.red, linewidth=2, title="1", title="[Fibonacci Level] Top")\nplot(fd764, color=color.white, linewidth=1, title="[Fibonacci Level] Long Target")\nplot(fd1, color=color.green, linewidth=2, title="1", title="[Fibonacci Level] Bottom")\n\n\n// Strategy Orders\nif timeFilter\n    // Entry Orders\n    strategy.entry(id="Long", long=true, when=openLong and high < targetUp, limit=close)\n    strategy.entry(id="Short", long=false, when=openShort and low > targetDown, limit=close)\n\n    // Exit Orders\n    strategy.exit(id="Long", when=closeLong and strategy.position_size > 0, limit=exit_long, stop=stop_long)\n    strategy.exit(id="Short", when=closeShort and strategy.position_size < 0, limit=exit_short, stop=stop_short)\n'

class SMRSIFibonacciGoldenRatioandRelativeStrengthRSIStrategy6814ce(PinePortBase, IStrategy):
    source_id = "SM_6814cef0ff3cc523"
    source_file = '黄金分割与相对强弱RSI策略Fibonacci-Golden-Ratio-and-Relative-Strength-RSI-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'len': 14, 'overSold': 30, 'overBought': 70, 'length': 200, 'src': 'hlc3', 'mult': 3.0, 'level': 764}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
