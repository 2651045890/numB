"""Deep Python/Freqtrade-style port of the FMZ multi-exchange ATR strategy.

The FMZ script runs the SAME channel logic independently over multiple futures
exchange objects.  A Freqtrade strategy instance is pair-local, so this file
reproduces the per-symbol trading algorithm exactly; portfolio orchestration,
FMZ Chart(), _G persistence and exchange.SetContractType are platform plumbing
and intentionally not mixed into signal generation.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

class SMB010_007_FMZMultiAssetATR(PinePortBase, IStrategy):
    timeframe='1d'; can_short=True; source_file='数字货币期货多品种ATR策略教学.md'
    source_defaults={"stopLoss":0.07,"atrPeriod":10,"emaPeriod":20,"trackRatio":2.0,"openRatio":0.1}
    source_qty_type='fixed'; source_qty_value=10.0; source_initial_capital=1_000_000.; source_pyramiding=0; source_commission_percent=0.; source_reproduce_stops=False
    source_fidelity_notes=[
        "FMZ executes each exchange independently; this class is the exact per-pair algorithm and should be instantiated for each pair.",
        "The source parameter openRatio is never used; order size is hard-coded as 10 in $.OpenLong/$.OpenShort. Preserved.",
        "Chart drawing, _G persistence, SetContractType and Sleep are execution-platform plumbing and have no effect on historical signals.",
        "FMZ evaluates the just-closed bar when a new bar appears. Computing a close crossover on each bar and filling on the next bar reproduces that timing model in the offline engine."
    ]
    def pine_indicators(self,d,p):
        typical=(d['high']+d['low']+d['close'])/3.0
        mid=ta.pine_ema(typical,int(p['emaPeriod']))
        atr=ta.pine_atr(d,int(p['atrPeriod']))
        up=mid+float(p['trackRatio'])*atr; down=mid-float(p['trackRatio'])*atr
        c=d['close']
        d['pine_mid']=mid; d['pine_up']=up; d['pine_down']=down
        d['pine_cross_up']=(c.shift(1)<up.shift(1))&(c>up)
        d['pine_cross_down']=(c.shift(1)>down.shift(1))&(c<down)
        return d
    def pine_context(self,d,p):
        return {'close':d['close'].to_numpy(float),'mid':d['pine_mid'].to_numpy(float),
                'up':d['pine_cross_up'].to_numpy(bool),'down':d['pine_cross_down'].to_numpy(bool),
                'stop':float(p['stopLoss'])}
    def pine_script(self,b,i,x):
        c=x['close'][i]; mid=x['mid'][i]
        if x['up'][i] and b.position_size<=0:
            if b.position_size<0: b.close('ATR Short')
            b.entry('ATR Long','long',qty=10.0)
        elif x['down'][i] and b.position_size>=0:
            if b.position_size>0: b.close('ATR Long')
            b.entry('ATR Short','short',qty=10.0)
        else:
            if b.position_size>0 and (c<=b.position_avg_price*(1-x['stop']) or c<=mid): b.close('ATR Long')
            elif b.position_size<0 and (c>=b.position_avg_price*(1+x['stop']) or c>=mid): b.close('ATR Short')
