"""Port of batch_002/RSI指标结合CCI指标的量化交易策略RSI-amp-CCI-Combination-Quantitative-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_878ed59c7bb98c4e.pine


Source computes MACD and CCI, not RSI despite the Markdown name. Mean absolute deviation uses the current window mean. MACD signal/histogram are plotted but do not filter orders."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMacdCci_878ed5(PinePortBase, IStrategy):
    source_id = "SM_878ed59c7bb98c4e"
    source_file = 'RSI指标结合CCI指标的量化交易策略RSI-amp-CCI-Combination-Quantitative-Trading-Strategy.md'
    timeframe = '1h'
    source_defaults = {'length': 14, 'fastLength': 12, 'slowLength': 26, 'signalLength': 2, 'src': 'close'}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Source computes MACD and CCI, not RSI despite the Markdown name. Mean absolute deviation uses the current window mean. MACD signal/histogram are plotted but do not filter orders.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        s = ta.pine_source(dataframe, params['src'])
        n = int(params['length'])
        ma = ta.pine_sma(s, n)
        dev = s.rolling(n).apply(lambda a: np.mean(np.abs(a - np.mean(a))), raw=True)
        cci = (s - ma) / (0.015 * dev)
        m = ta.pine_macd(dataframe.close, params['fastLength'], params['slowLength'], params['signalLength'])
        dataframe['ma'], dataframe['cci'] = ma, cci
        dataframe['macd'], dataframe['signal'], dataframe['hist'] = m.macd, m.signal, m.hist
        dataframe['longCond'] = ((cci > 100) & (m.macd > 0)) | ((cci > -100) & (m.macd < 0))
        dataframe['shortCond'] = ((cci < -100) & (m.macd < 0)) | ((cci < 100) & (m.macd > 0))
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('long', 'long', when=ctx['longCond'][i])
        broker.entry('short', 'short', when=ctx['shortCond'][i])
