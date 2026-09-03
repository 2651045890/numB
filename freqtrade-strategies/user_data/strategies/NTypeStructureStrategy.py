from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy


@dataclass
class _State:
    state: str = "IDLE"
    direction: str | None = None
    h1: float | None = None
    h1_idx: int | None = None
    l1: float | None = None
    l1_idx: int | None = None
    cross_idx: int | None = None

    def reset(self) -> None:
        self.state = "IDLE"
        self.direction = None
        self.h1 = None
        self.h1_idx = None
        self.l1 = None
        self.l1_idx = None
        self.cross_idx = None


class NTypeStructureStrategy(IStrategy):
    """
    严格对齐 n_type_bot 的 Freqtrade 迁移版。

    说明：
    - 保留 EMA 穿越后的状态机推进
    - 保留 H1/L1 / L1/H1 结构确认
    - 保留波动率过滤
    - 保留顺势方向限制
    - 交易出场仍由 Freqtrade 的 exit/stoploss/trailing 体系接管
    """

    INTERFACE_VERSION = 3
    timeframe = "15m"
    can_short = True
    process_only_new_candles = True
    startup_candle_count = 250
    minimal_roi = {"0": 0.03}
    stoploss = -0.08
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False
    trailing_stop = True
    trailing_stop_positive = 0.012
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    ema_period = 40
    atr_period = 14

    vol_filter_enabled = True
    vol_filter_period = 20
    vol_filter_threshold = 0.6

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = _State()

    @staticmethod
    def _is_swing_high(highs: np.ndarray, idx: int, lookback: int = 2) -> bool:
        start = max(0, idx - lookback)
        end = min(len(highs), idx + lookback + 1)
        if idx - start < lookback or end - idx - 1 < lookback:
            return False
        return highs[idx] == np.max(highs[start:end])

    @staticmethod
    def _is_swing_low(lows: np.ndarray, idx: int, lookback: int = 2) -> bool:
        start = max(0, idx - lookback)
        end = min(len(lows), idx + lookback + 1)
        if idx - start < lookback or end - idx - 1 < lookback:
            return False
        return lows[idx] == np.min(lows[start:end])

    def _check_volatility(self, atr_values: np.ndarray) -> np.ndarray:
        atr_sma = DataFrame(atr_values).rolling(self.vol_filter_period).mean().iloc[:, 0].values
        return np.where(
            np.isnan(atr_values) | np.isnan(atr_sma),
            False,
            atr_values >= atr_sma * self.vol_filter_threshold,
        )

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df["ema"] = ta.EMA(df, timeperiod=self.ema_period)
        df["atr"] = ta.ATR(df, timeperiod=self.atr_period)
        df["vol_sma"] = ta.SMA(df["volume"], timeperiod=20)
        df["vol_ok"] = self._check_volatility(df["atr"].fillna(0).values)
        df["swing_high"] = 0
        df["swing_low"] = 0
        df["enter_long"] = 0
        df["enter_short"] = 0
        df["exit_long"] = 0
        df["exit_short"] = 0

        state = _State()
        highs = df["high"].values
        lows = df["low"].values
        closes = df["close"].values
        ema = df["ema"].values

        for i in range(len(df)):
            if i < 3:
                continue
            if not bool(df["vol_ok"].iloc[i]):
                state.reset()
                continue
            if np.isnan(ema[i]):
                continue

            current_close = closes[i]
            current_ema = ema[i]

            if state.state != "IDLE":
                if state.direction == "bullish" and current_close < current_ema:
                    state.reset()
                elif state.direction == "bearish" and current_close > current_ema:
                    state.reset()

            if state.state == "IDLE":
                if current_close > current_ema:
                    state.state = "ABOVE_EMA"
                    state.direction = "bullish"
                    state.cross_idx = i if closes[i - 1] <= ema[i - 1] else max(0, i - 5)
                else:
                    state.state = "BELOW_EMA"
                    state.direction = "bearish"
                    state.cross_idx = i if closes[i - 1] >= ema[i - 1] else max(0, i - 5)

            elif state.state == "ABOVE_EMA":
                if state.h1 is None:
                    for j in range(max((state.cross_idx or 0) + 1, i - 3), i + 1):
                        if self._is_swing_high(highs, j) and highs[j] > ema[j] and closes[j] > ema[j]:
                            state.h1 = highs[j]
                            state.h1_idx = j
                            state.state = "H1_FOUND"
                            break

            elif state.state == "H1_FOUND":
                if state.l1 is None and state.h1_idx is not None:
                    for j in range(max(state.h1_idx + 1, i - 3), i + 1):
                        if self._is_swing_low(lows, j) and lows[j] > ema[j] and lows[j] < state.h1:
                            state.l1 = lows[j]
                            state.l1_idx = j
                            state.state = "PULLBACK_L1"
                            break

            elif state.state == "PULLBACK_L1":
                if state.h1 is not None and state.l1_idx is not None:
                    if highs[i] > state.h1:
                        df.loc[df.index[i], "enter_long"] = 1
                        state.reset()

            elif state.state == "BELOW_EMA":
                if state.l1 is None:
                    for j in range(max((state.cross_idx or 0) + 1, i - 3), i + 1):
                        if self._is_swing_low(lows, j) and lows[j] < ema[j] and closes[j] < ema[j]:
                            state.l1 = lows[j]
                            state.l1_idx = j
                            state.state = "L1_FOUND"
                            break

            elif state.state == "L1_FOUND":
                if state.h1 is None and state.l1_idx is not None:
                    for j in range(max(state.l1_idx + 1, i - 3), i + 1):
                        if self._is_swing_high(highs, j) and highs[j] < ema[j] and highs[j] > state.l1:
                            state.h1 = highs[j]
                            state.h1_idx = j
                            state.state = "PULLBACK_H1"
                            break

            elif state.state == "PULLBACK_H1":
                if state.h1 is not None and state.l1_idx is not None:
                    if lows[i] < state.l1:
                        df.loc[df.index[i], "enter_short"] = 1
                        state.reset()

            if current_close < current_ema:
                df.loc[df.index[i], "exit_long"] = 1
            if current_close > current_ema:
                df.loc[df.index[i], "exit_short"] = 1

        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

