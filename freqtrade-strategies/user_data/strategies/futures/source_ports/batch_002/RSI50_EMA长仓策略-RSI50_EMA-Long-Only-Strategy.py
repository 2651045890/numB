"""Port of batch_002/RSI50_EMA长仓策略-RSI50_EMA-Long-Only-Strategy.md
Extracted source: strategy_migration/sources/SM_97d16dd4e91cc9e0.pine


RSICLose does not match either entry ID and is preserved. RSI entry and RSI close also require bull_cross; RSI crossing alone does not submit an order."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsi50EmaLong_97d16d(PinePortBase, IStrategy):
    source_id = "SM_97d16dd4e91cc9e0"
    source_file = 'RSI50_EMA长仓策略-RSI50_EMA-Long-Only-Strategy.md'
    timeframe = '1d'
    source_defaults = {'len': 11, 'mul': 2, 'rsicap': 50}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['RSICLose does not match either entry ID and is preserved. RSI entry and RSI close also require bull_cross; RSI crossing alone does not submit an order.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    can_short = False
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0

    def pine_indicators(self, dataframe, params):
        rsi = ta.pine_rsi(dataframe.close, 20)
        price = ta.pine_sma(dataframe.close, 2)
        average = ta.pine_ema(dataframe.close, params['len'])
        diff = ta.pine_atr(dataframe, params['len']) * params['mul']
        dataframe['rsi_1'], dataframe['price'], dataframe['average'], dataframe['diff'] = rsi, price, average, diff
        dataframe['bull_level'], dataframe['bear_level'] = average + diff, average - diff
        dataframe['bull_cross'] = ta.pine_crossover(price, average + diff)
        dataframe['bear_cross'] = ta.pine_crossover(average - diff, price)
        dataframe['RENTRY'] = ta.pine_crossover(rsi, params['rsicap'])
        dataframe['EXIT'] = ta.pine_crossunder(rsi, 50)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['bull_cross'][i])
        broker.close('Buy', when=ctx['bear_cross'][i])
        if ctx['RENTRY'][i]:
            broker.entry('RSI', 'long', when=ctx['bull_cross'][i])
        if ctx['EXIT'][i]:
            broker.close('RSICLose', when=ctx['bull_cross'][i])
