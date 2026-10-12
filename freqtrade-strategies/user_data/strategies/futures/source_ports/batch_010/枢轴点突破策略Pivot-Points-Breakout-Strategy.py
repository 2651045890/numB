"""Deep Pine v2 port of Floor Pivot Points Backtest.
On the source's 1d chart, request.security(...,'D', high/low/close[1]) is simply
the previous daily bar, so this part is exactly reproducible without resampling.
"""
import numpy as np
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
class SMB010_016_FloorPivot(PinePortBase, IStrategy):
    timeframe='1d'; can_short=True; source_file='枢轴点突破策略Pivot-Points-Breakout-Strategy.md'
    source_defaults={"reverse":False}; source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["Because strategy timeframe equals requested daily timeframe, xHigh/xLow/xClose are previous-bar OHLC exactly.","pos is sticky: it remains previous state while close is between R1 and S1; explicitly reproduced."]
    def pine_indicators(self,d,p):
        h,l,c=d['high'].shift(1),d['low'].shift(1),d['close'].shift(1); pp=(h+l+c)/3; r1=2*pp-l; s1=2*pp-h
        pos=[]; prev=0
        for cc,rr,ss in zip(d['close'],r1,s1):
            if cc>rr: prev=1
            elif cc<ss: prev=-1
            pos.append(prev)
        arr=np.asarray(pos,dtype=int); arr=-arr if p['reverse'] else arr; d['pine_pos']=arr; return d
    def pine_context(self,d,p): return {'p':d['pine_pos'].to_numpy(int)}
    def pine_script(self,b,i,x):
        if x['p'][i]==1: b.entry('Long','long')
        if x['p'][i]==-1: b.entry('Short','short')
