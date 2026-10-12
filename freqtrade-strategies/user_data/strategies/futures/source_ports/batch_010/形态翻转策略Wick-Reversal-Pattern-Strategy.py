"""Deep Pine v4 port of Wick Reversal Signal."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_019_WickReversal(PinePortBase, IStrategy):
    timeframe='3m'; can_short=True; source_file='形态翻转策略Wick-Reversal-Pattern-Strategy.md'
    source_defaults={"wickMultiplier":3.25,"bodyPercentage":0.35,"barsBack":50,"bodyMultiplier":1.1}; source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["The doji test is absolute price difference abs(close-open)<0.01, not tick-size normalized; preserved.","No explicit exits: opposite signals reverse via strategy.entry netting."]
    def pine_indicators(self,d,p):
        h,l,o,c=d['high'],d['low'],d['open'],d['close']; rng=h-l; avg=ta.pine_rma(rng,int(p['barsBack'])); w=float(p['wickMultiplier']); bp=float(p['bodyPercentage']); bm=float(p['bodyMultiplier']); big=rng>=avg*bm
        L=((c>o)&((o-l)>=(c-o)*w)&((h-c)<=rng*bp)&big)|((c<o)&((c-l)>=(o-c)*w)&((h-c)<=rng*bp)&big)|(((c-o).abs()<0.01)&(c!=h)&(rng>=(h-c)*w)&((h-c)<=rng*bp)&big)
        S=((c<o)&((h-o)>=(o-c)*w)&((c-l)<=rng*bp)&big)|((c>o)&((h-c)>=(c-o)*w)&((c-l)<=rng*bp)&big)|(((c-o).abs()<0.01)&(c!=l)&(rng>=(c-l)*w)&((c-l)<=rng*bp)&big)
        d['pine_L']=L; d['pine_S']=S; return d
    def pine_context(self,d,p): return {'L':d['pine_L'].to_numpy(bool),'S':d['pine_S'].to_numpy(bool)}
    def pine_script(self,b,i,x):
        b.entry('LONG','long',when=x['L'][i]); b.entry('SHORT','short',when=x['S'][i])
