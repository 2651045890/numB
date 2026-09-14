# SEMANTIC-PRESERVING FREQTRADE PORT
# Nunchi-trade/auto-researchtrading@a502e425a40f79473ba438427bd4e920972bb896
from pandas import DataFrame
from freqtrade.strategy import IStrategy
class NunchiMeanReversionStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="1h"; startup_candle_count=24
    minimal_roi={"0":100.0}; stoploss=-0.04; use_exit_signal=True
    window=24; entry_zscore=2.0; exit_zscore=0.5
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d["mean"]=d.close.rolling(self.window).mean(); d["std"]=d.close.rolling(self.window).std(ddof=0); d["z"]=(d.close-d["mean"])/d["std"]; return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.z < -self.entry_zscore,"enter_long"]=1; d.loc[d.z > self.entry_zscore,"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.z.abs()<self.exit_zscore,["exit_long","exit_short"]]=1; return d

