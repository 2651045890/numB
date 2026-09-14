# SEMANTIC-PRESERVING FREQTRADE PORT
# Nunchi-trade/auto-researchtrading@a502e425a40f79473ba438427bd4e920972bb896
from pandas import DataFrame
from freqtrade.strategy import IStrategy
class NunchiMomentumBreakoutStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="1h"; startup_candle_count=48
    minimal_roi={"0":100.0}; stoploss=-0.99; trailing_stop=True; trailing_stop_positive=0.02; use_exit_signal=False
    lookback=48; breakout_threshold=0.008; volume_surge_mult=1.0; max_hold_bars=72
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d["period_high"]=d.high.rolling(self.lookback).max(); d["period_low"]=d.low.rolling(self.lookback).min(); d["avg_vol"]=d.volume.rolling(self.lookback).mean(); return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        vol=d.volume>d.avg_vol*self.volume_surge_mult
        d.loc[(((d.close-d.period_high)/d.period_high)>self.breakout_threshold)&vol,"enter_long"]=1
        d.loc[(((d.period_low-d.close)/d.period_low)>self.breakout_threshold)&vol,"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:return d
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if (current_time-trade.open_date_utc).total_seconds()>self.max_hold_bars*3600:return "max_hold"

