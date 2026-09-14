"""Exact OU funding signal core from aayanvatsa04/btc-perpetual-funding-arbitrage."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class OUParams:
    theta:float; mu:float; sigma:float; sigma_eq:float; half_life:float

def fit_ou(rates) -> OUParams:
    r=np.asarray(rates,dtype=float)
    if len(r)<30: raise ValueError("OU fit requires at least 30 observations")
    x,y=r[:-1],r[1:]; xm,ym=x.mean(),y.mean(); var=np.sum((x-xm)**2)
    if var==0: raise ValueError("constant funding series")
    b=float(np.clip(np.sum((x-xm)*(y-ym))/var,1e-6,1-1e-6)); a=ym-b*xm
    theta=-np.log(b); mu=a/(1-b); residual=y-(a+b*x); sigma=float(residual.std(ddof=2)); sigma_eq=sigma/np.sqrt(1-b*b)
    return OUParams(float(theta),float(mu),sigma,float(sigma_eq),float(np.log(2)/theta))

def rolling_ou(rates:pd.Series,window:int=90)->pd.DataFrame:
    rows=[]
    for i,v in enumerate(rates):
        if i<window: rows.append((np.nan,)*6); continue
        try:
            p=fit_ou(rates.iloc[i-window:i].values); z=0.0 if p.sigma_eq==0 else (float(v)-p.mu)/p.sigma_eq
            rows.append((z,p.theta,p.mu,p.sigma,p.sigma_eq,p.half_life))
        except (ValueError,ZeroDivisionError,FloatingPointError): rows.append((np.nan,)*6)
    return pd.DataFrame(rows,index=rates.index,columns=["z_score","theta","mu","sigma","sigma_eq","half_life"])

@dataclass(frozen=True)
class FundingDecision:
    action:str; perp_side:str|None; spot_side:str|None; reason:str

def basis_bps(perp:float,spot:float)->float: return 0.0 if spot==0 else (perp-spot)/spot*10000

def entry_decision(z:float,funding:float,perp:float,spot:float,entry_z=2.0,fee_bps=5.5,min_periods=3,notional=1000.0,max_basis=50.0)->FundingDecision:
    if not np.isfinite(z) or abs(z)<=entry_z:return FundingDecision("hold",None,None,"z_threshold")
    fees=4*(fee_bps/10000)*notional
    if abs(funding)*notional*min_periods<=fees:return FundingDecision("hold",None,None,"fee_gate")
    if abs(basis_bps(perp,spot))>max_basis:return FundingDecision("hold",None,None,"basis_gate")
    return FundingDecision("enter","short" if z>0 else "long","long" if z>0 else "short","ou_extreme")

def exit_decision(z:float,periods:int,current_basis:float,entry_basis:float,side:str,daily_pnl:float,exit_z=.75,max_periods=21,max_basis_change=100.0,daily_loss_limit=100.0)->str|None:
    if daily_pnl<=-daily_loss_limit:return "daily_loss_limit"
    change=current_basis-entry_basis
    adverse=(side=="short" and change>max_basis_change) or (side=="long" and change < -max_basis_change)
    if adverse:return "basis_stop"
    if periods>=max_periods:return "max_holding_periods"
    if abs(z)<exit_z:return "z_reversion"
    return None
