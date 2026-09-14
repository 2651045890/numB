# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/OctopusTakopi/24h-rollout-effect
# Original commit: 1963ae4cf1170b8b92d7770812a3697f5c921225
# Original files: scripts/build_trades.py
# Original market: Binance USDT perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
from pandas import DataFrame
from freqtrade.strategy import IStrategy

class Rollout24hEffectStrategy(IStrategy):
    INTERFACE_VERSION=3
    can_short=True
    timeframe="1h"
    startup_candle_count=50
    minimal_roi={"0":100.0}
    stoploss=-0.99
    use_exit_signal=False
    hold_bars=1

    def populate_indicators(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        # Source candle return and exact lag structure.
        dataframe["hour_ret"]=dataframe.close/dataframe.open-1.0
        dataframe["roll_max_24"]=dataframe.hour_ret.rolling(24,min_periods=24).max().shift(1)
        dataframe["roll_min_24"]=dataframe.hour_ret.rolling(24,min_periods=24).min().shift(1)
        dataframe["ret_24h_ago"]=dataframe.hour_ret.shift(24)
        return dataframe

    def populate_entry_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        # Positive extreme rolling out depresses displayed 24h return -> short.
        dataframe.loc[(dataframe.ret_24h_ago>0)&(dataframe.ret_24h_ago>=dataframe.roll_max_24)&(dataframe.volume>0),["enter_short","enter_tag"]]=(1,"positive_extreme_rollout")
        # Negative extreme rolling out lifts displayed 24h return -> long.
        dataframe.loc[(dataframe.ret_24h_ago<0)&(dataframe.ret_24h_ago<=dataframe.roll_min_24)&(dataframe.volume>0),["enter_long","enter_tag"]]=(1,"negative_extreme_rollout")
        return dataframe

    def populate_exit_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        return dataframe

    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if (current_time-trade.open_date_utc).total_seconds()>=self.hold_bars*3600:
            return "one_hour_hold"

    def leverage(self,pair,current_time,current_rate,proposed_leverage,max_leverage,entry_tag,side,**kwargs):
        return 1.0
