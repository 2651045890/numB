"""Port of batch_002/RSI鳄鱼交易策略Alligator-RSI-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_118dc166cdef9949.pine


Only Long has a stop/profit exit; Short exits through reversal. The two conditions per direction issue separate calls using the same order ID."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMAlligatorRsi_118dc1(PinePortBase, IStrategy):
    source_id = "SM_118dc166cdef9949"
    source_file = 'RSI鳄鱼交易策略Alligator-RSI-Trading-Strategy.md'
    timeframe = '1d'
    source_defaults = {'sl_inp': 10, 'tp_inp': 90}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Only Long has a stop/profit exit; Short exits through reversal. The two conditions per direction issue separate calls using the same order ID.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        j, t, l = ta.pine_rsi(dataframe.close, 34), ta.pine_rsi(dataframe.close, 5), ta.pine_rsi(dataframe.close, 13)
        dataframe['jaws'], dataframe['teeth'], dataframe['lips'] = j, t, l
        dataframe['longCondition'] = ta.pine_crossover(l, j) & (t > j)
        dataframe['longCondition1'] = ta.pine_crossover(t, j) & (l > j)
        dataframe['shortCondition'] = ta.pine_crossunder(l, j) & (t < j)
        dataframe['shortCondition1'] = ta.pine_crossunder(t, j) & (l < j)
        dataframe['sl_inp'], dataframe['tp_inp'] = params['sl_inp'] / 100, params['tp_inp'] / 100
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Long', 'long', when=ctx['longCondition'][i])
        broker.entry('Long', 'long', when=ctx['longCondition1'][i])
        broker.entry('Short', 'short', when=ctx['shortCondition'][i])
        broker.entry('Short', 'short', when=ctx['shortCondition1'][i])
        broker.exit('Stop Loss/Profit', 'Long', stop=broker.position_avg_price * (1 - ctx['sl_inp'][i]), limit=broker.position_avg_price * (1 + ctx['tp_inp'][i]))
