"""Port of batch_002/RSI和MACD结合支撑阻力的量化交易策略Quantitative-Trading-Strategy-Combining-RSI-MACD-and-Support-Resistance.md
Extracted source: strategy_migration/sources/SM_f9d4d34f5cad8a3c.pine


Support/resistance include the current candle. Source only enters/reverses; it declares no explicit exit or stop."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMRsiMacdSupport_f9d4d3(PinePortBase, IStrategy):
    source_id = "SM_f9d4d34f5cad8a3c"
    source_file = 'RSI和MACD结合支撑阻力的量化交易策略Quantitative-Trading-Strategy-Combining-RSI-MACD-and-Support-Resistance.md'
    timeframe = '1m'
    source_defaults = {'rsiOverbought': 70, 'rsiOversold': 30, 'macdFastLength': 12, 'macdSlowLength': 26, 'macdSignalSmoothing': 9}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['Support/resistance include the current candle. Source only enters/reverses; it declares no explicit exit or stop.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']

    def pine_indicators(self, dataframe, params):
        r = ta.pine_rsi(dataframe.close, 14)
        m = ta.pine_macd(dataframe.close, params['macdFastLength'], params['macdSlowLength'], params['macdSignalSmoothing'])
        s, res = ta.pine_lowest(dataframe.low, 100), ta.pine_highest(dataframe.high, 100)
        dataframe['rsiValue'], dataframe['macdLine'], dataframe['signalLine'] = r, m.macd, m.signal
        dataframe['support'], dataframe['resistance'] = s, res
        dataframe['longCondition'] = ta.pine_crossover(m.macd, m.signal) & (r < params['rsiOversold']) & ((dataframe.close - s) < dataframe.close * 0.01)
        dataframe['shortCondition'] = ta.pine_crossunder(m.macd, m.signal) & (r > params['rsiOverbought']) & ((res - dataframe.close) < dataframe.close * 0.01)
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.entry('Long', 'long', when=ctx['longCondition'][i])
        broker.entry('Short', 'short', when=ctx['shortCondition'][i])
