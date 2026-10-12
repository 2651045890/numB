"""Deep Pine v5 port of the EMA crossover DCA/dual trailing script.

Important source bug preserved: strategy() never enables pyramiding and
baseEntryPrice is assigned on the signal bar but reset later on the SAME bar
because strategy.position_size is still zero until the next-bar fill.  Thus the
safety-order path is effectively disabled in normal Pine execution.  A shallow
port that lets SO1/SO2 fill would materially change the strategy.
"""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase
class SMB010_012_SmartDCA(PinePortBase, IStrategy):
    timeframe='1d'; can_short=False; source_file='指数移动平均交叉智能定投链式止损跟踪系统-EMA-Crossover-Smart-DCA-with-Dual-Trailing-Stop-System.md'
    source_defaults={"fastMALen":9,"slowMALen":21,"trailStopPerc":0.08,"lockInThreshold":0.025,"lockInTrailPct":0.015,"useATRSpacing":True,"atrLength":14,"atrSo1Multiplier":1.2,"atrSo2Multiplier":2.5,"fallbackSo1Perc":0.04,"fallbackSo2Perc":0.08,"cooldownBars":4,"baseUsd":1000.,"so1Usd":1250.,"so2Usd":1750.}
    source_qty_type='fixed'; source_qty_value=0.; source_initial_capital=4000.; source_pyramiding=0; source_commission_percent=0.1; source_reproduce_stops=False
    source_fidelity_notes=["CRITICAL SOURCE BUG: baseEntryPrice is reset to na on the entry signal bar before the order fills, so safety-order trigger prices remain na afterward.","CRITICAL SOURCE LIMIT: pyramiding is left at Pine default 0, which would reject additional same-direction strategy.entry calls even if baseEntryPrice survived.","useDateFilter is declared but no actual inDateRange expression exists in the source; date filtering is therefore a no-op.","Trailing exits are close-based strategy.close_all conditions, not resting stop orders; reproduced as market close signals."]
    def pine_indicators(self,d,p):
        f=ta.pine_ema(d['close'],int(p['fastMALen'])); s=ta.pine_ema(d['close'],int(p['slowMALen']))
        d['pine_up']=ta.pine_crossover(f,s); d['pine_down']=ta.pine_crossunder(f,s); d['pine_atr']=ta.pine_atr(d,int(p['atrLength'])); return d
    def pine_context(self,d,p): return {'c':d['close'].to_numpy(float),'up':d['pine_up'].to_numpy(bool),'down':d['pine_down'].to_numpy(bool),'atr':d['pine_atr'].to_numpy(float),'p':p}
    def pine_script(self,b,i,x):
        if not hasattr(self,'_dca_state'):
            self._dca_state={'last_buy':None,'base':None,'high':None,'lock':False,'lock_peak':None}
        s=self._dca_state; p=x['p']; c=x['c'][i]
        cooldown=s['last_buy'] is not None and (i-s['last_buy']<int(p['cooldownBars']))
        if x['up'][i] and b.position_size==0 and not cooldown:
            b.entry('Base Order','long',qty=float(p['baseUsd'])/c); s['base']=c; s['last_buy']=i
        # These conditions are coded faithfully, although base is normally reset below on the entry signal bar.
        if s['base'] is not None and b.position_size>0:
            a=x['atr'][i]
            so1=s['base']-a*float(p['atrSo1Multiplier']) if p['useATRSpacing'] else s['base']*(1-float(p['fallbackSo1Perc']))
            so2=s['base']-a*float(p['atrSo2Multiplier']) if p['useATRSpacing'] else s['base']*(1-float(p['fallbackSo2Perc']))
            if c<=so1 and b.open_trades==1: b.entry('Safety Order 1','long',qty=float(p['so1Usd'])/c)
            if c<=so2 and b.open_trades==2: b.entry('Safety Order 2','long',qty=float(p['so2Usd'])/c)
        if b.position_size>0:
            s['high']=c if s['high'] is None else max(s['high'],c); normal=c < s['high']*(1-float(p['trailStopPerc']))
            avg=b.position_avg_price
            if not s['lock'] and c>=avg*(1+float(p['lockInThreshold'])): s['lock']=True; s['lock_peak']=c
            lock_hit=False
            if s['lock']:
                s['lock_peak']=max(s['lock_peak'],c); lock_hit=c < s['lock_peak']*(1-float(p['lockInTrailPct']))
            if normal or lock_hit or x['down'][i]: b.close_all()
        else:
            # Exact placement in source: this runs on the signal bar before entry fills and erases baseEntryPrice.
            s['high']=None; s['lock']=False; s['lock_peak']=None; s['base']=None
