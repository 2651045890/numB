"""Line-by-line semantic Python port of the FMZ profit-statistics utility.

This is not a trading strategy; it records cumulative profit snapshots and
computes 1/7/30-day and lifetime return/drawdown summaries.  The storage layer
is made explicit so it can be used in normal Python or adapted to FMZ _G().
"""
from __future__ import annotations
from dataclasses import dataclass
from time import time
from typing import MutableMapping
import json

@dataclass
class PeriodProfit:
    profit: float; expected_profit: float; profit_time: int; period_time: int
    open: float; close: float; drawback: float; drawback_profit: float

class ProfitStats:
    def __init__(self, store: MutableMapping[str,str]|None=None): self.store=store if store is not None else {}
    def get_all_profit(self):
        try: return json.loads(self.store.get('profit_history','[]'))
        except Exception: self.store.pop('profit_history',None); return []
    def log_profit(self, profit: float, timestamp: int|None=None):
        h=self.get_all_profit(); h.append([int(time()) if timestamp is None else int(timestamp),float(profit)]); self.store['profit_history']=json.dumps(h); return profit
    def filter_profit(self, from_ts:int, to_ts:int):
        arr=self.get_all_profit(); earliest=latest=None; max_profit=None; max_dd=0.; max_dd_profit=0.
        for row in arr:
            if not row: continue
            ts,p=row
            if ts>from_ts and ts<=to_ts:
                if earliest is None: earliest=row
                latest=row; max_profit=p if max_profit is None or p>max_profit else max_profit
                dd=max_profit-p
                if dd>max_dd: max_dd,max_dd_profit=dd,max_profit
        if earliest is None or latest is None: return None
        return earliest,latest,max_dd,max_dd_profit
    @staticmethod
    def day_second(days:int, now:int|None=None): return int((time() if now is None else now)-days*86400)
    def days_profit(self, offset:int, days:int, now:int|None=None):
        frm=self.day_second(-offset+days,now); to=self.day_second(-offset,now); arr=self.filter_profit(frm,to)
        if not arr: return None
        earliest,latest,dd,ddp=arr; pt=int(latest[0]-earliest[0])
        if not pt: return None
        period=to-frm; profit=float(latest[1]-earliest[1]); real_pct=pt*100/period
        return PeriodProfit(profit,profit*100/real_pct,pt,period,float(earliest[1]),float(latest[1]),dd,ddp)
    @staticmethod
    def expect_profit(p:PeriodProfit, days:int, base:float):
        sec=days*86400
        if sec<p.profit_time: return None
        return {'profit':round(p.profit*sec/p.profit_time,2),'percent':round(p.profit*sec*100/(p.profit_time*(base+p.open)),3)}
    def period_summary(self,p:PeriodProfit|None,base:float):
        if not p: return ''
        parts=[f'收{p.profit:.2f}元({p.profit*100/(base+p.open):.3f}%)']
        m=self.expect_profit(p,30,base); y=self.expect_profit(p,365,base)
        if m: parts.append(f"月化{m['percent']}%")
        if y: parts.append(f"年化{y['percent']}%")
        parts.append(f'回撤{p.drawback*100/(p.drawback_profit+base):.3f}%'); return '，'.join(parts)
    def profit_summary(self, initial_balance:float, now:int|None=None):
        if not initial_balance: return '没有传入初始资金'
        day=self.days_profit(0,1,now); last_day=self.days_profit(-1,1,now); week=self.days_profit(0,7,now); last_week=self.days_profit(-7,7,now); month=self.days_profit(0,30,now); last_month=self.days_profit(-30,30,now); allp=self.days_profit(0,10000,now)
        if not allp: return ''
        days=allp.profit_time//86400; rows=[]
        for label,p,gate in [('1日',day,True),('上1日',last_day,True),('7日',week,days>=7),('上7日',last_week,True),('30日',month,days>=30),('上30日',last_month,True)]:
            s=self.period_summary(p,initial_balance)
            if s and gate: rows.append(f'{label}: {s}')
        hours=(allp.profit_time%86400)//3600; dd=allp.drawback*100/(allp.drawback_profit+initial_balance)
        rows.append(f'总: 收{allp.close:.2f}元({allp.close*100/initial_balance:.3f}%)，最大回撤{dd:.3f}%，统计时间{days}天{hours}小时')
        return '\n'.join(rows)
