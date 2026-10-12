"""FMZ 474810: source backtest period is 1d despite 4H in the title."""
from freqtrade.strategy import IStrategy
from sm_event import EventStrategyBase
from sm_indicators import sma,stdev


class SMBollinger4HFollow(EventStrategyBase,IStrategy):
    execution_backend='pine_compat'
    timeframe='1d'
    can_short=True
    source_defaults={'length':20,'mult':2.0,'lev':3.0}
    declared_settings={'initial_capital':300.0,'commission_percent':0.04}

    def prepare_source(self,df,p):
        df['basis']=sma(df.close,p['length']);dev=p['mult']*stdev(df.close,p['length'])
        df['upperBand']=df.basis+dev;df['lowerBand']=df.basis-dev
        return df

    def source_on_bar(self,bar,b,state,p):
        # Pine evaluates these four variables before creating any of the orders.
        flat=b.position_size==0
        open_long=flat and bar.close>bar.open and (bar.close+bar.open)/2>bar.upperBand
        open_short=flat and bar.close<bar.open and (bar.close+bar.open)/2<bar.lowerBand
        close_long=b.position_size>0 and bar.close<bar.upperBand and bar.open<bar.upperBand and bar.close<bar.open
        close_short=b.position_size<0 and bar.close>bar.lowerBand and bar.open>bar.lowerBand and bar.close>bar.open
        if open_long:
            b.entry('Long',1,qty=b.equity*p['lev']/bar.close)
            b.exit('Long SL','Long',stop=bar.low)
        if open_short:
            b.entry('Short',-1,qty=b.equity*p['lev']/bar.close)
            b.exit('Short SL','Short',stop=bar.high)
        if close_long:b.close('Long')
        if close_short:b.close('Short')
