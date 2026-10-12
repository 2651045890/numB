"""Deep port of the Negroni MA & RSI strategy.

All active/default risk branches are implemented.  The only structural gap is
request.security() for the fixed daily MA: this offline port cannot synthesize
a second timeframe and therefore evaluates fixedMA1 on the supplied bars.
"""
import math
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

def _hma(s,n):
    n=max(1,int(n)); return ta.pine_wma(2*ta.pine_wma(s,max(1,n//2))-ta.pine_wma(s,n),max(1,int(round(math.sqrt(n)))))

def _ma(kind,s,n,volume=None):
    if kind=='EMA': return ta.pine_ema(s,n)
    if kind=='SMA': return ta.pine_sma(s,n)
    if kind=='VWMA':
        x=s.copy(); x.attrs['volume']=volume; return ta.pine_vwma(x,n)
    return _hma(s,n)

class SMB010_004_NegroniMA_RSI(PinePortBase, IStrategy):
    timeframe='12h'; can_short=True
    source_file='移动均线交叉系统交易策略Moving-Average-Trading-Strategy.md'
    source_defaults={"s1":True,"s2":False,"v1":False,"v2":False,"v3":True,
        "v2stoploss_input":0.025,"v2takeprofit_input":0.03,"atrLength":50,"v3stoploss_input":2.0,"v3takeprofit_input":2.5,
        "rsiLength":14,"rsiBuyLevel":55,"rsiSellLevel":45,"fastMAtype":"EMA","maFastLength":13,
        "trendMAtype":"EMA","maTrendLength":32,"slowMAtype":"EMA","maSlowLength":64,
        "fixedMA1type":"EMA","ema1FixLength":100}
    source_qty_type='percent_of_equity'; source_qty_value=3.0; source_initial_capital=100000.0
    source_pyramiding=3; source_commission_percent=0.0; source_reproduce_stops=True
    source_fidelity_notes=["DOMINANT GAP: request.security(...,'D',fixedMA1) is evaluated on strategy bars; no resampling is available.",
        "Default configuration activates only Retest + ATR risk branch (s1=True,v3=True). v1/v2 and breakout branch are still implemented.",
        "The source's guards for v2/v3 contain duplicated trendMA > slowMA checks; preserved exactly (fastMA is not part of those guards)."]
    def pine_indicators(self,d,p):
        c,v=d['close'],d['volume']
        fast=_ma(p['fastMAtype'],c,int(p['maFastLength']),v)
        trend=_ma(p['trendMAtype'],c,int(p['maTrendLength']),v)
        slow=_ma(p['slowMAtype'],c,int(p['maSlowLength']),v)
        fixed=_ma(p['fixedMA1type'],c,int(p['ema1FixLength']),v)
        rsi=ta.pine_rsi(c,int(p['rsiLength'])); atr=ta.pine_atr(d,int(p['atrLength']))
        cross_dn=ta.pine_crossunder(c,fast); cross_up=ta.pine_crossover(c,fast)
        close_long=ta.pine_crossunder(d['low'],fast); close_short=ta.pine_crossover(d['high'],fast)
        guard1L=(fast>trend)&(trend>slow); guard1S=(fast<trend)&(trend<slow)
        guard23L=(trend>slow)&(trend>slow); guard23S=(trend<slow)&(trend<slow)
        commonL=(c>fixed)&(rsi>int(p['rsiBuyLevel'])); commonS=(c<fixed)&(rsi<int(p['rsiSellLevel']))
        d['pine_retest1L']=cross_dn&guard1L&commonL; d['pine_retest1S']=cross_up&guard1S&commonS
        d['pine_break1L']=cross_up&guard1L&commonL; d['pine_break1S']=cross_dn&guard1S&commonS
        d['pine_retest23L']=cross_dn&guard23L&commonL; d['pine_retest23S']=cross_up&guard23S&commonS
        d['pine_break23L']=cross_up&guard23L&commonL; d['pine_break23S']=cross_dn&guard23S&commonS
        d['pine_closeL']=close_long; d['pine_closeS']=close_short; d['pine_atr']=atr
        return d
    def pine_context(self,d,p):
        keys=['retest1L','retest1S','break1L','break1S','retest23L','retest23S','break23L','break23S','closeL','closeS']
        x={k:d['pine_'+k].to_numpy(bool) for k in keys}; x['atr']=d['pine_atr'].to_numpy(float); x['p']=p; return x
    def pine_script(self,b,i,x):
        p=x['p']; avg=b.position_avg_price; atr=x['atr'][i]
        if p['s1'] and p['v1']:
            b.entry("Strat 1 'Retest' Long",'long',when=x['retest1L'][i]); b.close("Strat 1 'Retest' Long",when=x['closeL'][i])
            b.entry("Strat 1 'Retest' Short",'short',when=x['retest1S'][i]); b.close("Strat 1 'Retest' Short",when=x['closeS'][i])
        if p['s2'] and p['v1']:
            b.entry("Strat 1 'Breakout' Long",'long',when=x['break1L'][i]); b.close("Strat 1 'Breakout' Long",when=x['closeL'][i])
            b.entry("Strat 1 'Breakout' Short",'short',when=x['break1S'][i]); b.close("Strat 1 'Breakout' Short",when=x['closeS'][i])
        for tag,on,sigL,sigS in [('Retest',p['s1'],'retest23L','retest23S'),('Breakout',p['s2'],'break23L','break23S')]:
            if on and p['v2']:
                if x[sigL][i]: b.entry(f'Strat 2 {tag} Long','long')
                if x[sigS][i]: b.entry(f'Strat 2 {tag} Short','short')
                if b.position_size>0: b.exit(f'SL/TP Strat 2 {tag} long',f'Strat 2 {tag} Long',stop=avg*(1-p['v2stoploss_input']),limit=avg*(1+p['v2takeprofit_input']))
                if b.position_size<0: b.exit(f'SL/TP Strat 2 {tag} short',f'Strat 2 {tag} Short',stop=avg*(1+p['v2stoploss_input']),limit=avg*(1-p['v2takeprofit_input']))
            if on and p['v3']:
                if x[sigL][i]: b.entry(f'Strat 3 {tag} Long','long')
                if x[sigS][i]: b.entry(f'Strat 3 {tag} Short','short')
                if b.position_size>0: b.exit(f'SL/TP Strat 3 {tag} long',f'Strat 3 {tag} Long',stop=avg-p['v3stoploss_input']*atr,limit=avg+p['v3takeprofit_input']*atr)
                if b.position_size<0: b.exit(f'SL/TP Strat 3 {tag} short',f'Strat 3 {tag} Short',stop=avg+p['v3stoploss_input']*atr,limit=avg-p['v3takeprofit_input']*atr)
