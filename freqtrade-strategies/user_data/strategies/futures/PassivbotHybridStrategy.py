from __future__ import annotations

from pandas import DataFrame
import talib.abstract as ta

from freqtrade.strategy import IStrategy
import freqtrade.vendor.qtpylib.indicators as qtpylib


class PassivbotHybridStrategy(IStrategy):
    """
    Passivbot 风格混合策略的 Freqtrade 适配版。

    说明：
    - 原 passivbot 更像独立交易引擎，不是纯 Freqtrade 策略。
    - 这里做的是一个“可被你现有模板管理”的 Freqtrade 版近似实现。
    - 核心保留 EMA 趋势门控、波动率自适应、顺势入场与追踪止损。
    """

    INTERFACE_VERSION = 3
    timeframe = "15m"
    can_short = True
    process_only_new_candles = True
    startup_candle_count = 400
    minimal_roi = {"0": 0.05}
    stoploss = -0.1
    use_exit_signal = True
    exit_profit_only = False
    trailing_stop = True
    trailing_stop_positive = 0.008
    trailing_stop_positive_offset = 0.018
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["ema_fast"] = ta.EMA(dataframe, timeperiod=21)
        dataframe["ema_slow"] = ta.EMA(dataframe, timeperiod=89)
        dataframe["ema_trend1"] = ta.EMA(dataframe, timeperiod=790)
        dataframe["ema_trend2"] = ta.EMA(dataframe, timeperiod=1080)
        dataframe["atr"] = ta.ATR(dataframe, timeperiod=14)
        dataframe["atr_sma"] = ta.SMA(dataframe["atr"], timeperiod=20)
        dataframe["vol_sma"] = ta.SMA(dataframe["volume"], timeperiod=20)
        dataframe["trend_up"] = (dataframe["close"] > dataframe["ema_trend1"]) & (dataframe["ema_trend1"] > dataframe["ema_trend2"])
        dataframe["trend_down"] = (dataframe["close"] < dataframe["ema_trend1"]) & (dataframe["ema_trend1"] < dataframe["ema_trend2"])
        dataframe["volatility_ok"] = dataframe["atr"] > dataframe["atr_sma"] * 0.85
        dataframe["pullback_long"] = dataframe["close"] < dataframe["ema_fast"]
        dataframe["pullback_short"] = dataframe["close"] > dataframe["ema_fast"]
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        long_cond = (
            dataframe["trend_up"]
            & dataframe["volatility_ok"]
            & (dataframe["volume"] > dataframe["vol_sma"])
            & dataframe["pullback_long"]
            & qtpylib.crossed_above(dataframe["close"], dataframe["ema_fast"])
        )
        short_cond = (
            dataframe["trend_down"]
            & dataframe["volatility_ok"]
            & (dataframe["volume"] > dataframe["vol_sma"])
            & dataframe["pullback_short"]
            & qtpylib.crossed_below(dataframe["close"], dataframe["ema_fast"])
        )
        dataframe.loc[long_cond, "enter_long"] = 1
        dataframe.loc[short_cond, "enter_short"] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (qtpylib.crossed_below(dataframe["close"], dataframe["ema_fast"])) | (dataframe["close"] < dataframe["ema_slow"]),
            "exit_long",
        ] = 1
        dataframe.loc[
            (qtpylib.crossed_above(dataframe["close"], dataframe["ema_fast"])) | (dataframe["close"] > dataframe["ema_slow"]),
            "exit_short",
        ] = 1
        return dataframe

