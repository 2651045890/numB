"""Port of batch_002/MACD和EMA金叉死叉策略MACD-and-EMA-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_010c60466cf61cb6.pine


Both entry guards use position_size <= 0, including the short guard. This prevents opening short while long; it is not changed to >= 0."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMacdEmaCross_010c60(PinePortBase, IStrategy):
    source_id = "SM_010c60466cf61cb6"
    source_file = 'MACD和EMA金叉死叉策略MACD-and-EMA-Crossover-Strategy.md'
    timeframe = '1d'
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Both entry guards use position_size <= 0, including the short guard. This prevents opening short while long; it is not changed to >= 0.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        m = ta.pine_macd(dataframe.close, params['fastLength'], params['slowLength'], params['signalLength'])
        e = ta.pine_ema(dataframe.close, 200)
        dataframe['macdLine'], dataframe['signalLine'], dataframe['ema200'] = m.macd, m.signal, e
        dataframe['longCondition'] = ta.pine_crossover(m.macd, m.signal) & (m.macd < 0) & (dataframe.close > e)
        dataframe['shortCondition'] = ta.pine_crossunder(m.macd, m.signal) & (m.macd > 0) & (dataframe.close < e)
        dataframe['longTakeProfit'] = dataframe.close + 2 * (dataframe.close - e)
        dataframe['shortTakeProfit'] = dataframe.close - 2 * (e - dataframe.close)
        return dataframe

    def pine_script(self, broker, i, ctx):
        if ctx['longCondition'][i] and broker.position_size <= 0:
            broker.entry('Long', 'long')
            broker.exit('Exit Long', 'Long', stop=ctx['ema200'][i], limit=ctx['longTakeProfit'][i])
        if ctx['shortCondition'][i] and broker.position_size <= 0:
            broker.entry('Short', 'short')
            broker.exit('Exit Short', 'Short', stop=ctx['ema200'][i], limit=ctx['shortTakeProfit'][i])
