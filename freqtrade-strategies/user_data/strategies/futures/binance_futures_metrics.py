"""Lookahead-safe adapter for Binance futures auxiliary metrics.

Set BINANCE_FUTURES_METRICS_DIR to a directory containing per-symbol files:
  candles/BTCUSDT_5m.parquet  (taker_buy_volume, volume, date/open_time)
  metrics/BTCUSDT_metrics.parquet (open_interest, taker_ls_vol_ratio, date/create_time)
Files may also be CSV. Values are merged backward, never from the future.
"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd

def _symbol(pair: str) -> str:
    return pair.split(":",1)[0].replace("/","").replace("-","")

def _read(base: Path, stems: list[str]) -> pd.DataFrame | None:
    for stem in stems:
        for suffix in (".parquet", ".csv"):
            p=base/(stem+suffix)
            if p.exists():
                return pd.read_parquet(p) if suffix==".parquet" else pd.read_csv(p)
    return None

def _dated(df: pd.DataFrame, names: tuple[str,...]) -> pd.DataFrame:
    for n in names:
        if n in df.columns:
            out=df.copy(); out["date"]=pd.to_datetime(out[n],utc=True); return out.sort_values("date")
    if isinstance(df.index,pd.DatetimeIndex):
        out=df.reset_index(); out["date"]=pd.to_datetime(out.iloc[:,0],utc=True); return out.sort_values("date")
    raise ValueError("Auxiliary metrics file has no timestamp column")

def merge_aux(dataframe: pd.DataFrame, pair: str, timeframe: str) -> pd.DataFrame:
    out=dataframe.sort_values("date").copy(); root=os.environ.get("BINANCE_FUTURES_METRICS_DIR")
    if not root:
        for c in ("buy_ratio","open_interest","taker_ls_vol_ratio"): out[c]=float("nan")
        return out
    base=Path(root); sym=_symbol(pair)
    candles=_read(base,[f"candles/{sym}_{timeframe}",f"raw/{timeframe}/{sym}_{timeframe}"])
    if candles is not None:
        candles=_dated(candles,("date","open_time"))
        if "buy_ratio" not in candles and {"taker_buy_volume","volume"}<=set(candles):
            candles["buy_ratio"]=candles.taker_buy_volume/candles.volume.replace(0,float("nan"))
        if "buy_ratio" in candles:
            out=pd.merge_asof(out,candles[["date","buy_ratio"]],on="date",direction="backward")
    if "buy_ratio" not in out: out["buy_ratio"]=float("nan")
    metrics=_read(base,[f"metrics/{sym}_metrics",f"raw/metrics/{sym}_metrics"])
    if metrics is not None:
        metrics=_dated(metrics,("date","create_time"))
        metrics=metrics.rename(columns={"sum_open_interest":"open_interest","sum_taker_long_short_vol_ratio":"taker_ls_vol_ratio"})
        cols=[c for c in ("open_interest","taker_ls_vol_ratio") if c in metrics]
        out=pd.merge_asof(out,metrics[["date",*cols]],on="date",direction="backward")
    for c in ("open_interest","taker_ls_vol_ratio"):
        if c not in out: out[c]=float("nan")
    return out

