"""Port of batch_002/PVT-EMA趋势交叉量价策略-PVT-EMA-Trend-Crossover-Volume-Price-Strategy.md
Extracted source: strategy_migration/sources/SM_3fe2372921de827f.pine
// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © PakunFX

Historical close-bar implementation only: source calc_on_every_tick=true cannot be reproduced from OHLCV ticks. Zero cumulative volume raises the original runtime error."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMPvtEmaCross_3fe237(PinePortBase, IStrategy):
    source_id = "SM_3fe2372921de827f"
    source_file = 'PVT-EMA趋势交叉量价策略-PVT-EMA-Trend-Crossover-Volume-Price-Strategy.md'
    timeframe = '1d'
    source_defaults = {'emaLength': 20}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Historical close-bar implementation only: source calc_on_every_tick=true cannot be reproduced from OHLCV ticks. Zero cumulative volume raises the original runtime error.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    source_implementation_status = 'historical_only'

    def pine_indicators(self, dataframe, params):
        dataframe['cumVol'] = dataframe.volume.fillna(0).cumsum()
        if len(dataframe) and dataframe.cumVol.iloc[-1] == 0:
            raise ValueError('No volume is provided by the data vendor.')
        pvt = ta.pine_cum(dataframe.close.diff() / dataframe.close.shift(1) * dataframe.volume)
        e = ta.pine_ema(pvt, params['emaLength'])
        dataframe['pvt'], dataframe['emaPVT'] = pvt, e
        dataframe['longCondition'] = ta.pine_crossover(pvt, e)
        dataframe['shortCondition'] = ta.pine_crossunder(pvt, e)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['longCondition'][i])
        broker.entry('Sell', 'short', when=ctx['shortCondition'][i])
