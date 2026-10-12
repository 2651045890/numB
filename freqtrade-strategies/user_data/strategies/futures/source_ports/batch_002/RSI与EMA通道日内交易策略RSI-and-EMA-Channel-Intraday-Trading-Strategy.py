"""Port of batch_002/RSI与EMA通道日内交易策略RSI-and-EMA-Channel-Intraday-Trading-Strategy.md
Extracted source: strategy_migration/sources/SM_0f99a2eea66b5462.pine
// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/
// © moondevonyt

PARTIAL: both exits omit qty, and Pine exit reservation/OCA semantics are not fully represented by the shared engine. Preserve both calls and their order rather than inventing a 50/50 split."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiEmaChannel_0f99a2(PinePortBase, IStrategy):
    source_id = "SM_0f99a2eea66b5462"
    source_file = 'RSI与EMA通道日内交易策略RSI-and-EMA-Channel-Intraday-Trading-Strategy.md'
    timeframe = '1h'
    source_defaults = {}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['PARTIAL: both exits omit qty, and Pine exit reservation/OCA semantics are not fully represented by the shared engine. Preserve both calls and their order rather than inventing a 50/50 split.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    source_implementation_status = 'partial_exit_reservation'

    def pine_indicators(self, dataframe, params):
        eh, el = ta.pine_ema(dataframe.high, 5), ta.pine_ema(dataframe.low, 5)
        r = ta.pine_rsi(dataframe.close, 6)
        dataframe['ema_high'], dataframe['ema_low'], dataframe['rsi'] = eh, el, r
        dataframe['buy_condition'] = (dataframe.close > eh) & ta.pine_crossover(r, 70)
        dataframe['sell_condition'] = (dataframe.close < el) & ta.pine_crossunder(r, 30)
        dataframe['buy_tp1'] = dataframe.close + (dataframe.close - dataframe.low.shift(1))
        dataframe['buy_tp2'] = dataframe.close + 2 * (dataframe.close - dataframe.low.shift(1))
        dataframe['sell_tp1'] = dataframe.close - (dataframe.high.shift(1) - dataframe.close)
        dataframe['sell_tp2'] = dataframe.close - 2 * (dataframe.high.shift(1) - dataframe.close)
        return dataframe

    def pine_script(self, broker, i, ctx):
        if ctx['buy_condition'][i]:
            broker.entry('Buy', 'long')
            broker.exit('Take Profit 1', 'Buy', limit=ctx['buy_tp1'][i])
            broker.exit('Take Profit 2', 'Buy', limit=ctx['buy_tp2'][i])
        if ctx['sell_condition'][i]:
            broker.entry('Sell', 'short')
            broker.exit('Take Profit 1', 'Sell', limit=ctx['sell_tp1'][i])
            broker.exit('Take Profit 2', 'Sell', limit=ctx['sell_tp2'][i])
