"""Deep Pine v4 port of ADX/TSI/Bollinger Trend Chaser. Source is long-only."""
import numpy as np
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_015_TrendChaser(PinePortBase, IStrategy):
    timeframe='1d'; can_short=False; source_file='带状趋势追踪者Bollinger-Band-Trend-Chaser.md'
    source_defaults={"length":20,"mult":0.382,"MAlen":200,"TSlong":25,"TSshort":13,"TSsignal":52,"adxlen":13,"dilen":13}
    source_qty_type='percent_of_equity'; source_qty_value=10.; source_initial_capital=10000.; source_pyramiding=0; source_commission_percent=0.1; source_reproduce_stops=False
    source_fidelity_notes=["Sell/short conditions are calculated but never sent to strategy.entry; port is long-only.","Long1 intentionally compares current close with upper[5] AND close[5] with upper[6], not five consecutive closes; preserved.","No stop-loss exists despite prose mentioning one as possible future optimization."]
    def pine_indicators(self,d,p):
        c=d['close']; basis=ta.pine_sma(c,int(p['length'])); upper=basis+float(p['mult'])*ta.pine_stdev(c,int(p['length'])); ma=ta.pine_sma(c,int(p['MAlen']))
        pc=ta.pine_change(c); ds=ta.pine_wma(ta.pine_wma(pc,int(p['TSlong'])),int(p['TSshort'])); da=ta.pine_wma(ta.pine_wma(pc.abs(),int(p['TSlong'])),int(p['TSshort'])); tsi=100*ds/da; tsi2=ta.pine_wma(tsi,int(p['TSsignal']))
        up=ta.pine_change(d['high']); down=-ta.pine_change(d['low']); plus=up.where((up>down)&(up>0),0.0); minus=down.where((down>up)&(down>0),0.0)
        tr=ta.pine_rma(ta.pine_tr(d,handle_na=False),int(p['dilen'])); pdi=100*ta.pine_rma(plus,int(p['dilen']))/tr; mdi=100*ta.pine_rma(minus,int(p['dilen']))/tr; den=(pdi+mdi).replace(0,1); adx=100*ta.pine_rma((pdi-mdi).abs()/den,int(p['adxlen']))
        buy=(c>upper.shift(5))&(c.shift(5)>upper.shift(6))&(c>=ma.shift(1))&(tsi>tsi2)&(adx>20)&(adx<100)
        d['pine_buy']=buy; d['pine_close']=ta.pine_crossunder(tsi,tsi2); return d
    def pine_context(self,d,p): return {'b':d['pine_buy'].to_numpy(bool),'x':d['pine_close'].to_numpy(bool)}
    def pine_script(self,b,i,x):
        b.entry('Long','long',when=x['b'][i]); b.close('Long',when=x['x'][i])
