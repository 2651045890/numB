"""Port of batch_002/RSI指标改进交易策略RSI-Indicator-Improvement-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_6d5d548e861d7816.pine
//  Copyright by HPotter v1.0 22/12/2016

Buy test precedes sell test; default thresholds overlap and priority is preserved. Recursive pos falls back to nz(previous, 0)."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiHistoAlert_6d5d54(PinePortBase, IStrategy):
    source_id = "SM_6d5d548e861d7816"
    source_file = 'RSI指标改进交易策略RSI-Indicator-Improvement-Trading-Strategy.md'
    timeframe = '1d'
    source_defaults = {'RSIPeriod': 13, 'BuyAlertLevel': -10, 'SellAlertLevel': 10, 'RSIHistoModify': 1.5, 'reverse': False}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Buy test precedes sell test; default thresholds overlap and priority is preserved. Recursive pos falls back to nz(previous, 0).', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        x = (ta.pine_rsi(dataframe.close, params['RSIPeriod']) - 50) * params['RSIHistoModify']
        pos = np.zeros(len(dataframe)); previous = 0
        for i, value in enumerate(x):
            previous = 1 if value > params['BuyAlertLevel'] else -1 if value < params['SellAlertLevel'] else previous
            pos[i] = previous
        dataframe['RSIMain'], dataframe['pos'] = x, pos
        dataframe['possig'] = -pos if params['reverse'] else pos
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Long', 'long', when=ctx['possig'][i] == 1)
        broker.entry('Short', 'short', when=ctx['possig'][i] == -1)
