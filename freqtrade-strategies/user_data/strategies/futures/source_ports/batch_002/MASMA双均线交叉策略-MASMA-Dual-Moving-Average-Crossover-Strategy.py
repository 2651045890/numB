"""Port of batch_002/MASMA双均线交叉策略-MASMA-Dual-Moving-Average-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_7d8c94a821dcd0b2.pine


The source declares Binance spot data but requests both long and short; this target is an offline futures port. Chart labels are omitted."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMasmaCross_7d8c94(PinePortBase, IStrategy):
    source_id = "SM_7d8c94a821dcd0b2"
    source_file = 'MASMA双均线交叉策略-MASMA-Dual-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    source_defaults = {'short_length': 20, 'long_length': 50}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['The source declares Binance spot data but requests both long and short; this target is an offline futures port. Chart labels are omitted.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        a = ta.pine_sma(dataframe.close, params['short_length'])
        b = ta.pine_sma(dataframe.close, params['long_length'])
        dataframe['ma_short'], dataframe['ma_long'] = a, b
        dataframe['buy_condition'] = ta.pine_crossover(a, b)
        dataframe['sell_condition'] = ta.pine_crossunder(a, b)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['buy_condition'][i])
        broker.entry('Sell', 'short', when=ctx['sell_condition'][i])
