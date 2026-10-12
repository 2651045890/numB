"""Port of batch_002/MACD-量能反转交易策略MACD-Volume-Reversal-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_f56745d2024b0fb9.pine


Bullish-named condition enters short, bearish-named condition enters long. Profit orders are updated every bar from average position price."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMacdVolumeReversal_f56745(PinePortBase, IStrategy):
    source_id = "SM_f56745d2024b0fb9"
    source_file = 'MACD-量能反转交易策略MACD-Volume-Reversal-Trading-Strategy.md'
    timeframe = '1h'
    source_defaults = {'fastLength': 3, 'slowLength': 10, 'signalSmoothing': 16, 'takeProfitPct': 10.0, 'volumeMultiplier': 1.0}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Bullish-named condition enters short, bearish-named condition enters long. Profit orders are updated every bar from average position price.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        m = ta.pine_macd(dataframe.close, params['fastLength'], params['slowLength'], params['signalSmoothing'])
        dataframe['macd'], dataframe['signal'] = m.macd, m.signal
        v = dataframe.volume > dataframe.volume.shift(1) * params['volumeMultiplier']
        dataframe['bullishAntiPattern'] = ta.pine_crossunder(m.macd, m.signal) & v
        dataframe['bearishAntiPattern'] = ta.pine_crossover(m.macd, m.signal) & v
        dataframe['takeProfitPct'] = params['takeProfitPct'] / 100
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Short', 'short', when=ctx['bullishAntiPattern'][i])
        broker.entry('Long', 'long', when=ctx['bearishAntiPattern'][i])
        broker.exit('Take Profit Long', 'Long', limit=broker.position_avg_price * (1 + ctx['takeProfitPct'][i]))
        broker.exit('Take Profit Short', 'Short', limit=broker.position_avg_price * (1 - ctx['takeProfitPct'][i]))
