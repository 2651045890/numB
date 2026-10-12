"""batch_011 port of 突破均线的趋势追踪策略Breakthrough-Moving-Average-Trend-Tracking-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-27 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Buy Dip MA & PSAR", overlay=true)\n\nPSAR_start = input(0.02)\nPSAR_increment = input(0.02)\nPSAR_maximum = input(0.2)\n\nEMA_fast = input(20)\nEMA_slow = input(40)\nSMA_fast = input(100)\nSMA_slow = input(200)\n\nemafast = ema(close, EMA_fast)\nemaslow = ema(close, EMA_slow)\nsmafast = sma(close, SMA_fast)\nsmaslow = sma(close, SMA_slow)\n\npsar = sar(PSAR_start, PSAR_increment, PSAR_maximum)\nuptrend = emafast > emaslow and smafast > smaslow\nbreakdown = not uptrend\n\nif (psar >= high and uptrend)\n    strategy.entry("Buy", strategy.long, stop=psar, comment="Buy")\nelse\n    strategy.cancel("Buy")\n\nif (psar <= low)\n    strategy.exit("Close", "Buy", stop=psar, comment="Close")\nelse\n    strategy.cancel("Close")\n\nif (breakdown)\n    strategy.close("Buy")\n\n\nplot(emafast, color=blue)\nplot(emaslow, color=red)'

class SM8B525B7D42B1A53E(PinePortBase, IStrategy):
    source_id = "SM_8b525b7d42b1a53e"
    source_file = '突破均线的趋势追踪策略Breakthrough-Moving-Average-Trend-Tracking-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'PSAR_start': 0.02, 'PSAR_increment': 0.02, 'PSAR_maximum': 0.2, 'EMA_fast': 20, 'EMA_slow': 40, 'SMA_fast': 100, 'SMA_slow': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
