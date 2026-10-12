"""Explicit Pine-style indicator primitives for individually reviewed ports."""
import math
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
from pandas import Series
from pine_ta import pine_ema as ema
from sm_long_compat import sma, crossover, crossunder


def length_value(length):
    if isinstance(length,bool) or int(length)!=length or length<1:raise ValueError('Length must be a positive integer')
    return int(length)


def rma(source,length):
    length=length_value(length);seed=[];state=math.nan;values=[]
    for x in source:
        if not math.isnan(x):
            if math.isnan(state):
                seed.append(x)
                if len(seed)==length:state=sum(seed)/length
            else:state=x/length+(1-1/length)*state
        values.append(state)
    return Series(values,index=source.index,dtype=float)


def tr(df,handle_na=False):
    previous=df.close.shift(1)
    value=(df.high-df.low).combine((df.high-previous).abs(),np.maximum).combine((df.low-previous).abs(),np.maximum)
    if handle_na:value=value.where(previous.notna(),df.high-df.low)
    return value


def atr(df,length):return rma(tr(df,True),length)


def stdev(source,length):
    length=length_value(length)
    valid=source.dropna().rolling(length,min_periods=length).std(ddof=0)
    return valid.reindex(source.index).ffill()


def highest(source,length):return source.rolling(length_value(length),min_periods=1).max()
def lowest(source,length):return source.rolling(length_value(length),min_periods=1).min()


def source_column(df,name):
    if name in ('open','high','low','close','volume'):return df[name]
    if name=='hl2':return (df.high+df.low)/2
    if name=='hlc3':return (df.high+df.low+df.close)/3
    if name=='ohlc4':return (df.open+df.high+df.low+df.close)/4
    if name=='hlcc4':return (df.high+df.low+df.close*2)/4
    raise ValueError('Unsupported data source '+str(name))


def date_window(dates,start,end,timezone='UTC',inclusive=True):
    # Python datetime supports source's ToYear=9999; avoid pandas ns overflow.
    zone=ZoneInfo(timezone)
    lower=datetime(*start,tzinfo=zone);upper=datetime(*end,tzinfo=zone)
    return Series([(lower<=t.to_pydatetime()<=upper) if inclusive else
                   (lower<t.to_pydatetime()<upper) for t in dates],index=dates.index)
