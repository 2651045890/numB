# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/Crypto-Data-API/hyperliquid-backtester
# Original commit: a9dd95dafe0ce3cfae087449a51c683eda725bee
# Original files: strategies/examples/sma_cross.py, src/hlbt/indicators.py, src/hlbt/backtester.py
# Original market: Hyperliquid perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
import numpy as np
from pandas import DataFrame, Series
from freqtrade.strategy import IStrategy

def _seeded_ema(s: Series, period: int) -> Series:
    v = s.to_numpy(dtype=float); out = np.full(v.shape, np.nan)
    if len(v) >= period:
        a = 2.0 / (period + 1.0); out[period - 1] = v[:period].mean()
        for i in range(period, len(v)): out[i] = v[i] * a + out[i - 1] * (1.0 - a)
    return Series(out, index=s.index)

class HyperliquidSmaCrossStrategy(IStrategy):
    INTERFACE_VERSION = 3
    can_short = True
    timeframe = "15m"
    startup_candle_count = 60
    minimal_roi = {"0": 100.0}
    stoploss = -0.05
    use_exit_signal = True
    fast_length, slow_length = 12, 48

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["fast"] = _seeded_ema(dataframe["close"], self.fast_length)
        dataframe["slow"] = _seeded_ema(dataframe["close"], self.slow_length)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[(dataframe.fast.shift(1) <= dataframe.slow.shift(1)) & (dataframe.fast > dataframe.slow), "enter_long"] = 1
        dataframe.loc[(dataframe.fast.shift(1) >= dataframe.slow.shift(1)) & (dataframe.fast < dataframe.slow), "enter_short"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe.fast < dataframe.slow, "exit_long"] = 1
        dataframe.loc[dataframe.fast > dataframe.slow, "exit_short"] = 1
        return dataframe

    def custom_exit(self, pair, trade, current_time, current_rate, current_profit, **kwargs):
        if current_profit >= 0.15: return "take_profit"
        return None

