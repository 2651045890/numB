# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/EstebanSP23/crypto_systematic_research
# Original commit: d722857a70331f9605481ef8f32df85b990d351d
# Original files: 2_strategies/03_five_ema_filter/backtest.py
# Original market: BTC perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
from pandas import DataFrame
from freqtrade.strategy import IStrategy

class FiveEmaSlopeFilterStrategy(IStrategy):
    """Source V2: long in an EMA200 up-regime, short in a down-regime."""
    INTERFACE_VERSION=3
    can_short=True
    timeframe="1d"
    startup_candle_count=221
    minimal_roi={"0":100.0}
    stoploss=-0.99
    use_exit_signal=True
    exit_profit_only=False

    def populate_indicators(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        # Exact source formulas: pandas EWM, adjust=False.
        dataframe["ema5"]=dataframe.close.ewm(span=5,adjust=False).mean()
        dataframe["ema200_d"]=dataframe.close.ewm(span=200,adjust=False).mean()
        dataframe["ema200_d_lag20"]=dataframe.ema200_d.shift(20)
        dataframe["uptrend"]=dataframe.ema200_d>dataframe.ema200_d_lag20
        return dataframe

    def populate_entry_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        valid=dataframe.ema200_d_lag20.notna()&(dataframe.volume>0)
        dataframe.loc[valid&dataframe.uptrend&(dataframe.close>dataframe.ema5),["enter_long","enter_tag"]]=(1,"v2_uptrend_long")
        dataframe.loc[valid&(~dataframe.uptrend)&(dataframe.close<dataframe.ema5),["enter_short","enter_tag"]]=(1,"v2_downtrend_short")
        return dataframe

    def populate_exit_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        # Source target becomes None whenever its side condition ceases to hold.
        dataframe.loc[(~dataframe.uptrend)|(dataframe.close<=dataframe.ema5),["exit_long","exit_tag"]]=(1,"v2_target_changed")
        dataframe.loc[dataframe.uptrend|(dataframe.close>=dataframe.ema5),["exit_short","exit_tag"]]=(1,"v2_target_changed")
        return dataframe

    def leverage(self,pair,current_time,current_rate,proposed_leverage,max_leverage,entry_tag,side,**kwargs):
        return 1.0
