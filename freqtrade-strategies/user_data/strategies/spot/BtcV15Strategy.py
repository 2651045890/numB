# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/s9213712/BTC_trade
# Original commit: dde7c76d073e7941fbc8ea7fb54b35cf54a04a2d
# Original files: hourly_check.py, lib/indicators.py, lib/ml_filter.py, lib/state.py
# Original market: BTC/USDT spot
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
from datetime import datetime
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.persistence import Trade
from freqtrade.strategy import IStrategy, stoploss_from_absolute

class BtcV15Strategy(IStrategy):
    INTERFACE_VERSION=3; can_short=False; timeframe="1h"; startup_candle_count=210
    position_adjustment_enable=True; max_entry_position_adjustment=0
    minimal_roi={"0":100.0}; stoploss=-0.99; use_custom_stoploss=True; use_exit_signal=False
    half_tp=.10; half_ratio=.33; full_tp=.20; sl_atr=1.0; trail_start=.05; trail_dist=.03; max_hold=120; invest_ratio=.95
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d["ma20"]=d.close.rolling(20).mean(); d["ma50"]=d.close.rolling(50).mean(); d["ma200"]=d.close.rolling(200).mean()
        e12=d.close.ewm(span=12).mean(); e26=d.close.ewm(span=26).mean(); d["macd"]=e12-e26
        delta=d.close.diff(); gain=delta.where(delta>0,0).rolling(14).mean(); loss=(-delta.where(delta<0,0)).rolling(14).mean(); d["rsi"]=100-(100/(1+gain/(loss+1e-9)))
        pc=d.close.shift(); tr=pd.concat([d.high-d.low,(d.high-pc).abs(),(d.low-pc).abs()],axis=1).max(axis=1); d["atr"]=tr.rolling(14).mean()
        d["mom5"]=d.close.pct_change(5); d["vol_ma"]=d.volume.rolling(20).mean(); d["price_vs_ma20"]=(d.close-d.ma20)/(d.ma20+1e-9)
        d["ma50_slope"]=d.ma50.pct_change(5,fill_method=None); d["ma200_slope"]=d.ma200.pct_change(5,fill_method=None); return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        cond=(d.ma50_slope>0)&(d.macd>0)&d.price_vs_ma20.between(-.05,.01,inclusive="both")&(d.mom5<0)&d.rsi.between(40,70,inclusive="both")&(d.ma200_slope>0)&(d.volume<d.vol_ma)
        d.loc[cond,["enter_long","enter_tag"]]=(1,"v15_seven_conditions"); return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:return d
    def custom_stake_amount(self,pair,current_time,current_rate,proposed_stake,min_stake,max_stake,leverage,entry_tag,side,**kwargs): return min(max_stake,proposed_stake*self.invest_ratio)
    def adjust_trade_position(self,trade:Trade,current_time:datetime,current_rate:float,current_profit:float,min_stake,max_stake,current_entry_rate,current_exit_rate,current_entry_profit,current_exit_profit,**kwargs):
        if current_profit>=self.half_tp and trade.nr_of_successful_exits==0:return -(trade.stake_amount*self.half_ratio),"first_third_tp"
        return None
    def custom_stoploss(self,pair,trade:Trade,current_time,current_rate,current_profit,after_fill,**kwargs):
        d,_=self.dp.get_analyzed_dataframe(pair,self.timeframe)
        if d.empty or not np.isfinite(d.iloc[-1].atr):return self.stoploss
        return stoploss_from_absolute(trade.open_rate-float(d.iloc[-1].atr)*self.sl_atr,current_rate,is_short=False,leverage=trade.leverage)
    def custom_exit(self,pair,trade:Trade,current_time,current_rate,current_profit,**kwargs):
        if current_profit>=self.full_tp:return "FULL_TP"
        peak=max(float(trade.max_rate or current_rate),current_rate)
        if current_profit>self.trail_start and (peak-current_rate)/peak>=self.trail_dist:return "TRAIL_STOP"
        if (current_time-trade.open_date_utc).total_seconds()>=self.max_hold*3600:return "MAX_HOLD"
        return None
