"""FMZ 427516: preserve user state booleans and fib_100=1/100 (NOT 100%)."""
from freqtrade.strategy import IStrategy
from sm_event import EventStrategyBase
from sm_indicators import sma,stdev,source_column,highest,lowest,crossover,crossunder


class SMBollingerFibonacci(EventStrategyBase,IStrategy):
    execution_backend='pine_compat'
    timeframe='45m'
    can_short=True
    source_defaults={'length':20,'src':'close','mult':2.0,'fib_0':0.0,'fib_100':1.0}

    def prepare_source(self,df,p):
        if not (-100<=p['fib_0']<=100 and -100<=p['fib_100']<=100):raise ValueError('Fibonacci input outside source range')
        src=source_column(df,p['src']);df['basis']=sma(src,p['length']);dev=p['mult']*stdev(src,p['length'])
        df['upper_band']=df.basis+dev;df['lower_band']=df.basis-dev
        hi=highest(df.high,50);lo=lowest(df.low,50);span=hi-lo
        df['fib_high']=hi-span*p['fib_0']/100;df['fib_low']=lo+span*p['fib_100']/100
        df['long_condition']=crossover(df.close,df.upper_band)&(df.low>df.fib_low)
        df['short_condition']=crossunder(df.close,df.lower_band)&(df.high<df.fib_high)
        df['long_exit_condition']=crossunder(df.close,df.basis)
        df['short_exit_condition']=crossover(df.close,df.basis)
        return df

    def source_on_bar(self,bar,b,state,p):
        state.setdefault('long_position',False);state.setdefault('short_position',False)
        if bar.long_condition and not state['short_position']:
            b.entry('Long',1);state['long_position']=True;state['short_position']=False
        if bar.short_condition and not state['long_position']:
            b.entry('Short',-1);state['short_position']=True;state['long_position']=False
        if bar.long_exit_condition:b.close('Long');state['long_position']=False
        if bar.short_exit_condition:b.close('Short');state['short_position']=False
