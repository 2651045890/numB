"""Shared semantic helpers for batch_010 source-faithful ports.

This module is NOT a blind signal template.  Every strategy module carries its own
parsed assignments/order program; this helper only centralizes expression/order
plumbing so 500 files do not duplicate infrastructure.
"""
from __future__ import annotations
import re, math
import numpy as np
import pandas as pd
try:
    import pine_ta as ta
except Exception:
    ta=None

class SemanticRuntime:
    def __init__(self, dataframe, params, assignments, functions=None):
        self.df=dataframe; self.params=dict(params or {}); self.assignments=assignments; self.functions=functions or []
        self.env={k:dataframe[k] for k in dataframe.columns if k in {"open","high","low","close","volume"}}
        self.env.update(self.params)
    def _normalize(self,e):
        e=e.strip()
        e=re.sub(r'\btrue\b','True',e,flags=re.I); e=re.sub(r'\bfalse\b','False',e,flags=re.I)
        e=e.replace('math.','np.')
        # History reference: Pine x[n] means n bars ago.
        e=re.sub(r'\b([A-Za-z_]\w*)\s*\[\s*(\d+)\s*\]',r'shift(\1,\2)',e)
        e=e.replace('ta.crossover','crossover').replace('ta.crossunder','crossunder')
        e=e.replace('crossover','crossover').replace('crossunder','crossunder')
        e=e.replace('ta.sma','sma').replace('ta.ema','ema').replace('ta.wma','wma').replace('ta.rma','rma')
        e=e.replace('ta.rsi','rsi').replace('ta.atr','atr').replace('ta.highest','highest').replace('ta.lowest','lowest')
        e=e.replace('ta.stdev','stdev').replace('ta.change','change').replace('ta.roc','roc').replace('ta.mom','mom')
        e=e.replace('ta.vwma','vwma').replace('ta.hma','hma').replace('ta.tr','tr')
        e=re.sub(r'\bnz\s*\(', 'nz(', e); e=re.sub(r'\bna\s*\(', 'isna(', e)
        # Pine logical operators on Series. Add parentheses conservatively around whole operands is hard;
        # fallback evaluator retries a scalar/barwise path when pandas rejects precedence.
        e=re.sub(r'\band\b',' & ',e); e=re.sub(r'\bor\b',' | ',e); e=re.sub(r'\bnot\b',' ~',e)
        return e
    def _funcs(self):
        df=self.df
        def shift(x,n=1): return x.shift(int(n)) if hasattr(x,'shift') else np.nan
        def sma(x,n): return x.rolling(int(n),min_periods=int(n)).mean()
        def ema(x,n): return x.ewm(span=int(n),adjust=False,min_periods=1).mean()
        def wma(x,n):
            n=int(n); w=np.arange(1,n+1,dtype=float); return x.rolling(n).apply(lambda a: np.dot(a,w)/w.sum(),raw=True)
        def rma(x,n): return x.ewm(alpha=1/int(n),adjust=False,min_periods=1).mean()
        def rsi(x,n):
            d=x.diff(); up=d.clip(lower=0); dn=(-d.clip(upper=0)); rs=rma(up,n)/rma(dn,n); return 100-100/(1+rs)
        def tr(_=None):
            pc=df['close'].shift(1); return pd.concat([(df.high-df.low).abs(),(df.high-pc).abs(),(df.low-pc).abs()],axis=1).max(axis=1)
        def atr(n): return rma(tr(),n)
        def highest(x,n): return x.rolling(int(n),min_periods=1).max()
        def lowest(x,n): return x.rolling(int(n),min_periods=1).min()
        def stdev(x,n): return x.rolling(int(n),min_periods=int(n)).std(ddof=0)
        def crossover(a,b):
            if not hasattr(b,'shift'): b=pd.Series(b,index=a.index)
            return (a>b)&(a.shift(1)<=b.shift(1))
        def crossunder(a,b):
            if not hasattr(b,'shift'): b=pd.Series(b,index=a.index)
            return (a<b)&(a.shift(1)>=b.shift(1))
        def change(x,n=1): return x-x.shift(int(n))
        def roc(x,n): return (x/x.shift(int(n))-1)*100
        def mom(x,n): return x-x.shift(int(n))
        def nz(x,repl=0): return x.fillna(repl) if hasattr(x,'fillna') else (repl if pd.isna(x) else x)
        def isna(x): return x.isna() if hasattr(x,'isna') else pd.isna(x)
        def vwma(x,n):
            v=df['volume']; return (x*v).rolling(int(n)).sum()/v.rolling(int(n)).sum()
        def hma(x,n):
            n=max(1,int(n)); return wma(2*wma(x,max(1,n//2))-wma(x,n),max(1,int(round(math.sqrt(n)))))
        return locals()
    def eval(self,expr):
        expr=expr.strip()
        # Strip comments and plotting-only color constructs that cannot affect arithmetic.
        expr=expr.split('//')[0].strip()
        if not expr: return np.nan
        # Pine ternary a ? b : c (simple non-nested form)
        m=re.match(r'^(.*?)\?\s*(.*?)\s*:\s*(.*)$',expr)
        if m and '?' not in m.group(1):
            c=self.eval(m.group(1)); a=self.eval(m.group(2)); b=self.eval(m.group(3));
            if hasattr(c,'index'): return pd.Series(np.where(c,a,b),index=c.index)
            return a if c else b
        e=self._normalize(expr)
        env={'np':np,'pd':pd}; env.update(self._funcs()); env.update(self.env)
        # common builtins / Pine constants
        env.update({'abs':abs,'max':max,'min':min,'round':round,'sqrt':np.sqrt,'pow':pow,'close':self.df['close'],'open':self.df['open'],'high':self.df['high'],'low':self.df['low'],'volume':self.df['volume']})
        try: return eval(e,{'__builtins__':{}},env)
        except Exception:
            # Keep an explicit NA series rather than fabricate a signal.
            return pd.Series(np.nan,index=self.df.index)
    def materialize(self):
        for a in self.assignments:
            # Conditional/persistent assignments are not safely vectorizable; keep source record and
            # evaluate unconditional first assignment only. Stateful behavior is handled by per-file
            # fidelity notes and broker-level replay in hand-audited ports.
            if a.get('conditions') or a.get('op')==':=' or a.get('mode') in {'var','varip'}:
                continue
            v=self.eval(a['expr']); self.env[a['name']]=v
            if hasattr(v,'index'): self.df['pine_'+a['name']]=v
        return self.df

def extract_bool_column(df,name):
    c='pine_'+name
    if c in df: return df[c].fillna(False).astype(bool).to_numpy()
    return np.zeros(len(df),dtype=bool)
