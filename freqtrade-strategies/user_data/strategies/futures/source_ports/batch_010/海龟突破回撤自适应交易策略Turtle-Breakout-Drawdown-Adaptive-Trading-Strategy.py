"""Deep Pine v4 port of Noro's Turtle strategy.

The fast and slow Donchian STOP entries coexist.  With default settings only
long entries are enabled.  The source's recursive lot sizing is approximated
from current broker equity at the instant an entry order is placed; this is the
same economic formula used by the source whenever position size changes.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_008_NoroTurtles(PinePortBase, IStrategy):
    timeframe='1d'; can_short=True; source_file='海龟突破回撤自适应交易策略Turtle-Breakout-Drawdown-Adaptive-Trading-Strategy.md'
    source_defaults={"needlong":True,"needshort":False,"sizelong":100.0,"sizeshort":100.0,"needfast":True,"needslow":True,"enter_fast":20,"exit_fast":10,"enter_slow":55,"exit_slow":20}
    source_qty_type='percent_of_equity'; source_qty_value=100.; source_initial_capital=100.; source_commission_percent=0.1; source_pyramiding=0; source_reproduce_stops=True
    source_fidelity_notes=["Both fast and slow stop-entry orders are submitted while flat; whichever fills first determines position. The engine's resting-order arbitration governs same-bar ties.",
        "lotlong/lotshort are recursive in source and refresh when position_size changes. Here quantity is recomputed from broker.equity/close when flat and submitting entries, which is the source formula at the relevant transition.",
        "Drawdown label code is display-only and omitted."]
    def pine_indicators(self,d,p):
        h,l=d['high'],d['low']
        d['pine_fastL']=ta.pine_highest(h,int(p['enter_fast'])); d['pine_fastLC']=ta.pine_lowest(l,int(p['exit_fast']))
        d['pine_fastS']=ta.pine_lowest(l,int(p['enter_fast'])); d['pine_fastSC']=ta.pine_highest(h,int(p['exit_fast']))
        d['pine_slowL']=ta.pine_highest(h,int(p['enter_slow'])); d['pine_slowLC']=ta.pine_lowest(l,int(p['exit_slow']))
        d['pine_slowS']=ta.pine_lowest(l,int(p['enter_slow'])); d['pine_slowSC']=ta.pine_highest(h,int(p['exit_slow']))
        return d
    def pine_context(self,d,p):
        x={k:d['pine_'+k].to_numpy(float) for k in ['fastL','fastLC','fastS','fastSC','slowL','slowLC','slowS','slowSC']}; x['close']=d['close'].to_numpy(float); x['p']=p; return x
    def pine_script(self,b,i,x):
        p=x['p']; c=x['close'][i]
        if b.position_size==0:
            ql=b.equity/c*float(p['sizelong'])/100.0 if c else 0.0; qs=b.equity/c*float(p['sizeshort'])/100.0 if c else 0.0
            if p['needfast'] and p['needlong']: b.entry('fast L','long',qty=ql,stop=x['fastL'][i])
            if p['needfast'] and p['needshort']: b.entry('fast S','short',qty=qs,stop=x['fastS'][i])
            if p['needslow'] and p['needlong']: b.entry('slow L','long',qty=ql,stop=x['slowL'][i])
            if p['needslow'] and p['needshort']: b.entry('slow S','short',qty=qs,stop=x['slowS'][i])
        if b.position_size>0:
            if p['needfast'] and p['needlong']: b.exit('fast L',stop=x['fastLC'][i])
            if p['needslow'] and p['needlong']: b.exit('slow L',stop=x['slowLC'][i])
        if b.position_size<0:
            if p['needfast'] and p['needshort']: b.exit('fast S',stop=x['fastSC'][i])
            if p['needslow'] and p['needshort']: b.exit('slow S',stop=x['slowSC'][i])
