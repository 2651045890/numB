"""batch_011 port of 趋势追踪突破策略Gold-Silver-30m-Trend-Following-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-09 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("My Strategy", overlay = false, commission_value = 0.01, pyramiding = 1)\n// Custom RSI\nRSIlength = input( 14, minval=1 , title="lookback length of RSI")\nRSIOverBought = input(65, title="OB")\nRSIOverSold = input(35, title="OS")\nRSIprice = close\nvrsi = rsi(RSIprice, RSIlength)\nplot(vrsi)\n\n//Bollinger Bands\nBBlength = input(40, minval=1,title="Bollinger Period Length")\nBBmult = 2 // input(2.0, minval=0.001, maxval=50,title="Bollinger Bands Standard Deviation")\nBBbasis = sma(close, BBlength)\nBBdev = BBmult * stdev(close, BBlength)\nBBupper = BBbasis + BBdev\nBBlower = BBbasis - BBdev\nsource = close\n//RSI Levels\nx=hline(RSIOverSold)\nz=hline(RSIOverBought)\n\n\nstrategy.entry("Buy", strategy.long, 1, when = close > ema(close, 162) and vrsi < RSIOverSold)\nstrategy.exit("Buy", when = vrsi > RSIOverBought and close < ema(close, 162))\n\nstrategy.entry("Sell", strategy.short, 1, when = close < ema(close, 162) and vrsi > RSIOverSold)\nstrategy.exit("Sell", when = vrsi > RSIOverBought and close > ema(close, 162))\n\n\n\n  '

class SM93A5AFA8825F55F1(PinePortBase, IStrategy):
    source_id = "SM_93a5afa8825f55f1"
    source_file = '趋势追踪突破策略Gold-Silver-30m-Trend-Following-Breakout-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'RSIlength': 14, 'RSIOverBought': 65, 'RSIOverSold': 35, 'BBlength': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0.01
    source_pyramiding = 1
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
