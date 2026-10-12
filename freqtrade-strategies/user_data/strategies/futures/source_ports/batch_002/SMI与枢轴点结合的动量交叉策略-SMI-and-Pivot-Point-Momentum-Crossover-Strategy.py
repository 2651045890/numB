"""Port of batch_002/SMI与枢轴点结合的动量交叉策略-SMI-and-Pivot-Point-Momentum-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_9fa131663a43c1ab.pine


Highest/lowest use smiSource (close by default), not high/low. No pivot-point calculation exists in the source."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMSmiCross_9fa131(PinePortBase, IStrategy):
    source_id = "SM_9fa131663a43c1ab"
    source_file = 'SMI与枢轴点结合的动量交叉策略-SMI-and-Pivot-Point-Momentum-Crossover-Strategy.md'
    timeframe = '1h'
    source_defaults = {'smiLength': 8, 'smiK': 6, 'smiD': 6, 'smiSource': 'close'}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Highest/lowest use smiSource (close by default), not high/low. No pivot-point calculation exists in the source.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        s = ta.pine_source(dataframe, params['smiSource'])
        h, l = ta.pine_highest(s, params['smiLength']), ta.pine_lowest(s, params['smiLength'])
        m = (h + l) / 2
        d = (s - m) / (h - l) * 100
        smi = ta.pine_sma(d, params['smiK'])
        signal = ta.pine_sma(smi, params['smiD'])
        for key, value in dict(h=h, l=l, m=m, d=d, smi=smi, smiSignal=signal).items():
            dataframe[key] = value
        dataframe['bullishCondition'] = ta.pine_crossover(smi, signal)
        dataframe['bearishCondition'] = ta.pine_crossunder(smi, signal)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['bullishCondition'][i])
        broker.entry('Sell', 'short', when=ctx['bearishCondition'][i])
