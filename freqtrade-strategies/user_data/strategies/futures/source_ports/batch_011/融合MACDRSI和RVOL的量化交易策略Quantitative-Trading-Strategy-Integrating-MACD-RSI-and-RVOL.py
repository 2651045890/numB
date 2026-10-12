"""batch_011 port of 融合MACDRSI和RVOL的量化交易策略Quantitative-Trading-Strategy-Integrating-MACD-RSI-and-RVOL.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-10 00:00:00\nend: 2024-01-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © BobBarker42069\n\n//@version=4\nstrategy("MACD, RSI, & RVOL Strategy", overlay=true)\n\nlength = input( 14 )\noverSold = input( 30 )\noverBought = input( 70 )\nprice = close\nvrsi = rsi(price, length)\nco = crossover(vrsi, overSold)\ncu = crossunder(vrsi, overBought)\nfastLength = input(12)\nslowlength = input(26)\nMACDLength = input(9)\nMACD = ema(close, fastLength) - ema(close, slowlength)\naMACD = ema(MACD, MACDLength)\ndelta = MACD - aMACD\n\nRVOLlen = input(14, minval=1, title="RVOL Length")\nav = sma(volume, RVOLlen)\nRVOL = volume / av\n\n\n\nif (not na(vrsi)) \n\tif ((co and crossover(delta, 0)) or (co and crossover(RVOL, 2)) or (crossover(delta, 0) and crossover(RVOL, 2)))\n\t\tstrategy.entry("MACD & RSI BUY Long", strategy.long, comment="BUY LONG")\n\n\t\t\n\tif ((cu and crossunder(delta, 0)) or (cu and crossunder(RVOL, 5)) or (crossunder(delta, 0) and crossunder(RVOL, 5)))\n\t\tstrategy.entry("MACD & RSI SELL Short", strategy.short, comment="SELL LONG")\n\t\n\t\t\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)'

class SM21F7F9270086E4D8(PinePortBase, IStrategy):
    source_id = "SM_21f7f9270086e4d8"
    source_file = '融合MACDRSI和RVOL的量化交易策略Quantitative-Trading-Strategy-Integrating-MACD-RSI-and-RVOL.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'overSold': 30, 'overBought': 70, 'fastLength': 12, 'slowlength': 26, 'MACDLength': 9, 'RVOLlen': 14}
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
