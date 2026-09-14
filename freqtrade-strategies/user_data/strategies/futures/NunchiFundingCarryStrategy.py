# SEMANTIC-PRESERVING FREQTRADE PORT
# Nunchi-trade/auto-researchtrading@a502e425a40f79473ba438427bd4e920972bb896
from pandas import DataFrame
from freqtrade.strategy import IStrategy, merge_informative_pair
class NunchiFundingCarryStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="1h"; startup_candle_count=24
    minimal_roi={"0":100.0}; stoploss=-0.03; use_exit_signal=True
    entry_threshold=0.00005; exit_threshold=0.00001; lookback=24
    def informative_pairs(self): return [(p,"1h","funding_rate") for p in self.dp.current_whitelist()]
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        f=self.dp.get_pair_dataframe(pair=metadata["pair"],timeframe="1h",candle_type="funding_rate")
        if not f.empty:
            d=merge_informative_pair(d,f,self.timeframe,"1h",ffill=True,append_timeframe=True); cols=[c for c in d if c.startswith("open_") and c.endswith("_1h")]; d["funding"]=d[cols[0]] if cols else float("nan")
        else:d["funding"]=float("nan")
        d["avg_funding"]=d.funding.rolling(self.lookback).mean(); return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.avg_funding < -self.entry_threshold,"enter_long"]=1; d.loc[d.avg_funding > self.entry_threshold,"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.avg_funding.abs()<self.exit_threshold,["exit_long","exit_short"]]=1; return d

