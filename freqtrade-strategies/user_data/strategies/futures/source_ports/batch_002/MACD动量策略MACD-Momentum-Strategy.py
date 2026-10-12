"""Port of batch_002/MACD动量策略MACD-Momentum-Strategy.md
Extracted source: strategy_migration/sources/SM_610d1193e8677ec6.pine


The source passes low/high prices as loss/profit tick distances, not as absolute stop/limit prices. Preserve that arithmetic."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMMacdMomentum_610d11(PinePortBase, IStrategy):
    source_id = "SM_610d1193e8677ec6"
    source_file = 'MACD动量策略MACD-Momentum-Strategy.md'
    timeframe = '1d'
    source_defaults = {}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['The source passes low/high prices as loss/profit tick distances, not as absolute stop/limit prices. Preserve that arithmetic.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    can_short = False

    def pine_indicators(self, dataframe, params):
        m = ta.pine_macd(dataframe.close, 12, 26, 9)
        dataframe['macdLine'], dataframe['signalLine'] = m.macd, m.signal
        dataframe['enterLong'] = ta.pine_crossover(m.macd, m.signal)
        dataframe['exitLong'] = ta.pine_crossunder(m.macd, m.signal)
        dataframe['stopLossLevel'] = ta.pine_lowest(dataframe.low, 1)
        dataframe['takeProfitLevel'] = ta.pine_highest(dataframe.high, 3)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Buy', 'long', when=ctx['enterLong'][i])
        broker.close('Buy', when=ctx['exitLong'][i])
        broker.exit('Take Profit/Stop Loss', 'Buy', loss=ctx['stopLossLevel'][i], profit=ctx['takeProfitLevel'][i])
