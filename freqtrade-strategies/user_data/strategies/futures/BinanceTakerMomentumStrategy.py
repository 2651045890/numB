# SEMANTIC-PRESERVING FREQTRADE PORT
# Source: Gotodataru/binance-futures-backtest@5ed0d6e39d8a3e951bea40c66e2638c213012e1b
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy
from binance_futures_metrics import merge_aux

class BinanceTakerMomentumStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="5m"; startup_candle_count=55
    minimal_roi={"0":0.035}; stoploss=-0.02; use_exit_signal=False
    ma_period=15; confirm_bars=3; threshold_high=0.62; atr_period=14; hold_bars=16
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d=merge_aux(d,metadata["pair"],self.timeframe); br=d.buy_ratio.fillna(0.5)
        d["br_ma"]=br.rolling(self.ma_period,min_periods=self.ma_period).mean().shift(1)
        d["confirm_long"]=(br>0.5).astype(int).rolling(self.confirm_bars).min().shift(1)
        d["confirm_short"]=(br<0.5).astype(int).rolling(self.confirm_bars).min().shift(1)
        pc=d.close.shift(1); tr=pd.concat([d.high-d.low,(d.high-pc).abs(),(d.low-pc).abs()],axis=1).max(axis=1)
        d["atr"]=tr.ewm(span=self.atr_period,adjust=False).mean(); d["atr_ma"]=d.atr.rolling(50,min_periods=20).mean()
        return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        vol=d.atr>d.atr_ma*0.8
        d.loc[(d.br_ma>self.threshold_high)&(d.confirm_long==1)&vol,"enter_long"]=1
        d.loc[(d.br_ma<1-self.threshold_high)&(d.confirm_short==1)&vol,"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:return d
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if (current_time-trade.open_date_utc).total_seconds()>=self.hold_bars*5*60:return "hold_bars"

