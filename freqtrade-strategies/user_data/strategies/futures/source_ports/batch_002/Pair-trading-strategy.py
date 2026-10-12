"""Port of batch_002/Pair-trading-strategy.md
Extracted source: strategy_migration/sources/SM_1eb9f4f7d0808992.pine
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © femisapien

Despite its name this source uses one close series, not a pair spread. cross is bidirectional. The source close_all(true) positional argument is projected as an unconditional close call within the exit block. Exchange timezone is UTC for the declared Binance market."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMPairTrading_1eb9f4(PinePortBase, IStrategy):
    source_id = "SM_1eb9f4f7d0808992"
    source_file = 'Pair-trading-strategy.md'
    timeframe = '1d'
    source_defaults = {'smalength': 20, 'entryzscore': 2.0, 'startYear': 2016}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Despite its name this source uses one close series, not a pair spread. cross is bidirectional. The source close_all(true) positional argument is projected as an unconditional close call within the exit block. Exchange timezone is UTC for the declared Binance market.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        c = dataframe.close
        ma = ta.pine_sma(c, params['smalength'])
        dev = params['entryzscore'] * ta.pine_stdev(c, params['smalength'])
        dataframe['ma'], dataframe['dev'] = ma, dev
        dataframe['upper'], dataframe['lower'] = ma + dev, ma - dev
        dataframe['longEntrySignal'] = ta.pine_cross(c, ma - dev)
        dataframe['shortEntrySignal'] = ta.pine_cross(c, ma + dev)
        dataframe['exitSignal'] = ta.pine_cross(c, ma)
        dates = pd.to_datetime(dataframe['date'] if 'date' in dataframe else dataframe.index, utc=True)
        dataframe['afterStartDate'] = np.asarray(dates >= pd.Timestamp(year=int(params['startYear']), month=1, day=1, tz='UTC'))
        return dataframe

    def pine_script(self, broker, i, ctx):
        if ctx['afterStartDate'][i]:
            broker.entry('le', 'long', when=ctx['longEntrySignal'][i])
            broker.entry('se', 'short', when=ctx['shortEntrySignal'][i])
            broker.close_all(when=ctx['exitSignal'][i])
