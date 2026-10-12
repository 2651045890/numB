"""Port of batch_002/MACD双均线交叉策略-MACD-Dual-Moving-Average-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_e3db1c0f1fa1ed55.pine


Both sides use the same upward takeProfit formula based on the previous low. Exit orders are submitted only on crossover bars, and share the TP/SL ID."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMacdDualCross_e3db1c(PinePortBase, IStrategy):
    source_id = "SM_e3db1c0f1fa1ed55"
    source_file = 'MACD双均线交叉策略-MACD-Dual-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    source_defaults = {}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Both sides use the same upward takeProfit formula based on the previous low. Exit orders are submitted only on crossover bars, and share the TP/SL ID.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        m = ta.pine_macd(dataframe.close, 12, 26, 9)
        dataframe['macdLine'], dataframe['signalLine'] = m.macd, m.signal
        dataframe['longCondition'] = ta.pine_crossover(m.macd, m.signal)
        dataframe['shortCondition'] = ta.pine_crossunder(m.macd, m.signal)
        dataframe['longStopLoss'] = dataframe.low.shift(1)
        dataframe['shortStopLoss'] = dataframe.high.shift(1)
        dataframe['takeProfit'] = dataframe.close + (dataframe.close - dataframe.longStopLoss) * 4
        return dataframe

    def pine_script(self, broker, i, ctx):
        if ctx['longCondition'][i]:
            broker.entry('Buy', 'long')
            broker.exit('TP/SL', 'Buy', stop=ctx['longStopLoss'][i], limit=ctx['takeProfit'][i])
        if ctx['shortCondition'][i]:
            broker.entry('Sell', 'short')
            broker.exit('TP/SL', 'Sell', stop=ctx['shortStopLoss'][i], limit=ctx['takeProfit'][i])
