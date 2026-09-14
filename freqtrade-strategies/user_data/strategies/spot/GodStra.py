# GodStra Strategy
# Author: @Mablue (Masoud Azizi)
# github: https://github.com/mablue/
# IMPORTANT:Add to your pairlists inside config.json (Under StaticPairList):
#   {
#       "method": "AgeFilter",
#       "min_days_listed": 30
#   },
# IMPORTANT: INSTALL TA BEFOUR RUN(pip install ta)
# IMPORTANT: Use Smallest "max_open_trades" for getting best results inside config.json

# --- Do not remove these libs ---
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from pandas import DataFrame
from ta import add_all_ta_features
from ta.utils import dropna

# --------------------------------



GOD_GENES = [
    "open", "high", "low", "close", "volume", "volume_adi", "volume_obv",
    "volume_cmf", "volume_fi", "volume_mfi", "volume_em", "volume_sma_em", "volume_vpt",
    "volume_nvi", "volume_vwap", "volatility_atr", "volatility_bbm", "volatility_bbh",
    "volatility_bbl", "volatility_bbw", "volatility_bbp", "volatility_bbhi",
    "volatility_bbli", "volatility_kcc", "volatility_kch", "volatility_kcl",
    "volatility_kcw", "volatility_kcp", "volatility_kchi", "volatility_kcli",
    "volatility_dcl", "volatility_dch", "volatility_dcm", "volatility_dcw",
    "volatility_dcp", "volatility_ui", "trend_macd", "trend_macd_signal",
    "trend_macd_diff", "trend_sma_fast", "trend_sma_slow", "trend_ema_fast",
    "trend_ema_slow", "trend_adx", "trend_adx_pos", "trend_adx_neg",
    "trend_vortex_ind_pos", "trend_vortex_ind_neg", "trend_vortex_ind_diff", "trend_trix",
    "trend_mass_index", "trend_cci", "trend_dpo", "trend_kst", "trend_kst_sig",
    "trend_kst_diff", "trend_ichimoku_conv", "trend_ichimoku_base", "trend_ichimoku_a",
    "trend_ichimoku_b", "trend_visual_ichimoku_a", "trend_visual_ichimoku_b",
    "trend_aroon_up", "trend_aroon_down", "trend_aroon_ind", "trend_psar_up",
    "trend_psar_down", "trend_psar_up_indicator", "trend_psar_down_indicator", "trend_stc",
    "momentum_rsi", "momentum_stoch_rsi", "momentum_stoch_rsi_k", "momentum_stoch_rsi_d",
    "momentum_tsi", "momentum_uo", "momentum_stoch", "momentum_stoch_signal", "momentum_wr",
    "momentum_ao", "momentum_kama", "momentum_roc", "momentum_ppo", "momentum_ppo_signal",
    "momentum_ppo_hist", "others_dr", "others_dlr", "others_cr",
]
OPERATORS = ["D", ">", "<", "=", "CA", "CB", ">I", "=I", "<I", ">R", "=R", "<R"]


class GodStra(IStrategy):
    # 5/66:      9 trades. 8/0/1 Wins/Draws/Losses. Avg profit  21.83%. Median profit  35.52%. Total profit  1060.11476586 USDT ( 196.50Σ%). Avg duration 3440.0 min. Objective: -7.06960
    # +--------+---------+----------+------------------+--------------+-------------------------------+----------------+-------------+
    # |   Best |   Epoch |   Trades |    Win Draw Loss |   Avg profit |                        Profit |   Avg duration |   Objective |
    # |--------+---------+----------+------------------+--------------+-------------------------------+----------------+-------------|
    # | * Best |   1/500 |       11 |      2    1    8 |        5.22% |  280.74230393 USDT   (57.40%) |      2,421.8 m |    -2.85206 |
    # | * Best |   2/500 |       10 |      7    0    3 |       18.76% |  983.46414442 USDT  (187.58%) |        360.0 m |    -4.32665 |
    # | * Best |   5/500 |        9 |      8    0    1 |       21.83% | 1,060.11476586 USDT  (196.50%) |      3,440.0 m |     -7.0696 |

    INTERFACE_VERSION: int = 3
    can_short = False

    # Freqtrade 2026.7 native Hyperopt parameters, migrated from GodStraHo.
    buy_indicator = CategoricalParameter(GOD_GENES, default="trend_ichimoku_base", space="buy")
    buy_cross = CategoricalParameter(GOD_GENES, default="volatility_kcc", space="buy")
    buy_integer = IntParameter(-1, 100, default=42, space="buy")
    buy_real = DecimalParameter(-1.1, 1.1, decimals=5, default=0.06295, space="buy")
    buy_operator = CategoricalParameter(OPERATORS, default="<R", space="buy")

    sell_indicator = CategoricalParameter(GOD_GENES, default="trend_kst_diff", space="sell")
    sell_cross = CategoricalParameter(GOD_GENES, default="volume_mfi", space="sell")
    sell_integer = IntParameter(-1, 100, default=98, space="sell")
    sell_real = DecimalParameter(-0.01, 1.01, decimals=5, default=0.8779, space="sell")
    sell_operator = CategoricalParameter(OPERATORS, default="=R", space="sell")

    # ROI table:
    minimal_roi = {
        "0": 0.3556,
        "4818": 0.21275,
        "6395": 0.09024,
        "22372": 0
    }

    # Stoploss:
    stoploss = -0.34549

    # Trailing stop:
    trailing_stop = True
    trailing_stop_positive = 0.22673
    trailing_stop_positive_offset = 0.2684
    trailing_only_offset_is_reached = True
    # Buy hypers
    timeframe = '12h'
    @staticmethod
    def _condition(dataframe, operator, indicator, cross, integer, real):
        left = dataframe[indicator]
        right = dataframe[cross]
        operations = {
            "D": dataframe["volume"] >= 0,
            ">": left > right,
            "=": np.isclose(left, right),
            "<": left < right,
            "CA": qtpylib.crossed_above(left, right),
            "CB": qtpylib.crossed_below(left, right),
            ">I": left > integer,
            "=I": left == integer,
            "<I": left < integer,
            ">R": left > real,
            "=R": np.isclose(left, real),
            "<R": left < real,
        }
        return operations[operator]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # Add all ta features
        dataframe = dropna(dataframe)
        dataframe = add_all_ta_features(
            dataframe, open="open", high="high", low="low", close="close", volume="volume",
            fillna=True)
        # dataframe.to_csv("df.csv", index=True)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        condition = self._condition(
            dataframe, self.buy_operator.value, self.buy_indicator.value,
            self.buy_cross.value, self.buy_integer.value, self.buy_real.value,
        )
        dataframe.loc[condition & (dataframe["volume"] > 0), "enter_long"] = 1

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        condition = self._condition(
            dataframe, self.sell_operator.value, self.sell_indicator.value,
            self.sell_cross.value, self.sell_integer.value, self.sell_real.value,
        )
        dataframe.loc[condition & (dataframe["volume"] > 0), "exit_long"] = 1

        return dataframe
