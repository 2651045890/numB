from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from pandas import DataFrame

from freqtrade.strategy import IStrategy


@dataclass
class Signal:
    timestamp: datetime
    symbol: str
    side: str
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    position_size_pct: float
    confidence: float
    reasons: List[str] = field(default_factory=list)
    ob_level: Optional[float] = None
    fvg_level: Optional[float] = None
    poc_level: Optional[float] = None
    sweep_level: Optional[float] = None
    market_structure: str = "unknown"


@dataclass
class ConfluenceZone:
    timestamp: datetime
    zone_type: str
    zone_high: float
    zone_low: float
    zone_mid: float
    source_type: str
    factors: List[str]
    factor_count: int
    market_structure: str


def detect_swing_high_low(df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False
    for i in range(lookback, len(df) - lookback):
        if df["high"].iloc[i] == max(df["high"].iloc[i - lookback:i + lookback + 1]):
            if df["high"].iloc[i] > df["high"].iloc[i - lookback] and df["high"].iloc[i] > df["high"].iloc[i + lookback]:
                df.loc[df.index[i], "swing_high"] = True
        if df["low"].iloc[i] == min(df["low"].iloc[i - lookback:i + lookback + 1]):
            if df["low"].iloc[i] < df["low"].iloc[i - lookback] and df["low"].iloc[i] < df["low"].iloc[i + lookback]:
                df.loc[df.index[i], "swing_low"] = True
    return df


def detect_bos(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    df = df.copy()
    df["bos_bullish"] = False
    df["bos_bearish"] = False
    swing_highs = df[df["swing_high"]].index
    swing_lows = df[df["swing_low"]].index
    for i in range(1, len(df)):
        recent_highs = swing_highs[swing_highs < i]
        if len(recent_highs) > 0:
            last_high_idx = recent_highs[-1]
            if df["high"].iloc[i] > df["high"].iloc[last_high_idx] and i - last_high_idx <= lookback:
                df.loc[df.index[i], "bos_bullish"] = True
        recent_lows = swing_lows[swing_lows < i]
        if len(recent_lows) > 0:
            last_low_idx = recent_lows[-1]
            if df["low"].iloc[i] < df["low"].iloc[last_low_idx] and i - last_low_idx <= lookback:
                df.loc[df.index[i], "bos_bearish"] = True
    return df


def detect_market_structure(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["market_structure"] = "ranging"
    swing_highs_idx = df[df["swing_high"]].index.tolist()
    swing_lows_idx = df[df["swing_low"]].index.tolist()
    for i in range(1, len(df)):
        recent_highs = [h for h in swing_highs_idx if h < i]
        recent_lows = [l for l in swing_lows_idx if l < i]
        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            hh = df["high"].iloc[recent_highs[-1]] > df["high"].iloc[recent_highs[-2]]
            hl = df["low"].iloc[recent_lows[-1]] > df["low"].iloc[recent_lows[-2]]
            lh = df["high"].iloc[recent_highs[-1]] < df["high"].iloc[recent_highs[-2]]
            ll = df["low"].iloc[recent_lows[-1]] < df["low"].iloc[recent_lows[-2]]
            if hh and hl:
                df.loc[df.index[i], "market_structure"] = "uptrend"
            elif lh and ll:
                df.loc[df.index[i], "market_structure"] = "downtrend"
    return df


def detect_chooch(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["chooch_bullish"] = False
    df["chooch_bearish"] = False
    for i in range(1, len(df)):
        start = max(0, i - 30)
        prev_structure = df["market_structure"].iloc[start:i].value_counts()
        if df["bos_bullish"].iloc[i]:
            if prev_structure.get("downtrend", 0) > prev_structure.get("uptrend", 0) and prev_structure.get("downtrend", 0) >= 5:
                df.loc[df.index[i], "chooch_bullish"] = True
        if df["bos_bearish"].iloc[i]:
            if prev_structure.get("uptrend", 0) > prev_structure.get("downtrend", 0) and prev_structure.get("uptrend", 0) >= 5:
                df.loc[df.index[i], "chooch_bearish"] = True
    return df


def detect_order_blocks(df: pd.DataFrame, min_body_bps: float = 5.0) -> pd.DataFrame:
    df = df.copy()
    df["bullish_ob_top"] = np.nan
    df["bullish_ob_bottom"] = np.nan
    df["bearish_ob_top"] = np.nan
    df["bearish_ob_bottom"] = np.nan
    for i in range(2, len(df) - 1):
        prev_body = df["close"].iloc[i - 1] - df["open"].iloc[i - 1]
        curr_body = df["close"].iloc[i] - df["open"].iloc[i]
        if df["close"].iloc[i - 1] < df["open"].iloc[i - 1] and curr_body > 0 and abs(curr_body) > abs(prev_body) * 1.5:
            body_size_bps = (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) / df["close"].iloc[i - 1] * 10000
            if body_size_bps >= min_body_bps:
                df.loc[df.index[i], "bullish_ob_top"] = max(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
                df.loc[df.index[i], "bullish_ob_bottom"] = min(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
        if df["close"].iloc[i - 1] > df["open"].iloc[i - 1] and curr_body < 0 and abs(curr_body) > abs(prev_body) * 1.5:
            body_size_bps = (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) / df["close"].iloc[i - 1] * 10000
            if body_size_bps >= min_body_bps:
                df.loc[df.index[i], "bearish_ob_top"] = max(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
                df.loc[df.index[i], "bearish_ob_bottom"] = min(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
    return df


def detect_fvg(df: pd.DataFrame, min_gap_bps: float = 3.0) -> pd.DataFrame:
    df = df.copy()
    df["bullish_fvg_top"] = np.nan
    df["bullish_fvg_bottom"] = np.nan
    df["bearish_fvg_top"] = np.nan
    df["bearish_fvg_bottom"] = np.nan
    for i in range(2, len(df)):
        if df["high"].iloc[i - 2] < df["low"].iloc[i]:
            gap_bps = (df["low"].iloc[i] - df["high"].iloc[i - 2]) / df["close"].iloc[i] * 10000
            if gap_bps >= min_gap_bps:
                df.loc[df.index[i], "bullish_fvg_top"] = df["low"].iloc[i]
                df.loc[df.index[i], "bullish_fvg_bottom"] = df["high"].iloc[i - 2]
        if df["low"].iloc[i - 2] > df["high"].iloc[i]:
            gap_bps = (df["low"].iloc[i - 2] - df["high"].iloc[i]) / df["close"].iloc[i] * 10000
            if gap_bps >= min_gap_bps:
                df.loc[df.index[i], "bearish_fvg_top"] = df["low"].iloc[i - 2]
                df.loc[df.index[i], "bearish_fvg_bottom"] = df["high"].iloc[i]
    return df


def detect_liquidity_levels(df: pd.DataFrame, lookback: int = 50) -> pd.DataFrame:
    df = df.copy()
    df["bsl_level"] = np.nan
    df["ssl_level"] = np.nan
    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        bsl = window["high"].max()
        ssl = window["low"].min()
        if bsl > df["high"].iloc[i]:
            df.loc[df.index[i], "bsl_level"] = bsl
        if ssl < df["low"].iloc[i]:
            df.loc[df.index[i], "ssl_level"] = ssl
    return df


def detect_liquidity_sweep(df: pd.DataFrame, tolerance_bps: float = 2.0) -> pd.DataFrame:
    df = df.copy()
    df["sweep_bullish"] = False
    df["sweep_bearish"] = False
    df["sweep_low"] = np.nan
    df["sweep_high"] = np.nan
    for i in range(1, len(df) - 1):
        if not pd.isna(df["ssl_level"].iloc[i - 1]):
            ssl = df["ssl_level"].iloc[i - 1]
            if df["low"].iloc[i] < ssl and df["close"].iloc[i] > ssl:
                bps_below = (ssl - df["low"].iloc[i]) / ssl * 10000
                if bps_below <= tolerance_bps * 3:
                    df.loc[df.index[i], "sweep_bullish"] = True
                    df.loc[df.index[i], "sweep_low"] = df["low"].iloc[i]
        if not pd.isna(df["bsl_level"].iloc[i - 1]):
            bsl = df["bsl_level"].iloc[i - 1]
            if df["high"].iloc[i] > bsl and df["close"].iloc[i] < bsl:
                bps_above = (df["high"].iloc[i] - bsl) / bsl * 10000
                if bps_above <= tolerance_bps * 3:
                    df.loc[df.index[i], "sweep_bearish"] = True
                    df.loc[df.index[i], "sweep_high"] = df["high"].iloc[i]
    return df


def compute_full_smc(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    df = df.copy()
    df = detect_swing_high_low(df, lookback=config.get("swing_lookback", 5))
    df = detect_bos(df, lookback=config.get("bos_lookback", 20))
    df = detect_market_structure(df)
    df = detect_chooch(df)
    df = detect_order_blocks(df, min_body_bps=config.get("min_ob_size_bps", 5))
    df = detect_fvg(df, min_gap_bps=config.get("fvg_min_gap_bps", 3))
    df = detect_liquidity_levels(df, lookback=config.get("liquidity_lookback", 50))
    df = detect_liquidity_sweep(df, tolerance_bps=config.get("sweep_tolerance_bps", 2))
    return df


def compute_daily_volume_profile(df: pd.DataFrame, num_bins: int = 24, value_area_pct: float = 0.70, hvn_threshold: float = 1.5) -> Dict:
    if df.empty or len(df) < 5:
        return {}
    high = df["high"].max()
    low = df["low"].min()
    price_range = high - low
    if price_range == 0:
        return {}
    bin_size = price_range / num_bins
    bins = [low + i * bin_size for i in range(num_bins + 1)]
    bin_centers = [(bins[i] + bins[i + 1]) / 2 for i in range(num_bins)]
    volume_profile = np.zeros(num_bins)
    for _, row in df.iterrows():
        o, h, l, c, v = row["open"], row["high"], row["low"], row["close"], row["volume"]
        if v == 0 or np.isnan(v):
            continue
        bar_low = min(l, o)
        bar_high = max(h, c)
        start_bin = max(0, int((bar_low - low) / bin_size))
        end_bin = min(num_bins - 1, int((bar_high - low) / bin_size))
        if end_bin < start_bin:
            start_bin, end_bin = end_bin, start_bin
        num_bins_covered = end_bin - start_bin + 1
        if num_bins_covered > 0:
            vol_per_bin = v / num_bins_covered
            for b in range(start_bin, end_bin + 1):
                volume_profile[b] += vol_per_bin
    total_volume = volume_profile.sum()
    if total_volume == 0:
        return {}
    poc_idx = int(np.argmax(volume_profile))
    poc = bin_centers[poc_idx]
    sorted_indices = [poc_idx]
    left = poc_idx - 1
    right = poc_idx + 1
    while left >= 0 or right < num_bins:
        if left >= 0 and right < num_bins:
            if volume_profile[left] >= volume_profile[right]:
                sorted_indices.append(left)
                left -= 1
            else:
                sorted_indices.append(right)
                right += 1
        elif left >= 0:
            sorted_indices.append(left)
            left -= 1
        elif right < num_bins:
            sorted_indices.append(right)
            right += 1
    cum_vol = 0
    va_low_idx = poc_idx
    va_high_idx = poc_idx
    target_vol = total_volume * value_area_pct
    for idx in sorted_indices:
        cum_vol += volume_profile[idx]
        va_low_idx = min(va_low_idx, idx)
        va_high_idx = max(va_high_idx, idx)
        if cum_vol >= target_vol:
            break
    val = bin_centers[va_low_idx] - bin_size / 2
    vah = bin_centers[va_high_idx] + bin_size / 2
    avg_volume_per_bin = total_volume / num_bins
    hvn_levels = []
    for i in range(num_bins):
        if volume_profile[i] >= avg_volume_per_bin * hvn_threshold:
            hvn_levels.append(bin_centers[i])
    return {"poc": poc, "val": val, "vah": vah, "hvn_levels": hvn_levels}


def _find_nearest_swing_high_low(htf_df: pd.DataFrame, timestamp: datetime) -> tuple:
    before = htf_df[htf_df["timestamp"] <= timestamp].copy()
    if before.empty:
        return None, None
    recent_high = None
    if "swing_high" in before.columns:
        swing_highs = before[before["swing_high"] == True]
        if not swing_highs.empty:
            recent_high = float(swing_highs.iloc[-1]["high"])
    recent_low = None
    if "swing_low" in before.columns:
        swing_lows = before[before["swing_low"] == True]
        if not swing_lows.empty:
            recent_low = float(swing_lows.iloc[-1]["low"])
    return recent_high, recent_low


def collect_all_zones(htf_df: pd.DataFrame, vp_data: Dict) -> List[ConfluenceZone]:
    zones = []
    poc = vp_data.get("poc", 0)
    val = vp_data.get("val", 0)
    vah = vp_data.get("vah", 0)
    tolerance = 0.005
    for i in range(len(htf_df)):
        row = htf_df.iloc[i]
        ob_top = row.get("bullish_ob_top", np.nan)
        ob_bottom = row.get("bullish_ob_bottom", np.nan)
        if not pd.isna(ob_top) and not pd.isna(ob_bottom):
            mid = (ob_top + ob_bottom) / 2
            factors = ["ob"]
            if poc > 0 and abs(mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if val > 0 and abs(mid - val) / max(val, 1) <= tolerance:
                factors.append("val")
            if val > 0 and vah > 0 and ob_top >= val * 0.995 and ob_bottom <= vah * 1.005:
                factors.append("inside_value_area")
            zones.append(ConfluenceZone(row["timestamp"], "bullish", ob_top, ob_bottom, mid, "ob", factors, len(factors), row.get("market_structure", "ranging")))
        fvg_top = row.get("bullish_fvg_top", np.nan)
        fvg_bottom = row.get("bullish_fvg_bottom", np.nan)
        if not pd.isna(fvg_top) and not pd.isna(fvg_bottom):
            mid = (fvg_top + fvg_bottom) / 2
            factors = ["fvg"]
            if poc > 0 and abs(mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if val > 0 and abs(mid - val) / max(val, 1) <= tolerance:
                factors.append("val")
            if val > 0 and vah > 0 and fvg_top >= val * 0.995 and fvg_bottom <= vah * 1.005:
                factors.append("inside_value_area")
            zones.append(ConfluenceZone(row["timestamp"], "bullish", fvg_top, fvg_bottom, mid, "fvg", factors, len(factors), row.get("market_structure", "ranging")))
        bear_ob_top = row.get("bearish_ob_top", np.nan)
        bear_ob_bottom = row.get("bearish_ob_bottom", np.nan)
        if not pd.isna(bear_ob_top) and not pd.isna(bear_ob_bottom):
            mid = (bear_ob_top + bear_ob_bottom) / 2
            factors = ["ob"]
            if poc > 0 and abs(mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if vah > 0 and abs(mid - vah) / max(vah, 1) <= tolerance:
                factors.append("vah")
            if val > 0 and vah > 0 and bear_ob_top >= val * 0.995 and bear_ob_bottom <= vah * 1.005:
                factors.append("inside_value_area")
            zones.append(ConfluenceZone(row["timestamp"], "bearish", bear_ob_top, bear_ob_bottom, mid, "ob", factors, len(factors), row.get("market_structure", "ranging")))
        bear_fvg_top = row.get("bearish_fvg_top", np.nan)
        bear_fvg_bottom = row.get("bearish_fvg_bottom", np.nan)
        if not pd.isna(bear_fvg_top) and not pd.isna(bear_fvg_bottom):
            mid = (bear_fvg_top + bear_fvg_bottom) / 2
            factors = ["fvg"]
            if poc > 0 and abs(mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if vah > 0 and abs(mid - vah) / max(vah, 1) <= tolerance:
                factors.append("vah")
            if val > 0 and vah > 0 and bear_fvg_top >= val * 0.995 and bear_fvg_bottom <= vah * 1.005:
                factors.append("inside_value_area")
            zones.append(ConfluenceZone(row["timestamp"], "bearish", bear_fvg_top, bear_fvg_bottom, mid, "fvg", factors, len(factors), row.get("market_structure", "ranging")))
    return zones


def find_sweeps_in_ltf(ltf_df: pd.DataFrame) -> List[Dict]:
    sweeps = []
    for i in range(len(ltf_df)):
        row = ltf_df.iloc[i]
        if row.get("sweep_bullish", False):
            sweeps.append({"timestamp": row["timestamp"], "sweep_type": "bullish", "sweep_price": row.get("sweep_low", row["low"]), "close_price": row["close"], "high": row["high"], "low": row["low"], "chooch": row.get("chooch_bullish", False), "bos": row.get("bos_bullish", False)})
        if row.get("sweep_bearish", False):
            sweeps.append({"timestamp": row["timestamp"], "sweep_type": "bearish", "sweep_price": row.get("sweep_high", row["high"]), "close_price": row["close"], "high": row["high"], "low": row["low"], "chooch": row.get("chooch_bearish", False), "bos": row.get("bos_bearish", False)})
    return sweeps


def match_sweep_to_zone(sweep: Dict, zone: ConfluenceZone, ltf_df: pd.DataFrame, config: Dict, vp_data: Optional[Dict] = None, htf_df: Optional[pd.DataFrame] = None) -> Optional[Signal]:
    trading_cfg = config.get("trading", {})
    sweep_ts = sweep["timestamp"]
    _find_nearest_swing_high_low(htf_df, sweep_ts)
    if zone.factor_count < config.get("filters", {}).get("min_confluence_factors", 2):
        return None
    if zone.zone_type == "bullish" and zone.market_structure == "downtrend":
        return None
    if zone.zone_type == "bearish" and zone.market_structure == "uptrend":
        return None
    if sweep["sweep_type"] == "bullish" and zone.zone_type == "bullish":
        if sweep["sweep_price"] <= zone.zone_high and sweep["sweep_price"] >= zone.zone_low * 0.995:
            if not sweep.get("chooch", False) and not sweep.get("bos", False):
                sweep_idx = ltf_df[ltf_df["timestamp"] == sweep["timestamp"]].index
                if len(sweep_idx) > 0 and sweep_idx[0] + 1 < len(ltf_df):
                    next_bar = ltf_df.iloc[sweep_idx[0] + 1]
                    if not next_bar.get("chooch_bullish", False) and not next_bar.get("bos_bullish", False):
                        if not (next_bar["close"] > next_bar["open"] and next_bar["close"] > sweep["close_price"]):
                            return None
                else:
                    return None
            entry_price = max(sweep["close_price"], zone.zone_mid)
            sweep_low = sweep["sweep_price"]
            atr_value = calculate_atr(ltf_df, trading_cfg.get("atr_period", 14))
            if atr_value > 0:
                atr_buffer = trading_cfg.get("atr_sl_multiplier", 1.5) * atr_value / max(sweep_low, 1)
                atr_buffer = max(atr_buffer, trading_cfg.get("atr_sl_min_bps", 30) / 10000)
                atr_buffer = min(atr_buffer, trading_cfg.get("atr_sl_max_bps", 200) / 10000)
                stop_loss = sweep_low * (1 - atr_buffer)
            else:
                stop_loss = sweep_low * 0.99
            risk = entry_price - stop_loss
            if risk <= 0 or risk / entry_price > trading_cfg.get("max_risk_per_trade", 0.03):
                return None
            leverage = trading_cfg.get("leverage", 150)
            tp_ratio = 0.40 / leverage
            tp1 = entry_price * (1 + tp_ratio)
            confidence = min(0.95, 0.5 + zone.factor_count * 0.1 + (0.1 if sweep.get("chooch", False) else 0))
            reasons = [f"sweep+{zone.source_type}"]
            if zone.factor_count > 1:
                reasons.append("vp_confluence")
            return Signal(sweep["timestamp"], "", "long", entry_price, stop_loss, tp1, tp1, trading_cfg.get("position_size_pct", 0.02), confidence, reasons + zone.factors, zone.zone_high if zone.source_type == "ob" else None, zone.zone_high if zone.source_type == "fvg" else None, zone.zone_mid, sweep_low, zone.market_structure)
    if sweep["sweep_type"] == "bearish" and zone.zone_type == "bearish":
        if sweep["sweep_price"] >= zone.zone_low and sweep["sweep_price"] <= zone.zone_high * 1.005:
            if not sweep.get("chooch", False) and not sweep.get("bos", False):
                sweep_idx = ltf_df[ltf_df["timestamp"] == sweep["timestamp"]].index
                if len(sweep_idx) > 0 and sweep_idx[0] + 1 < len(ltf_df):
                    next_bar = ltf_df.iloc[sweep_idx[0] + 1]
                    if not next_bar.get("chooch_bearish", False) and not next_bar.get("bos_bearish", False):
                        if not (next_bar["close"] < next_bar["open"] and next_bar["close"] < sweep["close_price"]):
                            return None
                else:
                    return None
            entry_price = min(sweep["close_price"], zone.zone_mid)
            sweep_high = sweep["sweep_price"]
            atr_value = calculate_atr(ltf_df, trading_cfg.get("atr_period", 14))
            if atr_value > 0:
                atr_buffer = trading_cfg.get("atr_sl_multiplier", 1.5) * atr_value / max(sweep_high, 1)
                atr_buffer = max(atr_buffer, trading_cfg.get("atr_sl_min_bps", 30) / 10000)
                atr_buffer = min(atr_buffer, trading_cfg.get("atr_sl_max_bps", 200) / 10000)
                stop_loss = sweep_high * (1 + atr_buffer)
            else:
                stop_loss = sweep_high * 1.005
            risk = stop_loss - entry_price
            if risk <= 0 or risk / entry_price > trading_cfg.get("max_risk_per_trade", 0.03):
                return None
            leverage = trading_cfg.get("leverage", 150)
            tp_ratio = 0.40 / leverage
            tp1 = entry_price * (1 - tp_ratio)
            confidence = min(0.95, 0.5 + zone.factor_count * 0.1 + (0.1 if sweep.get("chooch", False) else 0))
            reasons = [f"sweep+{zone.source_type}"]
            if zone.factor_count > 1:
                reasons.append("vp_confluence")
            return Signal(sweep["timestamp"], "", "short", entry_price, stop_loss, tp1, tp1, trading_cfg.get("position_size_pct", 0.02), confidence, reasons + zone.factors, zone.zone_low if zone.source_type == "ob" else None, zone.zone_low if zone.source_type == "fvg" else None, zone.zone_mid, sweep_high, zone.market_structure)
    return None


def generate_signals(htf_df: pd.DataFrame, ltf_df: pd.DataFrame, vp_data: Dict, config: Dict) -> List[Signal]:
    zones = collect_all_zones(htf_df, vp_data)
    if not zones:
        return []
    sweeps = find_sweeps_in_ltf(ltf_df)
    if not sweeps:
        return []
    signals = []
    for sweep in sweeps:
        for zone in zones:
            time_diff = (sweep["timestamp"] - zone.timestamp).total_seconds()
            if time_diff < 900 or time_diff > 172800:
                continue
            signal = match_sweep_to_zone(sweep, zone, ltf_df, config, vp_data=vp_data, htf_df=htf_df)
            if signal is not None:
                signal.symbol = htf_df.attrs.get("symbol", "UNKNOWN")
                signals.append(signal)
                break
    if signals:
        signals.sort(key=lambda s: s.timestamp)
        deduped = [signals[0]]
        for s in signals[1:]:
            last = deduped[-1]
            if (s.timestamp - last.timestamp).total_seconds() > 7200 or s.side != last.side:
                deduped.append(s)
            elif s.confidence > last.confidence:
                deduped[-1] = s
        signals = deduped
    return signals


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    if df is None or len(df) < period + 1:
        return 0.0
    highs = df["high"].values
    lows = df["low"].values
    closes = df["close"].values
    tr_values = np.zeros(len(df))
    for i in range(1, len(df)):
        tr_values[i] = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
    return float(np.mean(tr_values[1:period + 1]))


class SMCVPConfluenceStrategy(IStrategy):
    INTERFACE_VERSION = 3
    timeframe = "5m"
    can_short = True
    process_only_new_candles = True
    startup_candle_count = 300
    minimal_roi = {"0": 0.04}
    stoploss = -0.06
    use_exit_signal = True
    exit_profit_only = False
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.018
    trailing_only_offset_is_reached = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        df = dataframe.copy()
        df["timestamp"] = pd.to_datetime(df["date"] if "date" in df.columns else df.index)
        smc_cfg = {"bos_lookback": 20, "min_ob_size_bps": 5, "fvg_min_gap_bps": 3, "sweep_tolerance_bps": 2, "liquidity_lookback": 50}
        df = compute_full_smc(df, smc_cfg)
        return df

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

