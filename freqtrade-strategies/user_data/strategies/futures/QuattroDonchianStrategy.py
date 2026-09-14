# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/EstebanSP23/crypto_systematic_research
# Original commit: d722857a70331f9605481ef8f32df85b990d351d
# Original files: 2_strategies/01_quattro_donchian/backtest.py
# Original market: BTC perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
from datetime import datetime
import pandas as pd
from pandas import DataFrame
from freqtrade.persistence import Order, Trade
from freqtrade.strategy import IStrategy, merge_informative_pair, stoploss_from_absolute

class QuattroDonchianStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=False; timeframe="4h"; startup_candle_count=250
    position_adjustment_enable=True; max_entry_position_adjustment=3
    minimal_roi={"0":100.0}; stoploss=-0.99; use_custom_stoploss=True; use_exit_signal=True
    risk_pct=.02; hard_stop_pct=.05; atr_mult_stop=2.0; pyramid_step=.5; max_units=4; max_strategy_leverage=20.0

    def informative_pairs(self): return [(p,"1d") for p in self.dp.current_whitelist()]
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d["donch_high_20"]=d.high.rolling(20).max().shift(1); d["donch_low_10"]=d.low.rolling(10).min().shift(1)
        pc=d.close.shift(1); tr=pd.concat([d.high-d.low,(d.high-pc).abs(),(d.low-pc).abs()],axis=1).max(axis=1)
        d["atr14"]=tr.ewm(alpha=1/14,adjust=False).mean()
        daily=self.dp.get_pair_dataframe(pair=metadata["pair"],timeframe="1d")
        if not daily.empty:
            daily=daily.copy(); daily["ema200"]=daily.close.ewm(span=200,adjust=False).mean()
            d=merge_informative_pair(d,daily[["date","ema200"]],self.timeframe,"1d",ffill=True)
        else:d["ema200_1d"]=float("nan")
        d["regime_up"]=d.close>d.ema200_1d; return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[(d.close>d.donch_high_20)&d.regime_up&(d.volume>0),["enter_long","enter_tag"]]=(1,"donchian20")
        return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        d.loc[d.close<d.donch_low_10,["exit_long","exit_tag"]]=(1,"donchian10"); return d
    def leverage(self,pair,current_time,current_rate,proposed_leverage,max_leverage,entry_tag,side,**kwargs): return min(self.max_strategy_leverage,max_leverage)
    def custom_stake_amount(self,pair,current_time,current_rate,proposed_stake,min_stake,max_stake,leverage,entry_tag,side,**kwargs):
        d,_=self.dp.get_analyzed_dataframe(pair,self.timeframe)
        if d.empty or not d.iloc[-1].atr14>0:return 0
        equity=self.wallets.get_total_stake_amount(); notional=equity*self.risk_pct*current_rate/(2*d.iloc[-1].atr14)
        return max(min_stake or 0,min(max_stake,notional/leverage))
    def order_filled(self,pair:str,trade:Trade,order:Order,current_time:datetime,**kwargs):
        if order.ft_order_side==trade.entry_side and trade.nr_of_successful_entries==1:
            d,_=self.dp.get_analyzed_dataframe(pair,self.timeframe); row=d.iloc[-1]
            trade.set_custom_data("original_atr",float(row.atr14)); trade.set_custom_data("original_entry",float(order.safe_price)); trade.set_custom_data("acct_at_entry",float(self.wallets.get_total_stake_amount()))
    def adjust_trade_position(self,trade:Trade,current_time:datetime,current_rate:float,current_profit:float,min_stake,max_stake,current_entry_rate,current_exit_rate,current_entry_profit,current_exit_profit,**kwargs):
        n=trade.get_custom_data("original_atr"); origin=trade.get_custom_data("original_entry")
        if not n or not origin or trade.nr_of_successful_entries>=self.max_units:return None
        trigger=origin+self.pyramid_step*trade.nr_of_successful_entries*n
        if current_rate<trigger:return None
        equity=trade.get_custom_data("acct_at_entry") or self.wallets.get_total_stake_amount(); notional=equity*self.risk_pct*trigger/(2*n)
        return min(max_stake,notional/trade.leverage),f"unit_{trade.nr_of_successful_entries+1}"
    def custom_stoploss(self,pair,trade:Trade,current_time,current_rate,current_profit,after_fill,**kwargs):
        n=trade.get_custom_data("original_atr"); origin=trade.get_custom_data("original_entry")
        if not n or not origin:return self.stoploss
        newest=origin+self.pyramid_step*(trade.nr_of_successful_entries-1)*n; atr_stop=newest-2*n
        acct=trade.get_custom_data("acct_at_entry") or 0; hard=trade.open_rate-(self.hard_stop_pct*acct/max(trade.amount,1e-12))
        return stoploss_from_absolute(max(atr_stop,hard),current_rate,is_short=False,leverage=trade.leverage)
