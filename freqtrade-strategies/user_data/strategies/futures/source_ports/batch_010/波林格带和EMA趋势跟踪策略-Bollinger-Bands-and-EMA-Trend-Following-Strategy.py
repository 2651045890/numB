"""Deep Pine v5 port of Bollinger Bands + EMA breakout with equity-risk sizing."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_011_BollingerEMA(PinePortBase, IStrategy):
    timeframe='1h'; can_short=True; source_file='波林格带和EMA趋势跟踪策略-Bollinger-Bands-and-EMA-Trend-Following-Strategy.md'
    source_defaults={"bb_length":20,"bb_mult":2.0,"ema_period":9,"stop_loss_pct":0.5,"take_profit_pct":1.0,"risk_per_trade":1.0}
    source_qty_type='fixed'; source_qty_value=1.; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=True
    source_fidelity_notes=["bb_offset/ema_offset affect plots only and are omitted from trading defaults.","Qty is computed from current strategy.equity and signal-bar close exactly from capital_at_risk / risk_per_unit.","Stop and target prices are frozen from the signal-bar close, not from eventual fill price."]
    def pine_indicators(self,d,p):
        c=d['close']; basis=ta.pine_sma(c,int(p['bb_length'])); dev=float(p['bb_mult'])*ta.pine_stdev(c,int(p['bb_length']))
        up,lo=basis+dev,basis-dev; ema=ta.pine_ema(c,int(p['ema_period']))
        d['pine_long']=ta.pine_crossover(c,ema)&(c>up); d['pine_short']=ta.pine_crossunder(c,ema)&(c<lo); return d
    def pine_context(self,d,p): return {'c':d['close'].to_numpy(float),'L':d['pine_long'].to_numpy(bool),'S':d['pine_short'].to_numpy(bool),'p':p}
    def pine_script(self,b,i,x):
        c=x['c'][i]; p=x['p']; sl=float(p['stop_loss_pct'])/100.; tp=float(p['take_profit_pct'])/100.; risk=b.equity*float(p['risk_per_trade'])/100.
        unit=abs(c-c*(1-sl)); qty=risk/unit if unit>0 else 0.
        if x['L'][i]:
            b.entry('Long','long',qty=qty); b.exit('Take Profit','Long',limit=c*(1+tp)); b.exit('Stop Loss','Long',stop=c*(1-sl))
        if x['S'][i]:
            b.entry('Short','short',qty=qty); b.exit('Take Profit','Short',limit=c*(1-tp)); b.exit('Stop Loss','Short',stop=c*(1+sl))
