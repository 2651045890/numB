# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/Crypto-Data-API/hyperliquid-backtester
# Original commit: a9dd95dafe0ce3cfae087449a51c683eda725bee
# Original files: strategies/examples/bollinger_revert.py, src/hlbt/indicators.py, src/hlbt/backtester.py
# Original market: Hyperliquid perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
import numpy as np
import pandas as pd
from pandas import DataFrame, Series
from freqtrade.strategy import IStrategy
from HyperliquidRsiReversionStrategy import _wilder_rsi

def _wilder_atr(df: DataFrame, period: int) -> Series:
    pc=df.close.shift(1); tr=pd.concat([df.high-df.low,(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1).to_numpy(float)
    out=np.full(tr.shape,np.nan)
    if len(tr)>=period:
        out[period-1]=tr[:period].mean()
        for i in range(period,len(tr)):out[i]=(out[i-1]*(period-1)+tr[i])/period
    return Series(out,index=df.index)

class HyperliquidBollingerRevertStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="15m"; startup_candle_count=100
    minimal_roi={"0":100.0}; stoploss=-0.06; use_exit_signal=True
    length=20; band_mult=2.5; rsi_period=2; rsi_overbought=92.0; rsi_oversold=8.0
    min_atr_pct=0.15; hard_take_pct=0.12; time_stop_bars=240

    def populate_indicators(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        dataframe["base"]=dataframe.close.rolling(self.length).mean()
        dataframe["sd"]=dataframe.close.rolling(self.length).std(ddof=0)
        dataframe["upper"]=dataframe.base+self.band_mult*dataframe.sd
        dataframe["lower"]=dataframe.base-self.band_mult*dataframe.sd
        dataframe["source_rsi"]=_wilder_rsi(dataframe.close,self.rsi_period)
        dataframe["source_atr"]=_wilder_atr(dataframe,14)
        return dataframe
    def populate_entry_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        vol=(dataframe.source_atr/dataframe.close)*100.0>=self.min_atr_pct
        dataframe.loc[vol&(dataframe.high>=dataframe.upper)&(dataframe.source_rsi>=self.rsi_overbought)&(dataframe.close>dataframe.base),"enter_short"]=1
        dataframe.loc[vol&(dataframe.low<=dataframe.lower)&(dataframe.source_rsi<=self.rsi_oversold)&(dataframe.close<dataframe.base),"enter_long"]=1
        return dataframe
    def populate_exit_trend(self,dataframe:DataFrame,metadata:dict)->DataFrame:
        dataframe.loc[dataframe.close>=dataframe.base,"exit_long"]=1
        dataframe.loc[dataframe.close<=dataframe.base,"exit_short"]=1; return dataframe
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if current_profit>=self.hard_take_pct:return "take_profit"
        if (current_time-trade.open_date_utc).total_seconds()>=self.time_stop_bars*15*60:return "time_stop"
        return None
