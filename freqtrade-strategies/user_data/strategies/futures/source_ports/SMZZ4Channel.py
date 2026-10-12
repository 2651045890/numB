"""FMZ 427450 / Noro 2019: persistent channel turns, equity lots, stop orders."""
import math
from freqtrade.strategy import IStrategy
from sm_event import EventStrategyBase
from sm_indicators import source_column,highest,lowest,date_window


class SMZZ4Channel(EventStrategyBase,IStrategy):
    execution_backend='pine_compat'
    timeframe='1d'
    can_short=True
    declared_settings={'default_qty_type':'percent_of_equity','default_qty_value':100.0}
    source_defaults=dict(needlong=True,needshort=True,capital=100,len=7,showll=True,showbg=False,showpc=False,
        fromyear=1900,toyear=2100,frommonth=1,tomonth=12,fromday=1,today=31)

    def prepare_source(self,df,p):
        src=source_column(df,'ohlc4');df['h']=highest(src,p['len']);df['l']=lowest(src,p['len'])
        old_h=old_l=old_mh=old_ml=hl=ll=math.nan
        hls=[];lls=[];mhs=[];mls=[]
        for h,l in zip(df.h,df.l):
            ml=1 if l>old_l else -1 if l<old_l else old_ml
            ll=old_l if ml==1 and old_ml==-1 else ll
            mh=1 if h>old_h else -1 if h<old_h else old_mh
            hl=old_h if mh==-1 and old_mh==1 else hl
            hls.append(hl);lls.append(ll);mhs.append(mh);mls.append(ml)
            old_h,old_l,old_mh,old_ml=h,l,mh,ml
        df['hl']=hls;df['ll']=lls;df['mh']=mhs;df['ml']=mls
        start=(p['fromyear'],p['frommonth'],p['fromday'],0,0)
        end=(p['toyear'],p['tomonth'],p['today'],23,59)
        timezone=self.config.get('source_timezone','UTC')
        df['truetime']=date_window(df.date,start,end,timezone,inclusive=False)
        from datetime import datetime
        from zoneinfo import ZoneInfo
        endtime=datetime(*end,tzinfo=ZoneInfo(timezone))
        df['after_end']=[t.to_pydatetime()>endtime for t in df.date]
        return df

    def source_on_bar(self,bar,b,state,p):
        previous=state.get('size',math.nan);lot=state.get('lot',math.nan)
        # Pine v4 comparison to na is na/false, NOT Python's nan != 0 (True).
        if not math.isnan(previous) and b.position_size!=previous:
            lot=b.equity/bar.close*p['capital']/100
        if bar.ll>0 and bar.hl>0 and bar.truetime:
            b.entry('Long',1,qty=lot if p['needlong'] else 0,stop=bar.hl)
            b.entry('Short',-1,qty=lot if p['needshort'] else 0,stop=bar.ll)
        if bar.after_end:
            b.close_all();b.cancel('Long');b.cancel('Short')
        state['size']=b.position_size;state['lot']=lot
