"""Generic source-preserving Pine adapter for batch_012.

This adapter follows the same PinePortBase surface used by batch_001:
`pine_indicators`, `pine_context`, and `pine_script`.

It evaluates the common vectorisable Pine subset with pandas and replays the
source's strategy.entry/close/exit/order calls through PineBroker.  Complex
stateful constructs are intentionally surfaced through fidelity notes instead
of being silently rewritten.
"""
from __future__ import annotations
import math, re
import numpy as np
import pandas as pd

class PineSeries(pd.Series):
    @property
    def _constructor(self):
        return PineSeries
    def __getitem__(self, key):
        # Pine x[n] means n bars ago, not label/index lookup.
        if isinstance(key, (int, np.integer)) and key >= 0:
            return PineSeries(self.shift(int(key)))
        return super().__getitem__(key)

def _ps(x, index=None):
    if isinstance(x, PineSeries): return x
    if isinstance(x, pd.Series): return PineSeries(x)
    if index is None: return x
    return PineSeries(pd.Series(x, index=index))

def _n(v, d=0):
    try:
        if isinstance(v, pd.Series):
            z=v.dropna()
            return int(z.iloc[-1]) if len(z) else int(d)
        return int(v)
    except Exception: return int(d)

def sma(x,n): return _ps(x).rolling(_n(n,1), min_periods=_n(n,1)).mean()
def sum_(x,n): return _ps(x).rolling(_n(n,1), min_periods=_n(n,1)).sum()
def stdev(x,n,*args,**kwargs): return _ps(x).rolling(_n(n,1), min_periods=_n(n,1)).std(ddof=0)
def highest(x,n): return _ps(x).rolling(_n(n,1), min_periods=1).max()
def lowest(x,n): return _ps(x).rolling(_n(n,1), min_periods=1).min()
def ema(x,n):
    return _ps(x).ewm(span=max(_n(n,1),1), adjust=False, min_periods=1).mean()
def rma(x,n):
    return _ps(x).ewm(alpha=1.0/max(_n(n,1),1), adjust=False, min_periods=1).mean()
def wma(x,n):
    n=max(_n(n,1),1); w=np.arange(1,n+1,dtype=float)
    return _ps(x).rolling(n,min_periods=n).apply(lambda a: float(np.dot(a,w)/w.sum()), raw=True)
def swma(x):
    return _ps(x).rolling(4,min_periods=4).apply(lambda a:(a[0]+2*a[1]+2*a[2]+a[3])/6.0,raw=True)
def hma(x,n):
    n=max(_n(n,1),1); return wma(2*wma(x,max(n//2,1))-wma(x,n),max(int(math.sqrt(n)),1))
def change(x,n=1): return _ps(x)-_ps(x).shift(_n(n,1))
def mom(x,n): return change(x,n)
def crossover(a,b):
    a=_ps(a); b=_ps(b,a.index) if not isinstance(b,pd.Series) else _ps(b)
    return PineSeries((a>b)&(a.shift(1)<=b.shift(1))).fillna(False)
def crossunder(a,b):
    a=_ps(a); b=_ps(b,a.index) if not isinstance(b,pd.Series) else _ps(b)
    return PineSeries((a<b)&(a.shift(1)>=b.shift(1))).fillna(False)
def cross(a,b): return crossover(a,b)|crossunder(a,b)
def rising(x,n):
    x=_ps(x); n=max(_n(n,1),1); return x>x.shift(1).rolling(n,min_periods=n).max()
def falling(x,n):
    x=_ps(x); n=max(_n(n,1),1); return x<x.shift(1).rolling(n,min_periods=n).min()
def tr_fn(high,low,close):
    pc=_ps(close).shift(1); h=_ps(high); l=_ps(low)
    return PineSeries(pd.concat([h-l,(h-pc).abs(),(l-pc).abs()],axis=1).max(axis=1))
def atr(high,low,close,n=14): return rma(tr_fn(high,low,close),n)
def rsi(x,n=14):
    x=_ps(x); d=x.diff(); up=d.clip(lower=0); dn=(-d.clip(upper=0)); au=rma(up,n); ad=rma(dn,n)
    rs=au/ad.replace(0,np.nan); out=100-(100/(1+rs)); out=out.where(ad!=0,100.0); return PineSeries(out)
def stoch(close,high,low,n=14):
    lo=lowest(low,n); hi=highest(high,n); return 100*(_ps(close)-lo)/(hi-lo).replace(0,np.nan)
def vwma(x,n,volume=None):
    x=_ps(x); volume=_ps(volume,x.index) if volume is not None else PineSeries(pd.Series(1.0,index=x.index))
    return sum_(x*volume,n)/sum_(volume,n)
def linreg(x,n,offset=0):
    x=_ps(x); n=max(_n(n,1),1); off=_n(offset,0)
    xx=np.arange(n,dtype=float)
    def f(a):
        if np.isnan(a).any(): return np.nan
        m,c=np.polyfit(xx,a,1); return c+m*(n-1-off)
    return x.rolling(n,min_periods=n).apply(f,raw=True)
def cum(x): return _ps(x).cumsum()
def percentile_linear_interpolation(x,n,p):
    return _ps(x).rolling(max(_n(n,1),1),min_periods=max(_n(n,1),1)).quantile(float(p)/100.0,interpolation='linear')
def valuewhen(cond,src,occ=0):
    cond=_ps(cond); src=_ps(src,cond.index) if not isinstance(src,pd.Series) else _ps(src); occ=_n(occ,0)
    vals=[]; hits=[]
    for c,v in zip(cond.fillna(False).astype(bool),src):
        if c: hits.append(v)
        vals.append(hits[-1-occ] if len(hits)>occ else np.nan)
    return PineSeries(vals,index=cond.index)
def barssince(cond):
    cond=_ps(cond).fillna(False).astype(bool); out=[]; last=None
    for i,c in enumerate(cond):
        if c: last=i; out.append(0)
        else: out.append(np.nan if last is None else i-last)
    return PineSeries(out,index=cond.index)
def nz(x,repl=0):
    if isinstance(x,pd.Series): return PineSeries(x.fillna(repl))
    try: return repl if pd.isna(x) else x
    except Exception: return x
def na(x):
    if isinstance(x,pd.Series): return PineSeries(x.isna())
    try: return bool(pd.isna(x))
    except Exception: return False
def iff(c,a,b): return where(c,a,b)
def where(c,a,b):
    if isinstance(c,pd.Series):
        idx=c.index; aa=_ps(a,idx) if not isinstance(a,pd.Series) else _ps(a); bb=_ps(b,idx) if not isinstance(b,pd.Series) else _ps(b)
        return PineSeries(pd.Series(np.where(c.fillna(False).astype(bool),aa,bb),index=idx))
    return a if bool(c) else b
def abs_(x): return x.abs() if isinstance(x,pd.Series) else abs(x)
def max_(a,b):
    if isinstance(a,pd.Series) or isinstance(b,pd.Series):
        idx=a.index if isinstance(a,pd.Series) else b.index; return PineSeries(pd.concat([_ps(a,idx),_ps(b,idx)],axis=1).max(axis=1))
    return max(a,b)
def min_(a,b):
    if isinstance(a,pd.Series) or isinstance(b,pd.Series):
        idx=a.index if isinstance(a,pd.Series) else b.index; return PineSeries(pd.concat([_ps(a,idx),_ps(b,idx)],axis=1).min(axis=1))
    return min(a,b)
def round_(x,n=0): return x.round(_n(n,0)) if isinstance(x,pd.Series) else round(x,_n(n,0))
def floor_(x): return np.floor(x)
def ceil_(x): return np.ceil(x)
def sqrt_(x): return np.sqrt(x)
def log_(x): return np.log(x)
def exp_(x): return np.exp(x)
def pow_(a,b): return np.power(a,b)
def sign_(x): return np.sign(x)
def security(*args,**kwargs):
    # Source-preserving approximation: same-frame value. Files using this are
    # flagged in source_fidelity_notes for manual MTF parity verification.
    return args[2] if len(args)>=3 else np.nan

def _split_args(s):
    out=[]; cur=''; dep=0; q=None; esc=False
    for ch in s:
        if q:
            cur+=ch
            if esc: esc=False
            elif ch=='\\': esc=True
            elif ch==q: q=None
            continue
        if ch in "'\"": q=ch; cur+=ch; continue
        if ch in '([{': dep+=1
        elif ch in ')]}': dep-=1
        if ch==',' and dep==0: out.append(cur.strip()); cur=''
        else: cur+=ch
    if cur.strip(): out.append(cur.strip())
    return out

def _strip_comment(line):
    q=None; esc=False
    for i in range(len(line)-1):
        c=line[i]
        if q:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q: q=None
        elif c in "'\"": q=c
        elif c=='/' and line[i+1]=='/': return line[:i]
    return line

def _balance(s):
    dep=0; q=None; esc=False
    for c in s:
        if q:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q:q=None
            continue
        if c in "'\"": q=c
        elif c in '([{': dep+=1
        elif c in ')]}': dep-=1
    return dep

def _logical_parenthesize(expr):
    # pandas.eval implements `and/or/not` elementwise with the Python engine.
    return expr

def _ternary(expr):
    # Convert a top-level Pine conditional expression to where(cond,a,b).
    dep=0; q=None; esc=False; qpos=-1
    for i,c in enumerate(expr):
        if q:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==q:q=None
            continue
        if c in "'\"": q=c; continue
        if c in '([{': dep+=1
        elif c in ')]}': dep-=1
        elif c=='?' and dep==0: qpos=i; break
    if qpos<0: return expr
    dep=0; q=None; esc=False; nested=0
    for j in range(qpos+1,len(expr)):
        c=expr[j]
        if q:
            if esc:esc=False
            elif c=='\\':esc=True
            elif c==q:q=None
            continue
        if c in "'\"": q=c; continue
        if c in '([{': dep+=1
        elif c in ')]}': dep-=1
        elif dep==0:
            if c=='?': nested+=1
            elif c==':':
                if nested: nested-=1
                else:
                    a=expr[:qpos].strip(); b=expr[qpos+1:j].strip(); d=expr[j+1:].strip()
                    return f'where(({_ternary(a)}),({_ternary(b)}),({_ternary(d)}))'
    return expr

def _prep_expr(expr):
    e=expr.strip().rstrip(';')
    e=re.sub(r'\btrue\b','True',e,flags=re.I); e=re.sub(r'\bfalse\b','False',e,flags=re.I)
    e=re.sub(r'\bna\b(?!\s*\()', 'np.nan', e)
    repl={
      'ta.sma':'sma','sma':'sma','ta.ema':'ema','ema':'ema','ta.wma':'wma','wma':'wma','ta.rma':'rma',
      'ta.stdev':'stdev','stdev':'stdev','ta.highest':'highest','highest':'highest','ta.lowest':'lowest','lowest':'lowest',
      'math.sum':'sum_','ta.sum':'sum_','sum':'sum_','ta.change':'change','change':'change','ta.crossover':'crossover','crossover':'crossover',
      'ta.crossunder':'crossunder','crossunder':'crossunder','ta.cross':'cross','cross':'cross','ta.rsi':'rsi','rsi':'rsi',
      'ta.stoch':'stoch','stoch':'stoch','ta.vwma':'vwma','vwma':'vwma','ta.linreg':'linreg','linreg':'linreg','ta.cum':'cum','cum':'cum',
      'ta.rising':'rising','rising':'rising','ta.falling':'falling','falling':'falling','ta.valuewhen':'valuewhen','valuewhen':'valuewhen',
      'ta.barssince':'barssince','barssince':'barssince','ta.mom':'mom','mom':'mom','ta.hma':'hma','hma':'hma','ta.swma':'swma',
      'ta.percentile_linear_interpolation':'percentile_linear_interpolation',
      'request.security':'security','security':'security','math.abs':'abs_','abs':'abs_','math.max':'max_','max':'max_','math.min':'min_','min':'min_',
      'math.round':'round_','round':'round_','math.floor':'floor_','floor':'floor_','math.ceil':'ceil_','ceil':'ceil_','math.sqrt':'sqrt_','sqrt':'sqrt_',
      'math.log':'log_','log':'log_','math.exp':'exp_','exp':'exp_','math.pow':'pow_','pow':'pow_','math.sign':'sign_','sign':'sign_',
      'ta.atr':'ATR_CALL','atr':'ATR_CALL','ta.tr':'TR_CALL','tr':'TR_CALL','iff':'iff','nz':'nz','na':'na'
    }
    # longest first, only function identifiers
    for k,v in sorted(repl.items(),key=lambda kv:-len(kv[0])):
        e=re.sub(r'(?<![\w.])'+re.escape(k)+r'(?=\s*\()',v,e)
    e=e.replace('ATR_CALL(', 'atr(high,low,close,')
    e=e.replace('TR_CALL(', 'tr_fn(high,low,close')
    # Pine `not` / and / or are accepted elementwise by pandas.eval.
    e=_ternary(e)
    return e

class Batch012Runtime:
    def __init__(self, source, dataframe, params, source_file=''):
        self.source=source; self.df=dataframe; self.params=params or {}; self.source_file=source_file
        self.index=dataframe.index
        self.env={k:PineSeries(dataframe[k]) for k in ('open','high','low','close','volume') if k in dataframe}
        if 'volume' not in self.env: self.env['volume']=PineSeries(pd.Series(0.0,index=self.index))
        self.env['hl2']=(self.env['high']+self.env['low'])/2
        self.env['hlc3']=(self.env['high']+self.env['low']+self.env['close'])/3
        self.env['ohlc4']=(self.env['open']+self.env['high']+self.env['low']+self.env['close'])/4
        self.env['time']=PineSeries(pd.Series(np.arange(len(self.index)),index=self.index))
        self.env['bar_index']=PineSeries(pd.Series(np.arange(len(self.index)),index=self.index))
        self.orders=[]; self.notes=[]
        self._build()
    def _locals(self, extra=None):
        d=dict(self.env)
        d.update({'np':np,'pd':pd,'sma':sma,'ema':ema,'wma':wma,'rma':rma,'stdev':stdev,'highest':highest,'lowest':lowest,
         'sum_':sum_,'change':change,'crossover':crossover,'crossunder':crossunder,'cross':cross,'rsi':rsi,'stoch':stoch,
         'vwma':lambda x,n:vwma(x,n,self.env.get('volume')),'linreg':linreg,'cum':cum,'rising':rising,'falling':falling,
         'valuewhen':valuewhen,'barssince':barssince,'mom':mom,'hma':hma,'swma':swma,'percentile_linear_interpolation':percentile_linear_interpolation,
         'atr':lambda h,l,c,n=14:atr(h,l,c,n),'tr_fn':tr_fn,'nz':nz,'na':na,'iff':iff,'where':where,'security':security,
         'abs_':abs_,'max_':max_,'min_':min_,'round_':round_,'floor_':floor_,'ceil_':ceil_,'sqrt_':sqrt_,'log_':log_,'exp_':exp_,'pow_':pow_,'sign_':sign_,
         'position_size':PineSeries(pd.Series(0.0,index=self.index)), 'position_avg_price':PineSeries(pd.Series(np.nan,index=self.index)),
         'strategy_long':'long','strategy_short':'short'})
        if extra:d.update(extra)
        return d
    def _eval(self, expr, extra=None):
        e=_prep_expr(expr)
        e=e.replace('strategy.long','strategy_long').replace('strategy.short','strategy_short')
        e=e.replace('strategy.position_size','position_size').replace('strategy.position_avg_price','position_avg_price')
        # common enum/display symbols
        e=re.sub(r'\b(?:color|plot|shape|location|size|display|barmerge|timeframe|currency|strategy)\.[A-Za-z_]\w*', '0', e)
        try:
            v=pd.eval(e,local_dict=self._locals(extra),engine='python')
            if isinstance(v,pd.Series) and not isinstance(v,PineSeries): v=PineSeries(v)
            return v
        except Exception as ex:
            self.notes.append(f'eval failed: {expr} :: {type(ex).__name__}: {ex}')
            return PineSeries(pd.Series(np.nan,index=self.index))
    def _mask(self, stack):
        m=PineSeries(pd.Series(True,index=self.index))
        for x in stack:
            try: m=PineSeries(m & _ps(x,self.index).fillna(False).astype(bool))
            except Exception: pass
        return m
    def _record_order(self,line,mask):
        m=re.search(r'strategy\.(entry|close|exit|order|close_all|cancel|cancel_all)\s*\((.*)\)\s*$',line.strip())
        if not m:return
        kind,args=m.group(1),_split_args(m.group(2)); pos=[]; kw={}
        for a in args:
            # named arg, but do not split == >= <=
            mm=re.match(r'^([A-Za-z_]\w*)\s*=\s*(?!=)(.*)$',a,re.S)
            if mm: kw[mm.group(1)]=mm.group(2).strip()
            else: pos.append(a)
        when=self._eval(kw.get('when','True')) if 'when' in kw else True
        full=PineSeries(self._mask(mask) & _ps(when,self.index).fillna(False).astype(bool))
        self.orders.append({'kind':kind,'pos':pos,'kw':kw,'mask':full,'raw':line})
    def _build(self):
        src=re.sub(r'/\*.*?\*/','',self.source,flags=re.S)
        physical=[]
        for raw in src.splitlines():
            raw=_strip_comment(raw.rstrip())
            if not raw.strip():continue
            if raw.strip().startswith('//@'):continue
            physical.append(raw.expandtabs(4))
        # join multiline parenthesized statements, preserving first-line indent
        lines=[]; i=0
        while i<len(physical):
            line=physical[i]; indent=len(line)-len(line.lstrip()); acc=line.strip(); bal=_balance(acc)
            while i+1<len(physical) and (bal>0 or acc.endswith((',', '+','-','*','/','and','or','?'))):
                i+=1; acc+=' '+physical[i].strip(); bal=_balance(acc)
            lines.append((indent,acc)); i+=1
        stack=[] # (indent, condition series)
        skip_func_indent=None
        for idx,(indent,s) in enumerate(lines):
            while stack and indent<=stack[-1][0]: stack.pop()
            if skip_func_indent is not None:
                if indent>skip_func_indent: continue
                skip_func_indent=None
            # function definitions are too varied for a generic vector pass; mark and skip body.
            if re.match(r'^[A-Za-z_]\w*\s*\([^)]*\)\s*=>',s):
                self.notes.append('custom function requires per-strategy parity review')
                skip_func_indent=indent; continue
            if s.startswith('if ' ) or s.startswith('if(') or s.startswith('if ('):
                cond=re.sub(r'^if\s*','',s).strip();
                if cond.startswith('(') and cond.endswith(')'): cond=cond[1:-1]
                stack.append((indent,self._eval(cond))); continue
            if s.startswith('else'):
                self.notes.append('else branch approximated in generic vector adapter'); continue
            if s.startswith(('for ','while ','switch ')) or s.endswith(' switch'):
                self.notes.append('loop/switch requires per-strategy parity review'); continue
            if s.startswith(('strategy(', 'indicator(', 'study(', 'library(')): continue
            if s.startswith(('plot','fill','bgcolor','barcolor','hline','alertcondition','alert(','label.','line.','box.','table.')): continue
            if s.startswith('strategy.'):
                self._record_order(s,[c for _,c in stack]); continue
            # assignment: optional var/type prefix; tuple assignments skipped with note
            if s.startswith('['):
                self.notes.append('tuple assignment requires per-strategy parity review'); continue
            am=re.match(r'^(?:(?:var|varip|const)\s+)?(?:(?:float|int|bool|string|color)\s+)?([A-Za-z_]\w*)\s*(?::=|=)\s*(.+)$',s,re.S)
            if am:
                name,rhs=am.group(1),am.group(2).strip()
                if rhs.startswith('input'):
                    # use source_defaults/params when available, otherwise first input arg
                    if name in self.params: val=self.params[name]
                    else:
                        mm=re.match(r'input(?:\.\w+)?\s*\((.*)\)$',rhs,re.S); aa=_split_args(mm.group(1)) if mm else []
                        val=self._eval(aa[0]) if aa else np.nan
                    self.env[name]=val; continue
                val=self._eval(rhs)
                if stack and isinstance(val,pd.Series):
                    old=self.env.get(name,PineSeries(pd.Series(np.nan,index=self.index)))
                    self.env[name]=where(self._mask([c for _,c in stack]),val,old)
                else:self.env[name]=val
                continue
            # source v1/v2 frequently uses bare function-like directives; ignore displays.
        # expose unique note order
        self.notes=list(dict.fromkeys(self.notes))
    def _val_at(self,expr,i):
        v=self._eval(expr)
        if isinstance(v,pd.Series):
            try:return v.iloc[i]
            except Exception:return np.nan
        return v
    def context(self):
        return {'runtime':self}
    def step(self,broker,i):
        for o in self.orders:
            try:
                if not bool(o['mask'].iloc[i]): continue
            except Exception: continue
            kind=o['kind']; pos=o['pos']; kw=o['kw']
            def val(s,default=None):
                if s is None:return default
                x=self._val_at(s,i)
                try:
                    if pd.isna(x): return default
                except Exception: pass
                return x
            if kind in ('entry','order'):
                oid=str(val(pos[0],'Order')) if pos else 'Order'
                direction=str(val(pos[1],'long')) if len(pos)>1 else 'long'
                direction='short' if 'short' in direction.lower() else 'long'
                qexpr=kw.get('qty') or (pos[2] if len(pos)>2 else None)
                kwargs={}
                q=val(qexpr,None); lim=val(kw.get('limit'),None); stop=val(kw.get('stop'),None)
                if q is not None: kwargs['qty']=float(q)
                if lim is not None: kwargs['limit']=float(lim)
                if stop is not None: kwargs['stop']=float(stop)
                try: broker.entry(oid,direction,**kwargs)
                except TypeError: broker.entry(oid,direction)
            elif kind=='close':
                oid=str(val(pos[0],'Order')) if pos else 'Order'
                try: broker.close(oid)
                except Exception: pass
            elif kind=='close_all':
                try: broker.close_all()
                except Exception:
                    # PineBroker versions without close_all: close known ids impossible here.
                    pass
            elif kind=='exit':
                xid=str(val(pos[0],'Exit')) if pos else 'Exit'; kwargs={}
                fe=kw.get('from_entry') or (pos[1] if len(pos)>1 else None)
                if fe is not None: kwargs['from_entry']=str(val(fe,''))
                for k in ('limit','stop','trail_price','trail_points','trail_offset'):
                    z=val(kw.get(k),None)
                    if z is not None: kwargs[k]=float(z)
                try: broker.exit(xid,**kwargs)
                except TypeError:
                    kwargs={k:v for k,v in kwargs.items() if k in ('from_entry','limit','stop')}
                    try: broker.exit(xid,**kwargs)
                    except Exception: pass
            elif kind=='cancel':
                try: broker.cancel(str(val(pos[0],'')))
                except Exception: pass
            elif kind=='cancel_all':
                try: broker.cancel_all()
                except Exception: pass
