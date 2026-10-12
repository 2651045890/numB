"""batch_011 port of 自适应VWAP波段基于Garman-Klass波动率动态跟踪策略-Adaptive-VWAP-Bands-with-Garman-Klass-Volatility-Dynamic-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-18 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Adaptive VWAP Bands with Garman Klass Volatility", overlay=true)\n\n// Inputs\nlength = input.int(25, title="Volatility Length")\nvwapLength = input.int(14, title="VWAP Length")\nvol_multiplier = input.float(1,title="Volatility Multiplier")\n\n// Function to calculate Garman-Klass Volatility\nvar float sum_gkv = na\nif na(sum_gkv)\n    sum_gkv := 0.0\n\nsum_gkv := 0.0\nfor i = 0 to length - 1\n    sum_gkv := sum_gkv + 0.5 * math.pow(math.log(high[i]/low[i]), 2) - (2*math.log(2)-1) * math.pow(math.log(close[i]/open[i]), 2)\n\ngcv = math.sqrt(sum_gkv / length)\n\n// VWAP calculation\nvwap = ta.vwma(close, vwapLength)\n\n// Standard deviation for VWAP bands\nvwapStdDev = ta.stdev(close, vwapLength)\n\n// Adaptive multiplier based on GCV\nmultiplier = (gcv / ta.sma(gcv, length)) * vol_multiplier\n\n// Upper and lower bands\nupperBand = vwap + (vwapStdDev * multiplier)\nlowerBand = vwap - (vwapStdDev * multiplier)\n\n// Plotting VWAP and bands\nplot(vwap, title="VWAP", color=color.blue, linewidth=2)\nplot(upperBand, title="Upper Band", color=color.green, linewidth=1)\nplot(lowerBand, title="Lower Band", color=color.red, linewidth=1)\n\nvar barColor = color.black\n\n// Strategy: Enter long above upper band, go to cash below lower band\nif (close > upperBand)\n    barColor := color.green\n    strategy.entry("Long", strategy.long)\nelse if (close < lowerBand)\n    barColor := color.fuchsia\n    strategy.close("Long")\n\nbarcolor(barColor)\n'

class SMF215C8AADC7ECF4F(PinePortBase, IStrategy):
    source_id = "SM_f215c8aadc7ecf4f"
    source_file = '自适应VWAP波段基于Garman-Klass波动率动态跟踪策略-Adaptive-VWAP-Bands-with-Garman-Klass-Volatility-Dynamic-Tracking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length': 25, 'vwapLength': 14, 'vol_multiplier': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
