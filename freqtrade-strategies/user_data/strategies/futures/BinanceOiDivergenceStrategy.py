# SEMANTIC-PRESERVING FREQTRADE PORT
# Source: Gotodataru/binance-futures-backtest@5ed0d6e39d8a3e951bea40c66e2638c213012e1b
from pandas import DataFrame
from freqtrade.strategy import IStrategy
from binance_futures_metrics import merge_aux

class BinanceOiDivergenceStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="15m"; startup_candle_count=18
    minimal_roi={"0":100.0}; stoploss=-0.99; use_exit_signal=False
    lookback_bars=12; price_thresh=0.005; oi_thresh=0.01; hold_bars=16; use_mr=1
    def populate_indicators(self,d:DataFrame,metadata:dict)->DataFrame:
        d=merge_aux(d,metadata["pair"],self.timeframe)
        d["price_chg"]=d.close.pct_change(self.lookback_bars).shift(1)
        d["oi_chg"]=d.open_interest.ffill().pct_change(self.lookback_bars).shift(1)
        d["ls_lag"]=d.taker_ls_vol_ratio.ffill().shift(1); return d
    def populate_entry_trend(self,d:DataFrame,metadata:dict)->DataFrame:
        pu=d.price_chg>self.price_thresh; pdn=d.price_chg < -self.price_thresh
        ou=d.oi_chg>self.oi_thresh; odn=d.oi_chg < -self.oi_thresh
        long=(pu&ou&(d.ls_lag>1.0))|(pdn&odn)
        short=(pdn&ou&(d.ls_lag<1.0))|(pu&odn)
        d.loc[long,"enter_long"]=1; d.loc[short,"enter_short"]=1; return d
    def populate_exit_trend(self,d:DataFrame,metadata:dict)->DataFrame:return d
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if (current_time-trade.open_date_utc).total_seconds()>=self.hold_bars*15*60:return "hold_bars"
