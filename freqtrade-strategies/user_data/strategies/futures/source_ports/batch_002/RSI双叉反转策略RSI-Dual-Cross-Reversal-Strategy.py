"""Port of batch_002/RSI双叉反转策略RSI-Dual-Cross-Reversal-Strategy.md
Extracted source: strategy_migration/sources/SM_57b0c37ac38db4fb.pine
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © email_analysts

Previous RSI comparisons are strict, unlike the inclusive previous-bar comparison used by ta.crossover."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiDualCross_57b0c3(PinePortBase, IStrategy):
    source_id = "SM_57b0c37ac38db4fb"
    source_file = 'RSI双叉反转策略RSI-Dual-Cross-Reversal-Strategy.md'
    timeframe = '1d'
    source_defaults = {'len1': 5, 'len2': 11, 'len3': 6}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Previous RSI comparisons are strict, unlike the inclusive previous-bar comparison used by ta.crossover.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        sh = ta.pine_rsi(dataframe.close, params['len1'])
        ln = ta.pine_rsi(dataframe.close, params['len2'])
        rs = ta.pine_rsi(dataframe.close, params['len3'])
        dataframe['sh'], dataframe['ln'], dataframe['rs'] = sh, ln, rs
        dataframe['buy'] = (sh.shift(1) < ln.shift(1)) & (sh > ln) & (rs.shift(1) < 30)
        dataframe['sell'] = (sh.shift(1) > ln.shift(1)) & (sh < ln) & (rs.shift(1) > 70)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('long', 'long', when=ctx['buy'][i])
        broker.entry('short', 'short', when=ctx['sell'][i])
