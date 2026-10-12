"""Deep Pine v4 port. Note the source nests BOTH close calls inside the short-condition block."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_005_GaanEMA(PinePortBase, IStrategy):
    timeframe='2m'; can_short=True; source_file='浪速EMA黄金交叉策略Gaan-EMA-Golden-Cross-Strategy.md'
    source_defaults={}; source_qty_type='fixed'; source_qty_value=1.0; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["Long/short are regime conditions, not EMA cross events.","strategy.close(long/short) executes only while the SHORT entry condition is true because of source indentation; preserved."]
    def pine_indicators(self,d,p):
        c=d['close']; e9=ta.pine_ema(c,9); e27=ta.pine_ema(c,27); e81=ta.pine_ema(c,81)
        d['pine_long']=(e27>e81)&(c>e9); d['pine_short']=(e27<e81)&(c<e9); d['pine_lx']=c<e9; d['pine_sx']=c>e9; return d
    def pine_context(self,d,p): return {k:d['pine_'+k].to_numpy(bool) for k in ['long','short','lx','sx']}
    def pine_script(self,b,i,x):
        if x['long'][i]: b.entry('long','long')
        if x['short'][i]:
            b.entry('short','short'); b.close('long',when=x['lx'][i]); b.close('short',when=x['sx'][i])
