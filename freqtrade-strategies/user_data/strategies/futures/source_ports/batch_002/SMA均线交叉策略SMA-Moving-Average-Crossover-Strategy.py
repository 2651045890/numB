"""Port of batch_002/SMA均线交叉策略SMA-Moving-Average-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_57c4c6f55c756f34.pine
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © j0secyn

window() returns true unconditionally: date inputs are retained but do not restrict trading. Source margin_long and margin_short are 100; engine margin modelling remains a shared boundary."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMSmaMaCross_57c4c6(PinePortBase, IStrategy):
    source_id = "SM_57c4c6f55c756f34"
    source_file = 'SMA均线交叉策略SMA-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    source_defaults = {'fromDay': 1, 'fromMonth': 1, 'fromYear': 2018, 'thruDay': 30, 'thruMonth': 9, 'thruYear': 2024, 'slow_ma_length': 100, 'fast_ma_length': 30}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['window() returns true unconditionally: date inputs are retained but do not restrict trading. Source margin_long and margin_short are 100; engine margin modelling remains a shared boundary.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    source_initial_capital = 10000.0
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    can_short = False

    def pine_indicators(self, dataframe, params):
        dataframe['start'] = pd.Timestamp(year=int(params['fromYear']), month=int(params['fromMonth']), day=int(params['fromDay']), tz='UTC').value // 1_000_000
        dataframe['finish'] = pd.Timestamp(year=int(params['thruYear']), month=int(params['thruMonth']), day=int(params['thruDay']), hour=23, minute=59, tz='UTC').value // 1_000_000
        fast = ta.pine_sma(dataframe.close, params['fast_ma_length'])
        slow = ta.pine_sma(dataframe.close, params['slow_ma_length'])
        dataframe['crossOv'] = ta.pine_crossover(fast, slow)
        dataframe['crossUn'] = ta.pine_crossunder(fast, slow)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('L', 'long', when=ctx['crossOv'][i])
        broker.close('L', when=ctx['crossUn'][i])
