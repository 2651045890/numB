"""Deep port of Bozz Strategy v1.1.
The source has its strategy() declaration commented out; this port uses the
settings written in that comment because the remaining code is explicitly
strategy.* code and otherwise would not compile as a TradingView strategy.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_006_BozzSwing(PinePortBase, IStrategy):
    timeframe='2h'; can_short=True; source_file='摆动交易策略Swing-Trading-Strategy.md'
    source_defaults={"source_ma_type":"EMA","source_ma_length":50,"fast_ma_length":20,"slow_ma_length":50,"use_trend_filter":True,"trend_filter_ma_type":"EMA","trend_filter_ma_length":200,"swing_trading_mode":False,"sl_perc":0.01,"tp_perc":0.01,"leverage":10}
    source_qty_type='percent_of_equity'; source_qty_value=100.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=True
    source_fidelity_notes=["The strategy() line is commented out in source. Its declared percent-of-equity defaults are treated as author intent; trade_qty is dead code and never passed to entry.","in_trading_window is literally true in source; bt_start_time/bt_end_time inputs are dead code."]
    def pine_indicators(self,d,p):
        c=d['close']; fast=ta.pine_ema(c,int(p['fast_ma_length'])); slow=ta.pine_ema(c,int(p['slow_ma_length']))
        tf=ta.pine_ema(c,int(p['trend_filter_ma_length'])) if p['trend_filter_ma_type']=='EMA' else ta.pine_sma(c,int(p['trend_filter_ma_length']))
        d['pine_buy']=ta.pine_crossover(fast,slow)&((c>tf) if p['use_trend_filter'] else True)
        d['pine_sell']=ta.pine_crossunder(fast,slow)&((c<tf) if p['use_trend_filter'] else True); return d
    def pine_context(self,d,p): return {'buy':d['pine_buy'].to_numpy(bool),'sell':d['pine_sell'].to_numpy(bool),'p':p}
    def pine_script(self,b,i,x):
        p=x['p']; b.entry('Long Entry','long',when=x['buy'][i]); b.entry('Short Entry','short',when=x['sell'][i])
        if not p['swing_trading_mode'] and b.position_size>0:
            a=b.position_avg_price; b.exit('Long Exit','Long Entry',limit=a*(1+p['tp_perc']),stop=a*(1-p['sl_perc']))
        if not p['swing_trading_mode'] and b.position_size<0:
            a=b.position_avg_price; b.exit('Short Exit','Short Entry',limit=a*(1-p['tp_perc']),stop=a*(1+p['sl_perc']))
