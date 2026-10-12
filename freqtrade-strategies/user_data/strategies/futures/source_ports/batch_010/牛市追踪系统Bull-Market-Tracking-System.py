"""Deep Pine v4 port of the Cowabunga system."""
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

def _stoch(c,h,l,n):
    lo=ta.pine_lowest(l,n); hi=ta.pine_highest(h,n); den=hi-lo; return 100*(c-lo)/den
class SMB010_013_Cowabunga(PinePortBase, IStrategy):
    timeframe='1h'; can_short=True; source_file='牛市追踪系统Bull-Market-Tracking-System.md'
    source_defaults={"length4":162,"smoothK4":48,"smoothD4":48,"length":10,"smoothK":3,"smoothD":3,"len1":240,"len":9,"fastLength":12,"slowLength":26,"signalLength":9,"inpTakeProfit":1000,"inpStopLoss":0,"inpTrailStop":400,"inpTrailOffset":0,"session":"0500-1600"}
    source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=True
    source_fidelity_notes=["The so-called 4H/15M indicators are not request.security calls; they are large/small lookbacks on the chart timeframe and are reproduced literally.","Session 0500-1600 is interpreted in UTC for Binance. TradingView uses the symbol exchange timezone; Binance symbols are normally UTC.","profit/loss/trail_points/trail_offset are Pine tick distances. trail_offset default 0 is converted to na by source; profit=1000 remains active."]
    def pine_indicators(self,d,p):
        c,h,l=d['close'],d['high'],d['low']; k4=ta.pine_sma(_stoch(c,h,l,int(p['length4'])),int(p['smoothK4'])); d4=ta.pine_sma(k4,int(p['smoothD4']))
        k=ta.pine_sma(_stoch(c,h,l,int(p['length'])),int(p['smoothK'])); dd=ta.pine_sma(k,int(p['smoothD']))
        r4=ta.pine_rsi(c,int(p['len1'])); r15=ta.pine_rsi(c,int(p['len'])); e80=ta.pine_ema(c,80); e162=ta.pine_ema(c,162); e5=ta.pine_ema(c,5); e10=ta.pine_ema(c,10); fast=ta.pine_ema(c,int(p['fastLength'])); slow=ta.pine_ema(c,int(p['slowLength']))
        if 'date' in d:
            t=pd.to_datetime(d['date'],utc=True); mins=t.dt.hour*60+t.dt.minute; session=(mins>=300)&(mins<960)
        else: session=True
        L=session&(r4<=80)&(k4>=d4)&(k4<=80)&(e80>=e162)&(r15<=80)&(k>=dd)&(k<=80)&(fast>=slow)&(e5>=e10)&ta.pine_crossover(c,e5)
        S=session&(r4>=20)&(k4<=d4)&(k4>=20)&(e80<=e162)&(r15>=20)&(k<=dd)&(k>=20)&(fast<=slow)&(e5<=e10)&ta.pine_crossunder(c,e5)
        d['pine_L']=L; d['pine_S']=S; return d
    def pine_context(self,d,p): return {'L':d['pine_L'].to_numpy(bool),'S':d['pine_S'].to_numpy(bool),'p':p}
    def pine_script(self,b,i,x):
        if x['L'][i]: b.entry('Long','long')
        if x['S'][i]: b.entry('Short','short')
        p=x['p']; tp=p['inpTakeProfit'] if p['inpTakeProfit']>=1 else None; sl=p['inpStopLoss'] if p['inpStopLoss']>=1 else None; tr=p['inpTrailStop'] if p['inpTrailStop']>=1 else None; off=p['inpTrailOffset'] if p['inpTrailOffset']>=1 else None
        b.exit('Exit Long','Long',profit=tp,loss=sl,trail_points=tr,trail_offset=off); b.exit('Exit Short','Short',profit=tp,loss=sl,trail_points=tr,trail_offset=off)
