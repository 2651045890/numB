"""Port of batch_002/RWI波动率反转策略RWI-Volatility-Contrarian-Strategy.md
Extracted source: strategy_migration/sources/SM_34ec941b9caa61ce.pine
// Copyright (c) 2020-present, JMOZ (1337.ltd)

nz on the length-offset high/low substitutes zero. Direction conditions are continuous states, not crossover events."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRwiContrarian_34ec94(PinePortBase, IStrategy):
    source_id = "SM_34ec941b9caa61ce"
    source_file = 'RWI波动率反转策略RWI-Volatility-Contrarian-Strategy.md'
    timeframe = '1h'
    source_defaults = {'length': 14, 'threshold': 1.0}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['nz on the length-offset high/low substitutes zero. Direction conditions are continuous states, not crossover events.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        n = int(params['length'])
        denominator = ta.pine_atr(dataframe, n) * np.sqrt(n)
        dataframe['rwi_high'] = (dataframe.high - dataframe.low.shift(n).fillna(0)) / denominator
        dataframe['rwi_low'] = (dataframe.high.shift(n).fillna(0) - dataframe.low) / denominator
        dataframe['is_rw'] = (dataframe.rwi_high < params['threshold']) & (dataframe.rwi_low < params['threshold'])
        dataframe['long'] = ~dataframe.is_rw & (dataframe.rwi_high > dataframe.rwi_low)
        dataframe['short'] = ~dataframe.is_rw & (dataframe.rwi_low > dataframe.rwi_high)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Long', 'long', when=ctx['long'][i])
        broker.entry('Short', 'short', when=ctx['short'][i])
