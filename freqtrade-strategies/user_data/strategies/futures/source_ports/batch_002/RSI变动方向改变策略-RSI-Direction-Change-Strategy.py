"""Port of batch_002/RSI变动方向改变策略-RSI-Direction-Change-Strategy.md
Extracted source: strategy_migration/sources/SM_be4d2e6b3e5044a7.pine


Exit tests the absolute RSI change, not a change of direction. Both entry calls precede both close calls, including bars on which entry and exit coexist."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiDirectionChange_be4d2e(PinePortBase, IStrategy):
    source_id = "SM_be4d2e6b3e5044a7"
    source_file = 'RSI变动方向改变策略-RSI-Direction-Change-Strategy.md'
    timeframe = '1d'
    source_defaults = {'rsiLength': 14, 'rsiChangeThreshold': 10, 'rsiExitThreshold': 5, 'priceReverseThreshold': 1}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Exit tests the absolute RSI change, not a change of direction. Both entry calls precede both close calls, including bars on which entry and exit coexist.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        rsi = ta.pine_rsi(dataframe.close, params['rsiLength'])
        change = rsi.diff()
        dataframe['rsi'], dataframe['rsiChange'] = rsi, change
        dataframe['buyCondition'] = change >= params['rsiChangeThreshold']
        dataframe['sellCondition'] = (change <= -params['rsiChangeThreshold']) | (dataframe.close.pct_change(fill_method=None) * 100 <= -params['priceReverseThreshold'])
        dataframe['exitCondition'] = change.abs() >= params['rsiExitThreshold']
        return dataframe

    def pine_script(self, broker, i, ctx):
        buy, sell, leave = ctx['buyCondition'][i], ctx['sellCondition'][i], ctx['exitCondition'][i]
        broker.entry('Buy', 'long', when=buy)
        broker.entry('Sell', 'short', when=sell)
        broker.close('Buy', when=leave or sell)
        broker.close('Sell', when=leave or buy)
