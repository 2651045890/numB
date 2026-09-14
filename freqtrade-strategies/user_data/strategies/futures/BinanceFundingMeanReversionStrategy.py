# SEMANTIC-PRESERVING FREQTRADE PORT
# Source: Gotodataru/binance-futures-backtest@5ed0d6e39d8a3e951bea40c66e2638c213012e1b
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, merge_informative_pair
from binance_futures_metrics import merge_aux

class BinanceFundingMeanReversionStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="15m"; startup_candle_count=102
    minimal_roi={"0":100.0}; stoploss=-0.99; use_exit_signal=False
    ema_period=50; threshold_high=0.0005; threshold_low=0.0001; hold_bars=16
    def informative_pairs(self):
        return [(p,"1h","funding_rate") for p in self.dp.current_whitelist()]
    def populate_indicators(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        dataframe=merge_aux(dataframe,metadata["pair"],self.timeframe)
        fr=self.dp.get_pair_dataframe(metadata["pair"],"1h",candle_type="funding_rate")
        if not fr.empty:
            dataframe=merge_informative_pair(dataframe,fr,self.timeframe,"1h",ffill=True,append_timeframe=True)
            candidates=[c for c in dataframe if c.startswith("open_") and c.endswith("_1h")]
            dataframe["funding_rate"]=dataframe[candidates[0]] if candidates else float("nan")
        else:dataframe["funding_rate"]=float("nan")
        dataframe["ema_lag"]=dataframe.close.ewm(span=self.ema_period,adjust=False).mean().shift(1)
        dataframe["funding_lag"]=dataframe.funding_rate.ffill().shift(1)
        dataframe["buy_ratio_lag"]=dataframe.buy_ratio.shift(1)
        return dataframe
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[(d.funding_lag < -self.threshold_low)&(d.close<d.ema_lag)&(d.buy_ratio_lag>0.45),"enter_long"]=1
        d.loc[(d.funding_lag > self.threshold_high)&(d.close>d.ema_lag)&(d.buy_ratio_lag<0.55),"enter_short"]=1
        return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:return d
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if (current_time-trade.open_date_utc).total_seconds()>=self.hold_bars*15*60:return "hold_bars"

