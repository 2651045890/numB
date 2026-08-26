# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- 不要删除这些库 ---
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from pandas import DataFrame
from typing import Dict, Optional, Union, Tuple

# 导入freqtrade策略相关模块
from freqtrade.strategy import (
    IStrategy,  # 策略基类
    Trade,      # 交易对象
    Order,      # 订单对象
    PairLocks,  # 交易对锁定
    informative,  # @informative装饰器，用于获取更高时间框架数据
    # 超参数优化参数类型
    BooleanParameter,     # 布尔参数
    CategoricalParameter, # 分类参数
    DecimalParameter,     # 小数参数
    IntParameter,         # 整数参数
    RealParameter,        # 实数参数
    # 时间框架辅助函数
    timeframe_to_minutes,   # 时间框架转分钟
    timeframe_to_next_date, # 时间框架到下一个日期
    timeframe_to_prev_date, # 时间框架到上一个日期
    # 策略辅助函数
    merge_informative_pair, # 合并信息对数据
    stoploss_from_absolute, # 从绝对值计算止损
    stoploss_from_open,     # 从开仓价计算止损
    AnnotationType,         # 注释类型
)

# --------------------------------
# 在此处添加您要导入的库
import talib.abstract as ta    # TA-Lib技术分析库
from technical import qtpylib  # QTPyLib技术分析库


class AwesomeStrategy(IStrategy):
    """
    这是一个策略模板，帮助您开始构建策略。
    更多信息请访问 https://www.freqtrade.io/en/latest/strategy-customization/

    您可以：
        :return: 包含策略所有必需指标的数据框
    - 重命名类名（不要忘记更新class_name）
    - 添加任何您想要构建策略的方法
    - 添加任何您需要构建策略的库

    您必须保留：
    - "不要删除这些库"部分中的库
    - 方法：populate_indicators, populate_entry_trend, populate_exit_trend
    您应该保留：
    - timeframe, minimal_roi, stoploss, trailing_*
    """

    # 策略接口版本 - 允许策略接口的新迭代
    # 查看文档或示例策略以获取最新版本
    INTERFACE_VERSION = 3

    # 策略的最佳时间框架
    timeframe = "5m" # 策略在 5 分钟级别运行。

    # 此策略是否可以做空？ 
    can_short: bool = False # 不允许开空单。

    # 为策略设计的最小投资回报率(ROI)
    # 如果配置文件包含"minimal_roi"，此属性将被覆盖
    minimal_roi = {
        "60": 0.01,  # 60分钟后最小1%收益  持仓满 60 分钟后，1% 盈利即可卖出
        "30": 0.02,  # 30分钟后最小2%收益  持仓满 30 分钟后，2% 盈利即可卖出
        "0": 0.04,   # 立即最小4%收益      一旦盈利达到 4%，立即卖出
    }

    # 为策略设计的最佳止损
    # 如果配置文件包含"stoploss"，此属性将被覆盖
    stoploss = -0.10  # 10%止损  最大亏损 -10%

    # 追踪止损设置
    trailing_stop = False  # 是否启用追踪止损
    # trailing_stop_positive = 0.01        # 正向追踪止损阈值
    # trailing_stop_positive_offset = 0.0  # 追踪止损偏移量（已禁用/未配置）
    # trailing_only_offset_is_reached = False  # 仅在达到偏移量时追踪
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = True
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # 策略参数 - 超参数优化
    buy_rsi = IntParameter(10, 40, default=30, space="buy")  # RSI买入阈值参数
    sell_rsi = IntParameter(60, 90, default=70, space="sell")  # RSI卖出阈值参数# Optional order type mapping.
    order_types = {
        "entry": "limit",
        "exit": "limit",
        "stoploss": "market",
        "stoploss_on_exchange": False
    }

    # Optional order time in force.
    order_time_in_force = {
        "entry": "GTC",
        "exit": "GTC"
    }
    @property
    def plot_config(self):
        """
        绘图配置 - 定义策略图表的显示方式
        """
        return {
            # 主图指标（移动平均线等）
            "main_plot": {
                "tema": {},  # 三重指数移动平均线
                "sar": {"color": "white"},  # 抛物线SAR，白色显示
            },
            "subplots": {
                # 子图 - 每个字典定义一个额外的绘图区域
                "MACD": {
                    "macd": {"color": "blue"},  # MACD线，蓝色显示
                    "macdsignal": {"color": "orange"},  # MACD信号线，橙色显示
                },
                "RSI": {
                    "rsi": {"color": "red"},  # RSI指标，红色显示
                }
            }
        }

    def informative_pairs(self):
        """
        定义要从交易所缓存的额外信息性货币对/时间间隔组合。
        这些货币对/时间间隔组合是不可交易的，除非它们也是白名单的一部分。
        更多信息请查阅文档
        :return: 格式为(pair, interval)的元组列表
            示例: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        为给定的数据框添加多个不同的技术分析指标

        性能提示：为了获得最佳性能，请谨慎选择使用的指标数量。
        只取消注释您在策略或超参数优化配置中使用的指标，
        否则会浪费内存和CPU使用率。
        :param dataframe: 来自交易所的数据框
        :param metadata: 附加信息，如当前交易的货币对
        :return: 包含策略所有必需指标的数据框
        """
        # 动量指标
        # ------------------------------------

        # ADX - 平均趋向指数（衡量趋势强度）
        dataframe["adx"] = ta.ADX(dataframe)

        # # 正向趋向指标/运动
        # dataframe["plus_dm"] = ta.PLUS_DM(dataframe)   # 正向运动
        # dataframe["plus_di"] = ta.PLUS_DI(dataframe)   # 正向趋向指标

        # # 负向趋向指标/运动
        # dataframe["minus_dm"] = ta.MINUS_DM(dataframe) # 负向运动
        # dataframe["minus_di"] = ta.MINUS_DI(dataframe) # 负向趋向指标

        # # Aroon指标，Aroon振荡器
        # aroon = ta.AROON(dataframe)
        # dataframe["aroonup"] = aroon["aroonup"]       # Aroon上升线
        # dataframe["aroondown"] = aroon["aroondown"]   # Aroon下降线
        # dataframe["aroonosc"] = ta.AROONOSC(dataframe) # Aroon振荡器

        # # 超棒振荡器（Awesome Oscillator）
        # dataframe["ao"] = qtpylib.awesome_oscillator(dataframe)

        # # 肯特纳通道（Keltner Channel）
        # keltner = qtpylib.keltner_channel(dataframe)
        # dataframe["kc_upperband"] = keltner["upper"]   # 上轨
        # dataframe["kc_lowerband"] = keltner["lower"]   # 下轨
        # dataframe["kc_middleband"] = keltner["mid"]     # 中轨
        # dataframe["kc_percent"] = (                     # 价格在通道中的位置百分比
        #     (dataframe["close"] - dataframe["kc_lowerband"]) /
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"])
        # )
        # dataframe["kc_width"] = (                       # 通道宽度
        #     (dataframe["kc_upperband"] - dataframe["kc_lowerband"]) / dataframe["kc_middleband"]
        # )

        # # 终极振荡器（Ultimate Oscillator）
        # dataframe["uo"] = ta.ULTOSC(dataframe)

        # # 商品通道指数：数值范围[超卖:-100, 超买:100]
        # dataframe["cci"] = ta.CCI(dataframe)

        # RSI - 相对强弱指数（衡量超买超卖）
        dataframe["rsi"] = ta.RSI(dataframe)

        # # RSI的逆费雪变换：数值范围[-1.0, 1.0] (https://goo.gl/2JGGoy)
        # rsi = 0.1 * (dataframe["rsi"] - 50)
        # dataframe["fisher_rsi"] = (np.exp(2 * rsi) - 1) / (np.exp(2 * rsi) + 1)

        # # RSI逆费雪变换标准化：数值范围[0.0, 100.0] (https://goo.gl/2JGGoy)
        # dataframe["fisher_rsi_norma"] = 50 * (dataframe["fisher_rsi"] + 1)

        # # 慢速随机指标
        # stoch = ta.STOCH(dataframe)
        # dataframe["slowd"] = stoch["slowd"]  # 慢速%D线
        # dataframe["slowk"] = stoch["slowk"]  # 慢速%K线

        # 快速随机指标
        stoch_fast = ta.STOCHF(dataframe)
        dataframe["fastd"] = stoch_fast["fastd"]  # 快速%D线
        dataframe["fastk"] = stoch_fast["fastk"]  # 快速%K线

        # # 随机RSI指标
        # 使用前请阅读 https://github.com/freqtrade/freqtrade/issues/2961
        # STOCHRSI与TradingView不一致，可能导致意外结果
        # stoch_rsi = ta.STOCHRSI(dataframe)
        # dataframe["fastd_rsi"] = stoch_rsi["fastd"]  # RSI快速%D线
        # dataframe["fastk_rsi"] = stoch_rsi["fastk"]  # RSI快速%K线

        # MACD - 移动平均收敛发散指标
        macd = ta.MACD(dataframe)
        dataframe["macd"] = macd["macd"]              # MACD线
        dataframe["macdsignal"] = macd["macdsignal"]  # MACD信号线
        dataframe["macdhist"] = macd["macdhist"]      # MACD柱状图

        # MFI - 资金流量指标（衡量买卖压力）
        dataframe["mfi"] = ta.MFI(dataframe)

        # # ROC - 变动率指标
        # dataframe["roc"] = ta.ROC(dataframe)

        # 重叠研究指标
        # ------------------------------------

        # 布林带（Bollinger Bands）
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe["bb_lowerband"] = bollinger["lower"]   # 布林带下轨
        dataframe["bb_middleband"] = bollinger["mid"]    # 布林带中轨（20日移动平均线）
        dataframe["bb_upperband"] = bollinger["upper"]   # 布林带上轨
        dataframe["bb_percent"] = (                       # 价格在布林带中的位置百分比
            (dataframe["close"] - dataframe["bb_lowerband"]) /
            (dataframe["bb_upperband"] - dataframe["bb_lowerband"])
        )
        dataframe["bb_width"] = (                         # 布林带宽度（衡量波动性）
            (dataframe["bb_upperband"] - dataframe["bb_lowerband"]) / dataframe["bb_middleband"]
        )

        # Bollinger Bands - Weighted (EMA based instead of SMA)
        # weighted_bollinger = qtpylib.weighted_bollinger_bands(
        #     qtpylib.typical_price(dataframe), window=20, stds=2
        # )
        # dataframe["wbb_upperband"] = weighted_bollinger["upper"]
        # dataframe["wbb_lowerband"] = weighted_bollinger["lower"]
        # dataframe["wbb_middleband"] = weighted_bollinger["mid"]
        # dataframe["wbb_percent"] = (
        #     (dataframe["close"] - dataframe["wbb_lowerband"]) /
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"])
        # )
        # dataframe["wbb_width"] = (
        #     (dataframe["wbb_upperband"] - dataframe["wbb_lowerband"]) / dataframe["wbb_middleband"]
        # )

        # # EMA - Exponential Moving Average
        # dataframe["ema3"] = ta.EMA(dataframe, timeperiod=3)
        # dataframe["ema5"] = ta.EMA(dataframe, timeperiod=5)
        # dataframe["ema10"] = ta.EMA(dataframe, timeperiod=10)
        # dataframe["ema21"] = ta.EMA(dataframe, timeperiod=21)
        # dataframe["ema50"] = ta.EMA(dataframe, timeperiod=50)
        # dataframe["ema100"] = ta.EMA(dataframe, timeperiod=100)

        # # SMA - Simple Moving Average
        # dataframe["sma3"] = ta.SMA(dataframe, timeperiod=3)
        # dataframe["sma5"] = ta.SMA(dataframe, timeperiod=5)
        # dataframe["sma10"] = ta.SMA(dataframe, timeperiod=10)
        # dataframe["sma21"] = ta.SMA(dataframe, timeperiod=21)
        # dataframe["sma50"] = ta.SMA(dataframe, timeperiod=50)
        # dataframe["sma100"] = ta.SMA(dataframe, timeperiod=100)

        # 抛物线SAR（止损和反转指标）
        dataframe["sar"] = ta.SAR(dataframe)

        # TEMA - 三重指数移动平均线（减少滞后性）
        dataframe["tema"] = ta.TEMA(dataframe, timeperiod=9)

        # 周期指标
        # ------------------------------------
        # 希尔伯特变换指标 - 正弦波
        hilbert = ta.HT_SINE(dataframe)
        dataframe["htsine"] = hilbert["sine"]          # 正弦波
        dataframe["htleadsine"] = hilbert["leadsine"]  # 领先正弦波

        # Pattern Recognition - Bullish candlestick patterns
        # ------------------------------------
        # # Hammer: values [0, 100]
        # dataframe["CDLHAMMER"] = ta.CDLHAMMER(dataframe)
        # # Inverted Hammer: values [0, 100]
        # dataframe["CDLINVERTEDHAMMER"] = ta.CDLINVERTEDHAMMER(dataframe)
        # # Dragonfly Doji: values [0, 100]
        # dataframe["CDLDRAGONFLYDOJI"] = ta.CDLDRAGONFLYDOJI(dataframe)
        # # Piercing Line: values [0, 100]
        # dataframe["CDLPIERCING"] = ta.CDLPIERCING(dataframe) # values [0, 100]
        # # Morningstar: values [0, 100]
        # dataframe["CDLMORNINGSTAR"] = ta.CDLMORNINGSTAR(dataframe) # values [0, 100]
        # # Three White Soldiers: values [0, 100]
        # dataframe["CDL3WHITESOLDIERS"] = ta.CDL3WHITESOLDIERS(dataframe) # values [0, 100]

        # Pattern Recognition - Bearish candlestick patterns
        # ------------------------------------
        # # Hanging Man: values [0, 100]
        # dataframe["CDLHANGINGMAN"] = ta.CDLHANGINGMAN(dataframe)
        # # Shooting Star: values [0, 100]
        # dataframe["CDLSHOOTINGSTAR"] = ta.CDLSHOOTINGSTAR(dataframe)
        # # Gravestone Doji: values [0, 100]
        # dataframe["CDLGRAVESTONEDOJI"] = ta.CDLGRAVESTONEDOJI(dataframe)
        # # Dark Cloud Cover: values [0, 100]
        # dataframe["CDLDARKCLOUDCOVER"] = ta.CDLDARKCLOUDCOVER(dataframe)
        # # Evening Doji Star: values [0, 100]
        # dataframe["CDLEVENINGDOJISTAR"] = ta.CDLEVENINGDOJISTAR(dataframe)
        # # Evening Star: values [0, 100]
        # dataframe["CDLEVENINGSTAR"] = ta.CDLEVENINGSTAR(dataframe)

        # Pattern Recognition - Bullish/Bearish candlestick patterns
        # ------------------------------------
        # # Three Line Strike: values [0, -100, 100]
        # dataframe["CDL3LINESTRIKE"] = ta.CDL3LINESTRIKE(dataframe)
        # # Spinning Top: values [0, -100, 100]
        # dataframe["CDLSPINNINGTOP"] = ta.CDLSPINNINGTOP(dataframe) # values [0, -100, 100]
        # # Engulfing: values [0, -100, 100]
        # dataframe["CDLENGULFING"] = ta.CDLENGULFING(dataframe) # values [0, -100, 100]
        # # Harami: values [0, -100, 100]
        # dataframe["CDLHARAMI"] = ta.CDLHARAMI(dataframe) # values [0, -100, 100]
        # # Three Outside Up/Down: values [0, -100, 100]
        # dataframe["CDL3OUTSIDE"] = ta.CDL3OUTSIDE(dataframe) # values [0, -100, 100]
        # # Three Inside Up/Down: values [0, -100, 100]
        # dataframe["CDL3INSIDE"] = ta.CDL3INSIDE(dataframe) # values [0, -100, 100]

        # # Chart type
        # # ------------------------------------
        # # Heikin Ashi Strategy
        # heikinashi = qtpylib.heikinashi(dataframe)
        # dataframe["ha_open"] = heikinashi["open"]
        # dataframe["ha_close"] = heikinashi["close"]
        # dataframe["ha_high"] = heikinashi["high"]
        # dataframe["ha_low"] = heikinashi["low"]

        # Retrieve best bid and best ask from the orderbook
        # ------------------------------------
        """
        # first check if dataprovider is available
        if self.dp:
            if self.dp.runmode.value in ("live", "dry_run"):
                ob = self.dp.orderbook(metadata["pair"], 1)
                dataframe["best_bid"] = ob["bids"][0][0]
                dataframe["best_ask"] = ob["asks"][0][0]
        """

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于技术分析指标，为给定数据框填充入场信号
        :param dataframe: 数据框
        :param metadata: 附加信息，如当前交易的货币对
        :return: 填充了入场列的数据框
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.buy_rsi.value)) &  # 信号：RSI向上穿越买入阈值
                (dataframe["tema"] <= dataframe["bb_middleband"]) &  # 守卫：TEMA在布林带中轨下方
                (dataframe["tema"] > dataframe["tema"].shift(1)) &  # 守卫：TEMA正在上升
                (dataframe["volume"] > 0)  # 确保成交量不为0
            ),
            "enter_long"] = 1  # 做多入场信号
        # 取消注释以使用做空（仅在期货/保证金模式下使用。查看文档了解更多信息）
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.sell_rsi.value)) &  # 信号：RSI向上穿越卖出阈值
                (dataframe["tema"] > dataframe["bb_middleband"]) &  # 守卫：TEMA在布林带中轨上方
                (dataframe["tema"] < dataframe["tema"].shift(1)) &  # 守卫：TEMA正在下降
                (dataframe['volume'] > 0)  # 确保成交量不为0
            ),
            'enter_short'] = 1  # 做空入场信号
        """

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        基于技术分析指标，为给定数据框填充出场信号
        :param dataframe: 数据框
        :param metadata: 附加信息，如当前交易的货币对
        :return: 填充了出场列的数据框
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.sell_rsi.value)) &  # 信号：RSI向上穿越卖出阈值
                (dataframe["tema"] > dataframe["bb_middleband"]) &  # 守卫：TEMA在布林带中轨上方
                (dataframe["tema"] < dataframe["tema"].shift(1)) &  # 守卫：TEMA正在下降
                (dataframe["volume"] > 0)  # 确保成交量不为0
            ),
            "exit_long"] = 1  # 做多出场信号
        # 取消注释以使用做空（仅在期货/保证金模式下使用。查看文档了解更多信息）
        """
        dataframe.loc[
            (
                (qtpylib.crossed_above(dataframe["rsi"], self.buy_rsi.value)) &  # 信号：RSI向上穿越买入阈值
                (dataframe["tema"] <= dataframe["bb_middleband"]) &  # 守卫：TEMA在布林带中轨下方
                (dataframe["tema"] > dataframe["tema"].shift(1)) &  # 守卫：TEMA正在上升
                (dataframe['volume'] > 0)  # 确保成交量不为0
            ),
            'exit_short'] = 1  # 做空出场信号
        """
        return dataframe