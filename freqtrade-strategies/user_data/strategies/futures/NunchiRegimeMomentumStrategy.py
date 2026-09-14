# SEMANTIC-PRESERVING FREQTRADE PORT
# Nunchi-trade/auto-researchtrading@a502e425a40f79473ba438427bd4e920972bb896
import numpy as np
from pandas import DataFrame
from freqtrade.strategy import IStrategy
class NunchiRegimeMomentumStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="1h"; startup_candle_count=48
    minimal_roi={"0":100.0}; stoploss=-0.08; use_exit_signal=True
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        lr=np.log(d.close).diff(); d["ann_vol"]=lr.rolling(47).std(ddof=0)*np.sqrt(8760); d["fast"]=d.close.rolling(12).mean(); d["slow"]=d.close.rolling(48).mean()
        d["spread_bps"]=np.select([d.ann_vol<.30,d.ann_vol<.60,d.ann_vol<1.0],[10,25,50],default=100); return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.fast>d.slow*(1+d.spread_bps/20000),"enter_long"]=1; d.loc[d.fast<d.slow*(1-d.spread_bps/20000),"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.fast<d.slow,"exit_long"]=1; d.loc[d.fast>d.slow,"exit_short"]=1; return d
