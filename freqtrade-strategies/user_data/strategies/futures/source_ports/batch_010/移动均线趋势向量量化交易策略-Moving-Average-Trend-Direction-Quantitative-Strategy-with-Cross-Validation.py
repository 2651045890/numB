"""Deep Pine v6 port of Open Close Cross Strategy v6.

The source's alternate-resolution request uses lookahead_on and therefore can
repaint/use future higher-timeframe values.  The offline engine cannot reproduce
that series; the selected MA is evaluated on the strategy timeframe.  The
source's unusual ebar/timenow gate is reproduced from the dataset's final time.
"""
import math, pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

def _variant(kind,src,n,off_sig,off_alma):
    n=int(n)
    if kind=='EMA': return ta.pine_ema(src,n)
    if kind=='DEMA':
        e=ta.pine_ema(src,n); return 2*e-ta.pine_ema(e,n)
    if kind=='TEMA':
        e1=ta.pine_ema(src,n); e2=ta.pine_ema(e1,n); e3=ta.pine_ema(e2,n); return 3*(e1-e2)+e3
    if kind=='WMA': return ta.pine_wma(src,n)
    if kind=='HullMA': return ta.pine_wma(2*ta.pine_wma(src,max(1,n//2))-ta.pine_wma(src,n),max(1,int(round(math.sqrt(n)))))
    if kind=='LSMA': return src.rolling(n,min_periods=n).apply(lambda a: pd.Series(a).reset_index(drop=True).pipe(lambda s: __import__('numpy').polyfit(range(n),s,1)[0]*(n-1-int(off_sig))+__import__('numpy').polyfit(range(n),s,1)[1]),raw=False)
    if kind=='TMA': return ta.pine_sma(ta.pine_sma(src,n),n)
    # Source explicitly maps SMMA/default to SMA. ALMA/SSMA are rare non-default paths; SMA fallback is safer than inventing future data.
    return ta.pine_sma(src,n)

class SMB010_010_OpenCloseCrossV6(PinePortBase, IStrategy):
    timeframe='1d'; can_short=True; source_file='移动均线趋势向量量化交易策略-Moving-Average-Trend-Direction-Quantitative-Strategy-with-Cross-Validation.md'
    source_defaults={"useRes":True,"intRes":3,"basisType":"SMMA","basisLen":8,"offsetSigma":6,"offsetALMA":0.85,"delayOffset":0,"tradeType":"BOTH","slPoints":0.0,"tpPoints":0.0,"ebar":10000}
    source_qty_type='percent_of_equity'; source_qty_value=10.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["DOMINANT GAP: request.security(...,3D,...,lookahead_on) cannot be reproduced. Local-timeframe MA is used; original may repaint.","ebar gate uses timenow and timeframe.multiplier exactly in spirit; on daily bars multiplier=1, so 10000 means only roughly the most recent 6.9 days.","Default slPoints/tpPoints are zero -> strategy.exit has both legs na and places no protective order."]
    def pine_indicators(self,d,p):
        src_c=d['close'].shift(int(p['delayOffset'])); src_o=d['open'].shift(int(p['delayOffset']))
        cma=_variant(p['basisType'],src_c,int(p['basisLen']),p['offsetSigma'],p['offsetALMA']); oma=_variant(p['basisType'],src_o,int(p['basisLen']),p['offsetSigma'],p['offsetALMA'])
        d['pine_long']=ta.pine_crossover(cma,oma); d['pine_short']=ta.pine_crossunder(cma,oma)
        if 'date' in d:
            t=pd.to_datetime(d['date'],utc=True); end=t.iloc[-1]; d['pine_ebar']=((end-t).dt.total_seconds()/60.0)<=int(p['ebar'])
        else: d['pine_ebar']=True
        return d
    def pine_context(self,d,p): return {'long':d['pine_long'].to_numpy(bool),'short':d['pine_short'].to_numpy(bool),'gate':d['pine_ebar'].to_numpy(bool) if hasattr(d['pine_ebar'],'to_numpy') else [True]*len(d),'p':p}
    def pine_script(self,b,i,x):
        if not hasattr(self,'_last_pos_type'): self._last_pos_type=0
        if not x['gate'][i] or x['p']['tradeType']=='NONE': return
        if self._last_pos_type==1 and x['short'][i]: b.close('long'); self._last_pos_type=0
        if self._last_pos_type==-1 and x['long'][i]: b.close('short'); self._last_pos_type=0
        if x['long'][i] and x['p']['tradeType']!='SHORT' and self._last_pos_type==0: b.entry('long','long'); self._last_pos_type=1
        if x['short'][i] and x['p']['tradeType']!='LONG' and self._last_pos_type==0: b.entry('short','short'); self._last_pos_type=-1
        tp=float(x['p']['tpPoints']); sl=float(x['p']['slPoints'])
        if self._last_pos_type!=0 and (tp>0 or sl>0): b.exit('TP/SL',profit=tp if tp>0 else None,loss=sl if sl>0 else None)
