"""Port of batch_002/MOST与双均线交叉策略-MOST-and-Dual-Moving-Average-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_6551fb9cf788df3c.pine


MOST is only plotted in the source and is not a trade filter."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMostMaCross_6551fb(PinePortBase, IStrategy):
    source_id = "SM_6551fb9cf788df3c"
    source_file = 'MOST与双均线交叉策略-MOST-and-Dual-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    source_defaults = {'fastMALength': 14, 'slowMALength': 21, 'mostLength': 9}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['MOST is only plotted in the source and is not a trade filter.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0

    def pine_indicators(self, dataframe, params):
        a = ta.pine_sma(dataframe.close, params['fastMALength'])
        b = ta.pine_sma(dataframe.close, params['slowMALength'])
        dataframe['fastMA'], dataframe['slowMA'] = a, b
        dataframe['most'] = ta.pine_highest(dataframe.close, params['mostLength'])
        dataframe['buySignal'] = ta.pine_crossover(a, b)
        dataframe['sellSignal'] = ta.pine_crossunder(a, b)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Alım', 'long', when=ctx['buySignal'][i])
        broker.entry('Satım', 'short', when=ctx['sellSignal'][i])
