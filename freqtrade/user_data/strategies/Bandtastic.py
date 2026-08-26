import talib.abstract as ta
import numpy as np  # noqa
import pandas as pd
from functools import reduce
from pandas import DataFrame
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import IStrategy, CategoricalParameter, DecimalParameter, IntParameter, RealParameter

__author__ = "Robert Roman"
__copyright__ = "Free For Use"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Robert Roman"
__email__ = "robertroman7@gmail.com"
__BTC_donation__ = "3FgFaG15yntZYSUzfEpxr5mDt1RArvcQrK"


# Optimized With Sharpe Ratio and 1 year data
# 199/40000:  30918 trades. 18982/3408/8528 Wins/Draws/Losses. Avg profit   0.39%. Median profit   0.65%. Total profit  119934.26007495 USDT ( 119.93%). Avg duration 8:12:00 min. Objective: -127.60220

class Bandtastic(IStrategy):
    INTERFACE_VERSION = 3

    timeframe = '15m'

    # ROI table:
    minimal_roi = {  # 卖出逻辑
    "0": 0.162,  # 入场后立即要求 16.2% 的回报
    "69": 0.097, # 69 分钟后要求 9.7%
    "229": 0.061, # 229 分钟后要求 6.1%
    "566": 0      # 566 分钟后无最低回报要求
    }

    # Stoploss:
    stoploss = -0.345 # 止损（stoploss）：-34.5%，即当损失达到 34.5% 时自动平仓，防止更大亏损。

    startup_candle_count = 999 

    # Trailing stop:
    trailing_stop = True # 追踪止盈（trailing_stop）
    trailing_stop_positive = 0.01           # 追踪止盈幅度为 1%（trailing_stop_positive），即价格回落 1% 时触发卖出。
    trailing_stop_positive_offset = 0.058   # 当价格上涨达到 5.8%（trailing_stop_positive_offset）时，启用追踪止盈。
    trailing_only_offset_is_reached = False 
    

    # Hyperopt Buy Parameters
    # 买入参数： V
    # buy_fastema 和 buy_slowema ：快速和慢速 EMA（指数移动平均线）的周期，分别优化范围为 1-236 和 1-250，默认值 211 和 250。
    buy_fastema = IntParameter(low=1, high=236, default=211, space='buy', optimize=True, load=True) # 快速EMA周期 指数移动平均线
    buy_slowema = IntParameter(low=1, high=250, default=250, space='buy', optimize=True, load=True) # 慢速EMA周期 指数移动平均线

    # buy_rsi 和 buy_mfi：RSI（相对强弱指数）和 MFI（资金流向指数）的买入阈值，优化范围为 15-70，默认值 52 和 30。
    buy_rsi = IntParameter(low=15, high=70, default=52, space='buy', optimize=True, load=True) # 使用RSI相对强弱指数买入
    buy_mfi = IntParameter(low=15, high=70, default=30, space='buy', optimize=True, load=True) # 使用MFI资金流向指数买入

    # buy_rsi_enabled, buy_mfi_enabled, buy_ema_enabled ：布尔值，决定是否启用 RSI、MFI 或 EMA 作为买入条件。
    buy_rsi_enabled = CategoricalParameter([True, False], space='buy', optimize=True, default=False) # 是否启用RSI
    buy_mfi_enabled = CategoricalParameter([True, False], space='buy', optimize=True, default=False) # 是否启用MFI
    buy_ema_enabled = CategoricalParameter([True, False], space='buy', optimize=True, default=False) # 是否启用EMA

    # buy_trigger：布林带的下轨选择（bb_lower1 到 bb_lower4），默认使用 bb_lower1。
    buy_trigger = CategoricalParameter(["bb_lower1", "bb_lower2", "bb_lower3", "bb_lower4"], default="bb_lower1", space="buy")

    # Hyperopt Sell Parameters
    # 卖出参数:
    # 与买入类似，但优化范围和默认值不同。例如，sell_fastema 和 sell_slowema 默认值分别为 7 和 6，sell_rsi 和 sell_mfi 默认值分别为 57 和 46。
    sell_fastema = IntParameter(low=1, high=365, default=7, space='sell', optimize=True, load=True)
    sell_slowema = IntParameter(low=1, high=365, default=6, space='sell', optimize=True, load=True)
    sell_rsi = IntParameter(low=30, high=100, default=57, space='sell', optimize=True, load=True)
    sell_mfi = IntParameter(low=30, high=100, default=46, space='sell', optimize=True, load=True)

    # 
    sell_rsi_enabled = CategoricalParameter([True, False], space='sell', optimize=True, default=False)
    sell_mfi_enabled = CategoricalParameter([True, False], space='sell', optimize=True, default=True)
    sell_ema_enabled = CategoricalParameter([True, False], space='sell', optimize=True, default=False)
    sell_trigger = CategoricalParameter(["sell-bb_upper1", "sell-bb_upper2", "sell-bb_upper3", "sell-bb_upper4"], default="sell-bb_upper2", space="sell")

    # 技术指标
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe) # 相对强弱指数：衡量价格的超买或超卖状态 
        dataframe['mfi'] = ta.MFI(dataframe) # 资金流向指数：结合价格和成交量，评估资金流入/流出的强度

        # Bollinger Bands 1,2,3 and 4  布林带 
        # 使用20周期的典型价格(（高+低+收盘）/3)计算1、2、3、4个标准差的上下轨
        # 列如: bb_lowerband1 是1的标准差的下轨、bb_lowerband4是4标准差的下轨
        bollinger1 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=1)
        dataframe['bb_lowerband1'] = bollinger1['lower']
        dataframe['bb_middleband1'] = bollinger1['mid']
        dataframe['bb_upperband1'] = bollinger1['upper']

        bollinger2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband2'] = bollinger2['lower']
        dataframe['bb_middleband2'] = bollinger2['mid']
        dataframe['bb_upperband2'] = bollinger2['upper']

        bollinger3 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=3)
        dataframe['bb_lowerband3'] = bollinger3['lower']
        dataframe['bb_middleband3'] = bollinger3['mid']
        dataframe['bb_upperband3'] = bollinger3['upper']

        bollinger4 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=4)
        dataframe['bb_lowerband4'] = bollinger4['lower']
        dataframe['bb_middleband4'] = bollinger4['mid']
        dataframe['bb_upperband4'] = bollinger4['upper']

        # Build EMA rows - combine all ranges to a single set to avoid duplicate calculations.
        for period in set( # EMA(指数移动平均线): 计算不同周期的EMA，用于趋势判断
                list(self.buy_fastema.range)
                + list(self.buy_slowema.range)
                + list(self.sell_fastema.range)
                + list(self.sell_slowema.range)
            ):
            dataframe[f'EMA_{period}'] = ta.EMA(dataframe, timeperiod=period)

        return dataframe

    # 买入逻辑，触发条件，：收盘价低于布林带的下轨（由 buy_trigger 决定，例如 bb_lowerband1）。
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # GUARDS 保护条件，可选，取决于buy_*_enabled
        if self.buy_rsi_enabled.value: # RSI < buy_rsi 默认52
            conditions.append(dataframe['rsi'] < self.buy_rsi.value)
        if self.buy_mfi_enabled.value: # MFI < buy_mfi 默认30
            conditions.append(dataframe['mfi'] < self.buy_mfi.value)
        if self.buy_ema_enabled.value: # 快速EMA > 慢速EMA
            conditions.append(dataframe[f'EMA_{self.buy_fastema.value}'] > dataframe[f'EMA_{self.buy_slowema.value}'])

        # TRIGGERS
        if self.buy_trigger.value == 'bb_lower1':
            conditions.append(dataframe["close"] < dataframe['bb_lowerband1'])
        if self.buy_trigger.value == 'bb_lower2':
            conditions.append(dataframe["close"] < dataframe['bb_lowerband2'])
        if self.buy_trigger.value == 'bb_lower3':
            conditions.append(dataframe["close"] < dataframe['bb_lowerband3'])
        if self.buy_trigger.value == 'bb_lower4':
            conditions.append(dataframe["close"] < dataframe['bb_lowerband4'])

        # Check that volume is not 0 确保成交量大于0，避免无效数据
        conditions.append(dataframe['volume'] > 0)

        if conditions:  # 当所有条件满足时，设置enter_long = 1，触发买入。
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'] = 1 

        return dataframe

    # 卖出逻辑， 收盘价高于布林带的上轨（由 sell_trigger 决定，例如 bb_upperband2）。
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []

        # GUARDS 保护条件
        if self.sell_rsi_enabled.value: # RSI > sell_rsi 默认57
            conditions.append(dataframe['rsi'] > self.sell_rsi.value)
        if self.sell_mfi_enabled.value: # MFI > sell_mfi 默认46
            conditions.append(dataframe['mfi'] > self.sell_mfi.value)
        if self.sell_ema_enabled.value: # 快速EMA < 慢速EMA
            conditions.append(dataframe[f'EMA_{self.sell_fastema.value}'] < dataframe[f'EMA_{self.sell_slowema.value}'])

        # TRIGGERS
        if self.sell_trigger.value == 'sell-bb_upper1':
            conditions.append(dataframe["close"] > dataframe['bb_upperband1'])
        if self.sell_trigger.value == 'sell-bb_upper2':
            conditions.append(dataframe["close"] > dataframe['bb_upperband2'])
        if self.sell_trigger.value == 'sell-bb_upper3':
            conditions.append(dataframe["close"] > dataframe['bb_upperband3'])
        if self.sell_trigger.value == 'sell-bb_upper4':
            conditions.append(dataframe["close"] > dataframe['bb_upperband4'])

        # Check that volume is not 0 成交量大于0 
        conditions.append(dataframe['volume'] > 0)

        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'] = 1 # 设置=1，触发卖出

        return dataframe
