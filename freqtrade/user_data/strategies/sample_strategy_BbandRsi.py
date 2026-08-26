from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib

class BbandRsi(IStrategy):

    # config文件中如果有 "minimal_roi"则会重写下面的minimal_roi
    # 1min 中后roi为正就继续持有，0min后roi大于-0.1%则继续持有。。。
    minimal_roi = {
         "1": 0.00, # 持仓 1分钟后，只要回报率 ≥ 0 就继续持有。
         "0": -0.001  # 持仓 0分钟后，只要回报率 ≥ -0.1% 也继续持有。
    }
    stoploss = -100 # 允许的最大止损是 -100%，也就是没有真正启用止损。
    # 一旦买入，不会因为价格下跌而自动止损，退出全靠 exit_trend。

    timeframe = '15m'
    # 策略运行在 15分钟K线 上。

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        # RSI (14周期)

        # Bollinger bands
        bollinger = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
        dataframe['bb_lowerband'] = bollinger['lower']
        dataframe['bb_middleband'] = bollinger['mid']
        dataframe['bb_upperband'] = bollinger['upper']

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] < 30) &
                    (dataframe['close'] < dataframe['bb_lowerband'])

            ),
            'buy'] = 1
        # RSI < 30 → 市场超卖，价格被压低。
        # 收盘价 < 下轨 → 跌破布林带下轨，说明严重偏离均值，可能反弹。
        # 👉 也就是 价格严重低估 + 超卖 时才买入。

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['rsi'] > 70)

            ),
            'sell'] = 1
        # ✅ 卖出条件：
        # RSI > 70 → 市场超买，价格可能出现回调。
        # 👉 一旦市场过热，就卖出止盈/止损。

        return dataframe