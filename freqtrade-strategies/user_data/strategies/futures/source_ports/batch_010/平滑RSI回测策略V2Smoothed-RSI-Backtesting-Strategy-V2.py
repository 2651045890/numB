"""Deep Pine v2 port of Ehlers-style smoothed RSI backtest."""
import numpy as np
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
class SMB010_020_SmoothedRSI(PinePortBase, IStrategy):
    timeframe='30m'; can_short=True; source_file='平滑RSI回测策略V2Smoothed-RSI-Backtesting-Strategy-V2.md'
    source_defaults={"Length":10,"TopBand":0.8,"LowBand":0.2,"reverse":False}; source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["nRes is a 0..1 ratio, not conventional 0..100 RSI.","pos is sticky between thresholds and is reversed only by the reverse input; exact recurrence reproduced."]
    def pine_indicators(self,d,p):
        c=d['close']; x=(c+2*c.shift(1)+2*c.shift(2)+c.shift(3))/6.; delta=x-x.shift(1); up=delta.where(delta>0,0.0).rolling(int(p['Length']),min_periods=int(p['Length'])).sum(); dn=(-delta.where(delta<0,0.0)).rolling(int(p['Length']),min_periods=int(p['Length'])).sum(); den=up+dn; r=(up/den).where(den!=0,0.0)
        state=[]; prev=0
        for v in r:
            if v>float(p['TopBand']): prev=1
            elif v<float(p['LowBand']): prev=-1
            state.append(prev)
        arr=np.asarray(state,dtype=int); arr=-arr if p['reverse'] else arr; d['pine_pos']=arr; d['pine_rsi']=r; return d
    def pine_context(self,d,p): return {'p':d['pine_pos'].to_numpy(int)}
    def pine_script(self,b,i,x):
        if x['p'][i]==1: b.entry('Long','long')
        if x['p'][i]==-1: b.entry('Short','short')
