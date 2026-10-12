"""Helpers for explicitly reviewed market-only long/flat Pine ports, not a translator."""
import numpy as np
from pandas import Series
# From the shared primitives, not from a port's module: a port's file is named
# after its source and re-filed whenever the corpus is regrouped, so importing
# one by module name couples this helper to the layout. Verified identical to
# the copy that lived beside the 1-2-3 Pattern port over 6 lengths x 5
# densities of na, index, dtype and bad-length rejection.
from pine_ta import pine_ema


def sma(source, length):
    if isinstance(length,bool) or int(length)!=length or length<1:
        raise ValueError('SMA length must be a positive integer')
    # Pine's length counts non-na observations, not elapsed bars.
    valid=source.dropna().rolling(int(length),min_periods=int(length)).mean()
    return valid.reindex(source.index).ffill()


def crossover(a,b):
    return (a>b) & (a.shift(1)<=b.shift(1))


def crossunder(a,b):
    return (a<b) & (a.shift(1)>=b.shift(1))


def long_flat(dataframe, buy, sell, quantity, entry_id):
    position=0
    pending=None
    rows=[]
    for enter,exit_ in zip(buy,sell):
        if pending is not None: position=pending
        pending=None
        el=xl=0
        if position==0 and enter:
            el,pending=1,1
        elif position==1 and exit_:
            xl,pending=1,0
        rows.append((el,0,xl,0,position*quantity,entry_id if el else 'close '+entry_id if xl else ''))
    for i,key in enumerate(('enter_long','enter_short','exit_long','exit_short','source_position','source_order')):
        dataframe[key]=[row[i] for row in rows]
    return dataframe
