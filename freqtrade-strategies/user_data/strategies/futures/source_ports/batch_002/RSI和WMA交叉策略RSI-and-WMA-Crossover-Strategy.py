"""Port of batch_002/RSI和WMA交叉策略RSI-and-WMA-Crossover-Strategy.md
Extracted source: strategy_migration/sources/SM_e194148f68fb8aa3.pine


WMA smooths RSI, not price. The 70/30 levels are visual only; BUY/SELL comment text does not affect orders."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiWmaCross_e19414(PinePortBase, IStrategy):
    source_id = "SM_e194148f68fb8aa3"
    source_file = 'RSI和WMA交叉策略RSI-and-WMA-Crossover-Strategy.md'
    timeframe = '1h'
    source_defaults = {'rsiLength': 14, 'wmaLength': 45}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['WMA smooths RSI, not price. The 70/30 levels are visual only; BUY/SELL comment text does not affect orders.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        r = ta.pine_rsi(dataframe.close, params['rsiLength'])
        w = ta.pine_wma(r, params['wmaLength'])
        dataframe['rsiValue'], dataframe['wmaValue'] = r, w
        dataframe['overboughtLevel'], dataframe['oversoldLevel'] = 70, 30
        dataframe['longCondition'] = ta.pine_crossover(r, w)
        dataframe['shortCondition'] = ta.pine_crossunder(r, w)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Long', 'long', when=ctx['longCondition'][i])
        broker.entry('Short', 'short', when=ctx['shortCondition'][i])
