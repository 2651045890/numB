"""Port of batch_002/MACD与EMA结合的SMC策略SMC-Strategy-Combining-MACD-and-EMA.md
Extracted source: strategy_migration/sources/SM_a2b325b0aee63e92.pine


Lux Algo signals in this source are two boolean inputs, both true by default; no external SMC indicator is computed."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMSmcMacdEma_a2b325(PinePortBase, IStrategy):
    source_id = "SM_a2b325b0aee63e92"
    source_file = 'MACD与EMA结合的SMC策略SMC-Strategy-Combining-MACD-and-EMA.md'
    timeframe = '1d'
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalLength': 9, 'emaLength': 200, 'buySignal': True, 'sellSignal': True}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Lux Algo signals in this source are two boolean inputs, both true by default; no external SMC indicator is computed.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        m = ta.pine_macd(dataframe.close, params['fastLength'], params['slowLength'], params['signalLength'])
        dataframe['macdLine'], dataframe['signalLine'], dataframe['hist'] = m.macd, m.signal, m.hist
        dataframe['emaValue'] = ta.pine_ema(dataframe.close, params['emaLength'])
        dataframe['buy'] = bool(params['buySignal']) & (m.macd > m.signal) & (dataframe.close > dataframe.emaValue)
        dataframe['sell'] = bool(params['sellSignal']) & (m.macd < m.signal) & (dataframe.close < dataframe.emaValue)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['buy'][i])
        broker.entry('Sell', 'short', when=ctx['sell'][i])
