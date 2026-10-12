"""Deep Pine v5 port. The source's date inputs are calculated but never used in entry/exit conditions."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_014_TripleMA(PinePortBase, IStrategy):
    timeframe='1d'; can_short=False; source_file='短中长期三重移动平均线趋势跟踪策略-Short-Medium-Long-Term-Triple-Moving-Average-Trend-Following-Strategy.md'
    source_defaults={}; source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=["start_date/end_date are dead code in source and do not constrain trading.","Variables named ema14/ema60 in related prose are irrelevant here; this strategy uses SMA(low,3), SMA(high,3), SMA(close,30)."]
    def pine_indicators(self,d,p):
        lo3=ta.pine_sma(d['low'],3); hi3=ta.pine_sma(d['high'],3); c30=ta.pine_sma(d['close'],30)
        d['pine_entry']=(d['close']<lo3)&(d['close']>c30); d['pine_exit']=d['close']>hi3; return d
    def pine_context(self,d,p): return {'e':d['pine_entry'].to_numpy(bool),'x':d['pine_exit'].to_numpy(bool)}
    def pine_script(self,b,i,x):
        if x['e'][i]: b.entry('Buy','long')
        if x['x'][i]: b.close('Buy')
