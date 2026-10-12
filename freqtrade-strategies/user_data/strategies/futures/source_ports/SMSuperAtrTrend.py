"""FMZ 442096: literal Super ATR bands and trend state; no artificial ATR stop."""
import math
from freqtrade.strategy import IStrategy
from sm_event import EventStrategyBase
from sm_indicators import atr,tr,sma,source_column,date_window


class SMSuperAtrTrend(EventStrategyBase,IStrategy):
    execution_backend='pine_compat'
    timeframe='1d'
    can_short=True
    source_defaults=dict(Periods=10,src='hl2',Multiplier=3.0,changeATR=True,showsignals=False,
        FromMonth=9,FromDay=1,FromYear=2018,ToMonth=1,ToDay=1,ToYear=9999)

    def prepare_source(self,df,p):
        df['atr2']=sma(tr(df),p['Periods'])
        df['atr']=atr(df,p['Periods']) if p['changeATR'] else df.atr2
        src=source_column(df,p['src'])
        raw_up=src-p['Multiplier']*df.atr;raw_dn=src+p['Multiplier']*df.atr
        previous_up=previous_dn=previous_close=math.nan;previous_trend=None
        ups=[];dns=[];trends=[];buys=[];sells=[]
        for close,up,dn in zip(df.close,raw_up,raw_dn):
            up1=up if math.isnan(previous_up) else previous_up
            dn1=dn if math.isnan(previous_dn) else previous_dn
            up=max(up,up1) if previous_close>up1 else up
            dn=min(dn,dn1) if previous_close<dn1 else dn
            trend=1 if previous_trend is None else previous_trend
            trend=1 if trend==-1 and close>dn1 else -1 if trend==1 and close<up1 else trend
            buys.append(trend==1 and previous_trend==-1);sells.append(trend==-1 and previous_trend==1)
            ups.append(up);dns.append(dn);trends.append(trend)
            previous_up,previous_dn,previous_close,previous_trend=up,dn,close,trend
        df['up']=ups;df['dn']=dns;df['trend']=trends
        df['buySignal']=buys;df['sellSignal']=sells
        df['window']=date_window(df.date,(p['FromYear'],p['FromMonth'],p['FromDay'],0,0),
            (p['ToYear'],p['ToMonth'],p['ToDay'],23,59),self.config.get('source_timezone','UTC'))
        return df

    def source_on_bar(self,bar,b,state,p):
        if bar.buySignal and bar.window:b.entry('BUY',1)
        if bar.sellSignal and bar.window:b.entry('SAL',-1)
