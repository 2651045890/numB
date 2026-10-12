"""Deep Pine v5 port of the candlestick pattern/trend-filter strategy.
The custom function named sma() is reproduced as a simple rolling mean; despite
variables named ema14/ema60, the source does NOT calculate EMA.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_018_CandlestickTrend(PinePortBase, IStrategy):
    timeframe='1d'; can_short=True; source_file='烛台形态趋势过滤策略Candlestick-Pattern-Trend-Filter-Strategy.md'
    source_defaults={}; source_qty_type='percent_of_equity'; source_qty_value=5.; source_initial_capital=10000.; source_pyramiding=0; source_commission_percent=0.02; source_reproduce_stops=False
    source_fidelity_notes=["ema14/ema60 are custom SMA values, not EMA.","The morningStar alternative is impossible because it requires close < ema60 while upTrend requires close > ema60. The darkCloud alternative is likewise impossible under downTrend. These contradictions are preserved; effective signals reduce to engulfing branches.","No strategy.close/exit exists; opposite entry reverses the position."]
    def pine_indicators(self,d,p):
        o,c=d['open'],d['close']; bull=(c>o)&(o<c.shift(1))&(c.shift(1)<o.shift(1))&(c>o.shift(1)); bear=(c<o)&(o>c.shift(1))&(c.shift(1)>o.shift(1))&(c<o.shift(1)); dark=(c<o)&(o>c.shift(1))&(c<o.shift(1)); morning=(c.shift(2)<o.shift(2))&(c.shift(1)<o.shift(1))&(c.shift(1)<c.shift(2))&(o.shift(1)>c.shift(2))&(c>o)&(c>o.shift(1))
        m14=ta.pine_sma(c,14); m60=ta.pine_sma(c,60); up=(c>m14)&(c>m60); down=(c<m14)&(c<m60)
        d['pine_L']=(bull&(c>m14)&(c>m60)&up)|(morning&(c<m60)&up); d['pine_S']=(bear&(c<m14)&(c<m60)&down)|(dark&(c>m14)&(c>m60)&down); return d
    def pine_context(self,d,p): return {'L':d['pine_L'].to_numpy(bool),'S':d['pine_S'].to_numpy(bool)}
    def pine_script(self,b,i,x):
        if x['L'][i]: b.entry('Long','long')
        if x['S'][i]: b.entry('Short','short')
