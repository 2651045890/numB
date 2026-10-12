"""Explicit historical OHLC broker subset for reviewed Pine v4/v5 ports.

Calculation at close; market/price orders become eligible on the next bar.
No margin enforcement (v4/v5 default margin=0), no tick replay, no pyramiding,
no partial fills, no synthetic final exit. Unsupported semantics must raise.
Original-platform parity is not certified by this implementation.
"""
from dataclasses import dataclass, asdict
import math


@dataclass(frozen=True)
class BrokerSettings:
    initial_capital: float = 1000000.0
    default_qty_type: str = 'fixed'
    default_qty_value: float = 1.0
    commission_percent: float = 0.0
    slippage_ticks: int = 0
    tick_size: float = 0.01
    quantity_step: float = 0.0
    point_value: float = 1.0
    margin_long: float = 0.0
    margin_short: float = 0.0
    pyramiding: int = 0

    def __post_init__(self):
        if self.pyramiding or self.margin_long or self.margin_short:
            raise NotImplementedError('Nonzero pyramiding/margin requires a separate implementation')
        if self.default_qty_type not in ('fixed','percent_of_equity','cash'):
            raise ValueError('Unsupported quantity mode')
        values=(self.initial_capital,self.default_qty_value,self.commission_percent,
                self.slippage_ticks,self.tick_size,self.quantity_step,self.point_value)
        if not all(math.isfinite(v) for v in values):raise ValueError('Nonfinite broker setting')
        if self.initial_capital<=0 or self.default_qty_value<=0 or self.tick_size<=0 or self.point_value<=0:
            raise ValueError('Capital, size, tick and point value must be positive')
        if self.commission_percent<0 or self.quantity_step<0 or self.slippage_ticks<0 or int(self.slippage_ticks)!=self.slippage_ticks:
            raise ValueError('Invalid fee, precision or slippage')


@dataclass
class Order:
    id: str
    kind: str
    side: int
    qty: float | None
    stop: float | None
    limit: float | None
    from_entry: str | None
    created_bar: int
    created_time: str
    sequence: int


def optional(value):
    return None if value is None or math.isnan(float(value)) else float(value)


class Broker:
    def __init__(self, settings=None):
        self.settings=settings or BrokerSettings()
        self.cash=self.settings.initial_capital
        self.position_size=0.0
        self.position_avg_price=math.nan
        self.entry_id=None
        self.entry_time=None
        self.entry_bar=None
        self.entry_fee=0.0
        self.orders={}
        self.events=[]
        self.fills=[]
        self.trades=[]
        self.bar_index=-1
        self.time=''
        self.mark=math.nan
        self.sequence=0
        self.ambiguous_path_bars=0

    @property
    def equity(self):
        return self.cash+(self.position_size*(self.mark-self.position_avg_price)*self.settings.point_value if self.position_size else 0)

    @property
    def opentrades(self):return int(self.position_size!=0)

    def log(self, event, **data):
        self.events.append(dict(event=event,bar=self.bar_index,time=self.time,**data))

    def _put(self,id,kind,side,qty=None,stop=None,limit=None,from_entry=None):
        qty,stop,limit=optional(qty),optional(stop),optional(limit)
        if qty is not None and (not math.isfinite(qty) or qty<0):raise ValueError('Invalid order quantity')
        if qty==0:
            self.log('ignored_zero_quantity',order_id=id)
            return
        if any(v is not None and (not math.isfinite(v) or v<=0) for v in (stop,limit)):
            raise ValueError('Order prices must be finite and positive')
        if kind=='entry' and stop is not None and limit is not None:
            raise NotImplementedError('Stop-limit entry is not a bracket order')
        self.sequence+=1
        key=(kind,id)
        event='modify' if key in self.orders else 'create'
        order=Order(id,kind,side,qty,stop,limit,from_entry,self.bar_index,self.time,self.sequence)
        self.orders[key]=order
        self.log(event,order=asdict(order))

    def entry(self,id,side,qty=None,stop=None,limit=None):
        if side not in (-1,1):raise ValueError('Entry side must be -1 or +1')
        if self.position_size*side>0:
            self.log('ignored_pyramiding',order_id=id)
            return
        self._put(id,'entry',side,qty,stop,limit)

    def close(self,id,qty=None):
        # strategy.close targets FILLED entry IDs, not an unfilled strategy.entry.
        if self.entry_id==id and self.position_size:
            self._put('close '+id,'close',-1 if self.position_size>0 else 1,
                      abs(self.position_size) if qty is None else qty,from_entry=id)

    def close_all(self):
        if self.position_size:self.close(self.entry_id)

    def exit(self,id,from_entry,stop=None,limit=None):
        matching=self.entry_id==from_entry or ('entry',from_entry) in self.orders
        if not matching:return
        if optional(stop) is None and optional(limit) is None:return
        side=(-1 if self.position_size>0 else 1) if self.entry_id==from_entry else -self.orders[('entry',from_entry)].side
        self._put(id,'exit',side,stop=stop,limit=limit,from_entry=from_entry)

    def cancel(self,id):
        for key in [key for key,order in self.orders.items() if order.id==id]:
            del self.orders[key]
            self.log('cancel',order_id=id)

    def _eligible(self,order):
        if order.created_bar>=self.bar_index:return False
        if order.kind!='entry':return self.entry_id==order.from_entry and self.position_size!=0
        return True

    def _trigger(self,order,start,end):
        if order.stop is None and order.limit is None:return (0.0,start,'market')
        candidates=[]
        # A stop buy triggers above; limit buy triggers below. Sells reverse it.
        for label,level,above in [('stop',order.stop,order.side==1),('limit',order.limit,order.side==-1)]:
            if level is None:continue
            if (start>=level if above else start<=level):
                candidates.append((0.0,start,label))
            elif (end>=level if above else end<=level):
                candidates.append((abs(level-start),level,label))
        return min(candidates) if candidates else None

    def _quantity(self,order,rate):
        if order.qty is not None:return order.qty
        s=self.settings
        if s.default_qty_type=='fixed':quantity=s.default_qty_value
        elif s.default_qty_type=='cash':quantity=s.default_qty_value/(rate*s.point_value)
        else:quantity=self.equity*s.default_qty_value/100/(rate*s.point_value)
        if s.quantity_step:quantity=math.floor(quantity/s.quantity_step+1e-12)*s.quantity_step
        return quantity

    def _close_position(self,qty,rate,fee,order_id):
        qty=min(qty,abs(self.position_size))
        direction=1 if self.position_size>0 else -1
        ratio=qty/abs(self.position_size)
        entry_fee=self.entry_fee*ratio
        pnl=direction*qty*(rate-self.position_avg_price)*self.settings.point_value
        self.cash+=pnl-fee
        self.trades.append(dict(entry_id=self.entry_id,exit_id=order_id,side='long' if direction==1 else 'short',
            quantity=qty,entry_time=self.entry_time,exit_time=self.time,entry_bar=self.entry_bar,exit_bar=self.bar_index,
            entry_price=self.position_avg_price,exit_price=rate,pnl_gross=pnl,fees=entry_fee+fee,pnl_net=pnl-entry_fee-fee))
        self.entry_fee-=entry_fee
        self.position_size-=direction*qty
        if abs(self.position_size)<1e-12:
            old_id=self.entry_id
            self.position_size=0.0;self.position_avg_price=math.nan;self.entry_id=None
            for key in [key for key,o in self.orders.items() if o.kind!='entry' and o.from_entry==old_id]:
                del self.orders[key]
                self.log('cancel_after_close',order_id=key[1])

    def _fill(self,key,rate,trigger):
        order=self.orders.pop(key)
        if order.kind=='entry' and order.side*self.position_size>0:
            self.log('ignored_pyramiding_at_fill',order_id=order.id)
            return
        if trigger!='limit':rate+=order.side*self.settings.slippage_ticks*self.settings.tick_size
        if rate<=0:raise ValueError('Slippage caused a nonpositive price')
        self.mark=rate
        qty=self._quantity(order,rate) if order.kind=='entry' else min(order.qty or abs(self.position_size),abs(self.position_size))
        if not math.isfinite(qty) or qty<=0:
            self.log('reject_nonpositive_quantity',order_id=order.id,quantity=qty)
            return
        if order.kind=='entry' and self.settings.quantity_step:
            qty=math.floor(qty/self.settings.quantity_step+1e-12)*self.settings.quantity_step
            if qty<=0:
                self.log('reject_quantity_precision',order_id=order.id)
                return
        previous=self.position_size
        closing=abs(previous) if order.kind=='entry' and previous*order.side<0 else (qty if order.kind!='entry' else 0.0)
        opening=qty if order.kind=='entry' else 0.0
        unit_fee=rate*self.settings.point_value*self.settings.commission_percent/100
        if closing:self._close_position(closing,rate,closing*unit_fee,order.id)
        if opening:
            self.cash-=opening*unit_fee
            self.position_size=order.side*opening
            self.position_avg_price=rate
            self.entry_id=order.id
            self.entry_time=self.time;self.entry_bar=self.bar_index;self.entry_fee=opening*unit_fee
        fill=dict(order_id=order.id,kind=order.kind,trigger=trigger,side='buy' if order.side==1 else 'sell',
            quantity=closing+opening,price=rate,fee=(closing+opening)*unit_fee,signal_bar=order.created_bar,
            signal_time=order.created_time,fill_bar=self.bar_index,fill_time=self.time,
            position_before=previous,position_after=self.position_size)
        self.fills.append(fill);self.log('fill',**fill)

    def _segment(self,start,end):
        current=start
        while True:
            candidates=[]
            for key,order in self.orders.items():
                if not self._eligible(order):continue
                trigger=self._trigger(order,current,end)
                if trigger:candidates.append((trigger[0],order.sequence,key,trigger[1],trigger[2]))
            if not candidates:break
            _,_,key,price,kind=min(candidates)
            self._fill(key,price,kind)
            current=price

    def advance(self,bar_index,bar):
        self.bar_index=bar_index;self.time=bar.date.isoformat();self.mark=float(bar.open)
        o,h,l,c=map(float,(bar.open,bar.high,bar.low,bar.close))
        if not all(math.isfinite(v) and v>0 for v in (o,h,l,c)) or h<max(o,l,c) or l>min(o,h,c):
            raise ValueError('Invalid OHLC bar')
        # Gap-crossed orders fill at OPEN, not at the stop/limit inside the gap.
        self._segment(o,o)
        if abs(h-o)==abs(o-l):self.ambiguous_path_bars+=1
        path=(o,h,l,c) if abs(h-o)<abs(o-l) else (o,l,h,c)
        for start,end in zip(path,path[1:]):self._segment(start,end)
        self.mark=c
