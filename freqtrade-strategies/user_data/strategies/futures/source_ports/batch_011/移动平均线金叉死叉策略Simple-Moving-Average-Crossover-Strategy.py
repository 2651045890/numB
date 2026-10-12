"""batch_011 port of 移动平均线金叉死叉策略Simple-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-08-21 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © DaynTrading\n\n//@version=4\n// strategy(\n//      title="Simple Moving Average Cross",\n//      overlay=true,\n//      initial_capital=5000,\n//      default_qty_type=strategy.percent_of_equity,\n//      default_qty_value=2,\n//      commission_type=strategy.commission.percent,\n//      commission_value=0.075,\n//      pyramiding=0\n//      )\n\nsma_top_input = input(title="SMA Top", type=input.integer, defval=20)\nsma_mid_input = input(title="SMA Mid", type=input.integer, defval=50)\nsma_low_input = input(title="SMA Low", type=input.integer, defval=200)\n\nbars_long = input(title="Long: After trigger, how many bars to wait?", type=input.integer, defval=5)\nbars_short = input(title="Short: After trigger, how many bars to wait?", type=input.integer, defval=5)\n\nsma_top = sma(close, sma_top_input)\nsma_mid = sma(close, sma_mid_input)\nsma_low = sma(close, sma_low_input)\n\nlong = sma_top > sma_mid and sma_mid > sma_low\nshort = sma_top < sma_mid and sma_mid < sma_low\n\nlong_condition = long and long[bars_long] and not long[bars_long + 1]\nshort_condition = short and short[bars_short] and not short[bars_short + 1]\n\nclose_long = sma_top < sma_mid and sma_mid < sma_low and not long[bars_long + 1]\nclose_short = sma_top > sma_mid and sma_mid > sma_low and not short[bars_short + 1]\n\nplot(sma_top, title="SMA Top", color=#95f252, linewidth=2)\nplot(sma_mid, title="SMA Mid", color=#FF1493, linewidth=2)\nplot(sma_low, title="SMA Low", color=#6a0dad, linewidth=2)\n\nstrategy.entry("LongPosition", strategy.long, when = long_condition)\nstrategy.entry("ShortPosition", strategy.short, when = short_condition)\n    \nstrategy.close("LongPosition", when = close_short)\nstrategy.close("ShortPosition", when = close_long)'

class SM9E3DBD95429A26C7(PinePortBase, IStrategy):
    source_id = "SM_9e3dbd95429a26c7"
    source_file = '移动平均线金叉死叉策略Simple-Moving-Average-Crossover-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'sma_top_input': 20, 'sma_mid_input': 50, 'sma_low_input': 200, 'bars_long': 5, 'bars_short': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
