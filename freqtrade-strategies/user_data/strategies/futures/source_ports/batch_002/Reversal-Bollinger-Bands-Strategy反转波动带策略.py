"""Port of batch_002/Reversal-Bollinger-Bands-Strategy反转波动带策略.md
Extracted source: strategy_migration/sources/SM_240c0861fc944006.pine


Short condition deliberately compares previous close to CURRENT upper band, unlike its previous-open comparison. Preserve the asymmetric offsets and common exit ID."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMReversalBollinger_240c08(PinePortBase, IStrategy):
    source_id = "SM_240c0861fc944006"
    source_file = 'Reversal-Bollinger-Bands-Strategy反转波动带策略.md'
    timeframe = '4h'
    source_defaults = {}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Short condition deliberately compares previous close to CURRENT upper band, unlike its previous-open comparison. Preserve the asymmetric offsets and common exit ID.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        mdl = ta.pine_sma(dataframe.close, 20)
        dev = ta.pine_stdev(dataframe.close, 20)
        upr, lwr = mdl + 2 * dev, mdl - 2 * dev
        dataframe['mdl'], dataframe['dev'], dataframe['upr'], dataframe['lwr'] = mdl, dev, upr, lwr
        dataframe['buy'] = (dataframe.open.shift(1) < lwr.shift(1)) & (dataframe.close.shift(1) < lwr.shift(1))
        dataframe['sell'] = (dataframe.open.shift(1) > upr.shift(1)) & (dataframe.close.shift(1) > upr)
        dataframe['lowest10'] = ta.pine_lowest(dataframe.low, 10)
        dataframe['highest10'] = ta.pine_highest(dataframe.high, 10)
        return dataframe

    def pine_script(self, broker, i, ctx):
        if ctx['buy'][i]:
            broker.entry('bb_buy', 'long')
            broker.exit('TP/SL', 'bb_buy', stop=ctx['lowest10'][i], limit=ctx['highest10'][i])
        if ctx['sell'][i]:
            broker.entry('bb_sell', 'short')
            broker.exit('TP/SL', 'bb_sell', stop=ctx['highest10'][i], limit=ctx['lowest10'][i])
