"""Port of batch_002/The-Genesis-Crossover-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_14d2f291e6d688e3.pine
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © genesisjgonzalezh

The long entry ID is lowercase long, but its exit references uppercase Long. Preserve the mismatch and the shared Exit ID. profit=10 and loss=2 are ticks, handled by broker.exit."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMGenesisCrossover_14d2f2(PinePortBase, IStrategy):
    source_id = "SM_14d2f291e6d688e3"
    source_file = 'The-Genesis-Crossover-Trading-Strategy.md'
    timeframe = '1d'
    source_defaults = {}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['The long entry ID is lowercase long, but its exit references uppercase Long. Preserve the mismatch and the shared Exit ID. profit=10 and loss=2 are ticks, handled by broker.exit.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        dataframe['ema1'] = ta.pine_ema(dataframe.close, 20)
        dataframe['ema2'] = ta.pine_ema(dataframe.close, 50)
        dataframe['long'] = ta.pine_crossover(dataframe.ema1, dataframe.ema2)
        dataframe['short'] = ta.pine_crossover(dataframe.ema2, dataframe.ema1)
        dataframe['LongSignal'] = dataframe['long']
        dataframe['ShortSignal'] = ta.pine_crossunder(dataframe.ema1, dataframe.ema2)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('long', 'long', when=ctx['long'][i])
        broker.exit('Exit', 'Long', profit=10, loss=2)
        broker.entry('short', 'short', when=ctx['short'][i])
        broker.exit('Exit', 'short', profit=10, loss=2)
