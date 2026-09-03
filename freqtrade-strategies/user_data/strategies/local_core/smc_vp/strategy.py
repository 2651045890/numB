"""
SMC + VP 共振交易策略（实战优化版）

核心逻辑更简化、更实战：
1. 在 HTF (15m) 上扫描所有历史 OB/FVG 订单块
2. 检查这些订单块是否与 VP 的 POC/VAH/VAL 共振
3. 记录每个共振区的价格范围和形成时间
4. 在 LTF (5m) 上扫描流动性掠夺事件
5. 若掠夺发生在共振区内，且出现微观反转信号，则进场
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import pandas as pd


@dataclass
class Signal:
    """交易信号"""
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
    """共振区"""
    timestamp: datetime
    zone_type: str          # "bullish" or "bearish"
    zone_high: float
    zone_low: float
    zone_mid: float
    source_type: str        # "ob" or "fvg"
    factors: List[str]
    factor_count: int
    market_structure: str


def collect_all_zones(htf_df: pd.DataFrame, vp_data: Dict) -> List[ConfluenceZone]:
    """
    扫描整个 HTF 数据集，收集所有 SMC + VP 共振区

    逻辑：
    1. 对每根 HTF K 线，检查是否有 OB/FVG 标记
    2. 检查该区域是否与 VP 的 POC/VAL/VAH 重叠
    3. 记录共振区的价格范围和形成时间

    参数:
        htf_df: 已计算 SMC 指标的 HTF DataFrame
        vp_data: 每日 VP 数据
        config: 策略配置
    """
    zones = []
    poc = vp_data.get("poc", 0)
    val = vp_data.get("val", 0)
    vah = vp_data.get("vah", 0)
    tolerance = 0.005  # 0.5% 容忍度（放宽）

    for i in range(len(htf_df)):
        row = htf_df.iloc[i]

        # --- 做多共振区 ---
        # 1. 看涨 OB
        ob_top = row.get("bullish_ob_top", np.nan)
        ob_bottom = row.get("bullish_ob_bottom", np.nan)
        if not pd.isna(ob_top) and not pd.isna(ob_bottom):
            ob_mid = (ob_top + ob_bottom) / 2
            factors = ["ob"]

            # 检查是否与 VP 共振
            if poc > 0 and abs(ob_mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if val > 0 and abs(ob_mid - val) / max(val, 1) <= tolerance:
                factors.append("val")
            if val > 0 and vah > 0 and ob_top >= val * 0.995 and ob_bottom <= vah * 1.005:
                factors.append("inside_value_area")

            zones.append(ConfluenceZone(
                timestamp=row["timestamp"],
                zone_type="bullish",
                zone_high=ob_top,
                zone_low=ob_bottom,
                zone_mid=ob_mid,
                source_type="ob",
                factors=factors,
                factor_count=len(factors),
                market_structure=row.get("market_structure", "ranging"),
            ))

        # 2. 看涨 FVG
        fvg_top = row.get("bullish_fvg_top", np.nan)
        fvg_bottom = row.get("bullish_fvg_bottom", np.nan)
        if not pd.isna(fvg_top) and not pd.isna(fvg_bottom):
            fvg_mid = (fvg_top + fvg_bottom) / 2
            factors = ["fvg"]

            if poc > 0 and abs(fvg_mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if val > 0 and abs(fvg_mid - val) / max(val, 1) <= tolerance:
                factors.append("val")
            if val > 0 and vah > 0 and fvg_top >= val * 0.995 and fvg_bottom <= vah * 1.005:
                factors.append("inside_value_area")

            zones.append(ConfluenceZone(
                timestamp=row["timestamp"],
                zone_type="bullish",
                zone_high=fvg_top,
                zone_low=fvg_bottom,
                zone_mid=fvg_mid,
                source_type="fvg",
                factors=factors,
                factor_count=len(factors),
                market_structure=row.get("market_structure", "ranging"),
            ))

        # --- 做空共振区 ---
        # 3. 看跌 OB
        bear_ob_top = row.get("bearish_ob_top", np.nan)
        bear_ob_bottom = row.get("bearish_ob_bottom", np.nan)
        if not pd.isna(bear_ob_top) and not pd.isna(bear_ob_bottom):
            ob_mid = (bear_ob_top + bear_ob_bottom) / 2
            factors = ["ob"]

            if poc > 0 and abs(ob_mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if vah > 0 and abs(ob_mid - vah) / max(vah, 1) <= tolerance:
                factors.append("vah")
            if val > 0 and vah > 0 and bear_ob_top >= val * 0.995 and bear_ob_bottom <= vah * 1.005:
                factors.append("inside_value_area")

            zones.append(ConfluenceZone(
                timestamp=row["timestamp"],
                zone_type="bearish",
                zone_high=bear_ob_top,
                zone_low=bear_ob_bottom,
                zone_mid=ob_mid,
                source_type="ob",
                factors=factors,
                factor_count=len(factors),
                market_structure=row.get("market_structure", "ranging"),
            ))

        # 4. 看跌 FVG
        bear_fvg_top = row.get("bearish_fvg_top", np.nan)
        bear_fvg_bottom = row.get("bearish_fvg_bottom", np.nan)
        if not pd.isna(bear_fvg_top) and not pd.isna(bear_fvg_bottom):
            fvg_mid = (bear_fvg_top + bear_fvg_bottom) / 2
            factors = ["fvg"]

            if poc > 0 and abs(fvg_mid - poc) / max(poc, 1) <= tolerance:
                factors.append("poc")
            if vah > 0 and abs(fvg_mid - vah) / max(vah, 1) <= tolerance:
                factors.append("vah")
            if val > 0 and vah > 0 and bear_fvg_top >= val * 0.995 and bear_fvg_bottom <= vah * 1.005:
                factors.append("inside_value_area")

            zones.append(ConfluenceZone(
                timestamp=row["timestamp"],
                zone_type="bearish",
                zone_high=bear_fvg_top,
                zone_low=bear_fvg_bottom,
                zone_mid=fvg_mid,
                source_type="fvg",
                factors=factors,
                factor_count=len(factors),
                market_structure=row.get("market_structure", "ranging"),
            ))

    # 去重：合并相同时间附近的共振区
    zones = _deduplicate_zones(zones)
    return zones


def _deduplicate_zones(zones: List[ConfluenceZone]) -> List[ConfluenceZone]:
    """合并时间和价格相近的共振区"""
    if not zones:
        return []

    # 按时间排序
    zones_sorted = sorted(zones, key=lambda z: z.timestamp)
    merged = [zones_sorted[0]]

    for z in zones_sorted[1:]:
        last = merged[-1]
        time_diff = (z.timestamp - last.timestamp).total_seconds()
        price_diff = abs(z.zone_mid - last.zone_mid) / max(last.zone_mid, 1)

        # 如果时间差 < 30 分钟且价格差 < 0.3%，合并
        if time_diff < 1800 and price_diff < 0.003:
            # 合并：取更宽的价格范围
            merged[-1] = ConfluenceZone(
                timestamp=last.timestamp,
                zone_type=z.zone_type,
                zone_high=max(last.zone_high, z.zone_high),
                zone_low=min(last.zone_low, z.zone_low),
                zone_mid=(max(last.zone_high, z.zone_high) + min(last.zone_low, z.zone_low)) / 2,
                source_type="merged",
                factors=list(set(last.factors + z.factors)),
                factor_count=len(set(last.factors + z.factors)),
                market_structure=z.market_structure,
            )
        else:
            merged.append(z)

    return merged


def calculate_atr(df: pd.DataFrame, period: int = 14) -> float:
    """
    计算当前 ATR（平均真实波幅）

    ATR 衡量市场波动率，用于自适应止损：
    - 波动大时 → SL 自动放宽，避免被插针打掉
    - 波动小时 → SL 自动收紧，控制风险

    参数:
        df: OHLCV DataFrame，必须包含 high/low/close 列
        period: ATR 计算周期（默认14根K线）

    返回:
        float: 当前 ATR 值（以价格为单位），数据不足时返回 0.0
    """
    if df is None or len(df) < period + 1:
        return 0.0

    highs = df['high'].values
    lows = df['low'].values
    closes = df['close'].values

    tr_values = np.zeros(len(df))
    for i in range(1, len(df)):
        tr_values[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1])
        )

    # 使用简单移动平均计算 ATR
    atr = np.mean(tr_values[1:period + 1])
    return float(atr)


def _find_nearest_swing_high_low(htf_df: pd.DataFrame, timestamp: datetime) -> tuple:
    """
    查找给定时间戳之前最近的结构高点（swing_high）和结构低点（swing_low）。

    用于精确计算 TP1（BSL/SSL）和 TP2（前高/前低），
    替代原来使用全局 HTF 最高/最低价的不精确做法。

    参数:
        htf_df: HTF 级别 DataFrame，必须包含 swing_high/swing_low 布尔列
        timestamp: 掠夺事件的时间戳

    返回:
        (recent_swing_high, recent_swing_low) 元组，无可用的结构点时返回 (None, None)
    """
    if htf_df is None or htf_df.empty:
        return None, None

    # 筛选出 timestamp 之前的数据
    before = htf_df[htf_df["timestamp"] <= timestamp].copy()
    if before.empty:
        return None, None

    # 查找最近的结构高点（swing_high = True 的行的最高价）
    recent_high = None
    if "swing_high" in before.columns:
        swing_highs = before[before["swing_high"] == True]
        if not swing_highs.empty:
            recent_high = float(swing_highs.iloc[-1]["high"])

    # 查找最近的结构低点（swing_low = True 的行的最低价）
    recent_low = None
    if "swing_low" in before.columns:
        swing_lows = before[before["swing_low"] == True]
        if not swing_lows.empty:
            recent_low = float(swing_lows.iloc[-1]["low"])

    return recent_high, recent_low


def find_sweeps_in_ltf(ltf_df: pd.DataFrame) -> List[Dict]:
    """
    在 LTF 上扫描流动性掠夺事件

    返回掠夺事件列表，每个事件包含：
    - timestamp: 发生时间
    - sweep_type: "bullish" (多头掠夺 = 跌破收回) 或 "bearish" (空头掠夺 = 突破收回)
    - sweep_price: 掠夺极值（最低/最高）
    - close_price: 收盘价
    - chooch: 是否有 CHOCH 信号
    """
    sweeps = []
    for i in range(len(ltf_df)):
        row = ltf_df.iloc[i]

        if row.get("sweep_bullish", False):
            sweeps.append({
                "timestamp": row["timestamp"],
                "sweep_type": "bullish",
                "sweep_price": row.get("sweep_low", row["low"]),
                "close_price": row["close"],
                "high": row["high"],
                "low": row["low"],
                "chooch": row.get("chooch_bullish", False),
                "bos": row.get("bos_bullish", False),
            })

        if row.get("sweep_bearish", False):
            sweeps.append({
                "timestamp": row["timestamp"],
                "sweep_type": "bearish",
                "sweep_price": row.get("sweep_high", row["high"]),
                "close_price": row["close"],
                "high": row["high"],
                "low": row["low"],
                "chooch": row.get("chooch_bearish", False),
                "bos": row.get("bos_bearish", False),
            })

    return sweeps


def match_sweep_to_zone(sweep: Dict, zone: ConfluenceZone, ltf_df: pd.DataFrame,
                         config: Dict,
                         vp_data: Optional[Dict] = None,
                         htf_df: Optional[pd.DataFrame] = None) -> Optional[Signal]:
    """
    将掠夺事件与共振区匹配，生成交易信号

    做多条件：
    - 掠夺类型 = bullish (跌破收回)
    - 掠夺低点落在共振区内或附近
    - 有 CHOCH 或 BOS 确认
    - 趋势方向吻合（uptrend 或 ranging）

    做空条件：
    - 掠夺类型 = bearish (突破收回)
    - 掠夺高点落在共振区内或附近
    - 有 CHOCH 或 BOS 确认
    - 趋势方向吻合（downtrend 或 ranging）

    止盈止损计算（按策略要求）：
    - 做多 SL: 流动性掠夺产生的最低点下方
    - 做多 TP1: 当日VAH（价值区上限）或上方的流动性池 (BSL)
    - 做多 TP2: 前高
    - 做空 SL: 流动性掠夺产生的最高点上方
    - 做空 TP1: 当日VAL（价值区下限）或下方的流动性池 (SSL)
    - 做空 TP2: 前低
    """
    trading_cfg = config.get("trading", {})

    # 查找最近的结构高点/低点（用于精确计算 TP1 的 BSL/SSL 和 TP2 的前高/前低）
    # 替代原来使用全局 HTF 最高/最低价的不精确做法
    sweep_ts = sweep["timestamp"]
    swing_high, swing_low = _find_nearest_swing_high_low(htf_df, sweep_ts)

    # 检查最小共振因子数（避免低质量信号）
    filters_cfg = config.get("filters", {})
    min_confluence = filters_cfg.get("min_confluence_factors", 2)
    if zone.factor_count < min_confluence:
        return None

    # 检查趋势一致性
    if zone.zone_type == "bullish" and zone.market_structure == "downtrend":
        return None
    if zone.zone_type == "bearish" and zone.market_structure == "uptrend":
        return None

    # 检查掠夺是否发生在共振区内
    if sweep["sweep_type"] == "bullish" and zone.zone_type == "bullish":
        # 多头掠夺：低点需在共振区内或略低于
        if sweep["sweep_price"] <= zone.zone_high and sweep["sweep_price"] >= zone.zone_low * 0.995:
            # 确认有 CHOCH 或 BOS
            if not sweep.get("chooch", False) and not sweep.get("bos", False):
                # 如果没有 CHOCH 也没有 BOS，检查下一根 K 线
                sweep_idx = ltf_df[ltf_df["timestamp"] == sweep["timestamp"]].index
                if len(sweep_idx) > 0:
                    idx = sweep_idx[0]
                    if idx + 1 < len(ltf_df):
                        next_bar = ltf_df.iloc[idx + 1]
                        if not next_bar.get("chooch_bullish", False) and not next_bar.get("bos_bullish", False):
                            if not (next_bar["close"] > next_bar["open"] and next_bar["close"] > sweep["close_price"]):
                                return None
                else:
                    return None

            # ================================================================
            # 计算进场点
            # ================================================================
            entry_price = max(sweep["close_price"], zone.zone_mid)

            # ================================================================
            # 止损: ATR自适应 — 设在流动性掠夺最低点下方
            # 根据市场波动率自动调整缓冲距离，避免被插针打掉
            # ================================================================
            sweep_low = sweep["sweep_price"]  # 掠夺最低点
            atr_value = calculate_atr(ltf_df, trading_cfg.get("atr_period", 14))
            if atr_value > 0:
                atr_buffer = trading_cfg.get("atr_sl_multiplier", 1.5) * atr_value / max(sweep_low, 1)
                atr_buffer = max(atr_buffer, trading_cfg.get("atr_sl_min_bps", 30) / 10000)
                atr_buffer = min(atr_buffer, trading_cfg.get("atr_sl_max_bps", 200) / 10000)
                stop_loss = sweep_low * (1 - atr_buffer)
            else:
                stop_loss = sweep_low * 0.99  # ATR不可用时回退到固定值

            # 最大风险检查
            risk = entry_price - stop_loss
            max_risk = trading_cfg.get("max_risk_per_trade", 0.03)
            if risk <= 0 or risk / entry_price > max_risk:
                return None

            # ================================================================
            # 单一止盈：固定收益率 40%（基于杠杆倍数，如 150x → 40%/150=0.267% 价格涨幅）
            # ================================================================
            leverage = trading_cfg.get("leverage", 150)
            tp_ratio = 0.40 / leverage
            tp1 = entry_price * (1 + tp_ratio)   # 收益率 40% / 杠杆
            tp2 = entry_price * (1 + tp_ratio)   # 只用一个止盈，TP2 设置相同

            # 置信度
            confidence = 0.5 + zone.factor_count * 0.1
            if sweep.get("chooch", False):
                confidence += 0.1
            confidence = min(confidence, 0.95)

            reasons = [f"sweep+{zone.source_type}"]
            if zone.factor_count > 1:
                reasons.append("vp_confluence")

            return Signal(
                timestamp=sweep["timestamp"],
                symbol="",
                side="long",
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                position_size_pct=trading_cfg.get("position_size_pct", 0.02),
                confidence=confidence,
                reasons=reasons + zone.factors,
                ob_level=zone.zone_high if zone.source_type == "ob" else None,
                fvg_level=zone.zone_high if zone.source_type == "fvg" else None,
                sweep_level=sweep_low,
                market_structure=zone.market_structure,
            )

    elif sweep["sweep_type"] == "bearish" and zone.zone_type == "bearish":
        # 空头掠夺：高点需在共振区内或略高于
        if sweep["sweep_price"] >= zone.zone_low and sweep["sweep_price"] <= zone.zone_high * 1.005:
            if not sweep.get("chooch", False) and not sweep.get("bos", False):
                sweep_idx = ltf_df[ltf_df["timestamp"] == sweep["timestamp"]].index
                if len(sweep_idx) > 0:
                    idx = sweep_idx[0]
                    if idx + 1 < len(ltf_df):
                        next_bar = ltf_df.iloc[idx + 1]
                        if not next_bar.get("chooch_bearish", False) and not next_bar.get("bos_bearish", False):
                            if not (next_bar["close"] < next_bar["open"] and next_bar["close"] < sweep["close_price"]):
                                return None
                else:
                    return None

            # ================================================================
            # 计算进场点
            # ================================================================
            entry_price = min(sweep["close_price"], zone.zone_mid)

            # ================================================================
            # 止损: ATR自适应 — 设在流动性掠夺最高点上方
            # 根据市场波动率自动调整缓冲距离，避免被插针打掉
            # ================================================================
            sweep_high = sweep["sweep_price"]  # 掠夺最高点
            atr_value = calculate_atr(ltf_df, trading_cfg.get("atr_period", 14))
            if atr_value > 0:
                atr_buffer = trading_cfg.get("atr_sl_multiplier", 1.5) * atr_value / max(sweep_high, 1)
                atr_buffer = max(atr_buffer, trading_cfg.get("atr_sl_min_bps", 30) / 10000)
                atr_buffer = min(atr_buffer, trading_cfg.get("atr_sl_max_bps", 200) / 10000)
                stop_loss = sweep_high * (1 + atr_buffer)
            else:
                stop_loss = sweep_high * 1.005  # ATR不可用时回退到固定值

            # 最大风险检查
            risk = stop_loss - entry_price
            max_risk = trading_cfg.get("max_risk_per_trade", 0.03)
            if risk <= 0 or risk / entry_price > max_risk:
                return None

            # ================================================================
            # 单一止盈：固定收益率 40%（做空，基于杠杆倍数）
            # ================================================================
            leverage = trading_cfg.get("leverage", 150)
            tp_ratio = 0.40 / leverage
            tp1 = entry_price * (1 - tp_ratio)   # 收益率 40% / 杠杆
            tp2 = entry_price * (1 - tp_ratio)   # 只用一个止盈，TP2 设置相同

            confidence = 0.5 + zone.factor_count * 0.1
            if sweep.get("chooch", False):
                confidence += 0.1
            confidence = min(confidence, 0.95)

            reasons = [f"sweep+{zone.source_type}"]
            if zone.factor_count > 1:
                reasons.append("vp_confluence")

            return Signal(
                timestamp=sweep["timestamp"],
                symbol="",
                side="short",
                entry_price=entry_price,
                stop_loss=stop_loss,
                take_profit_1=tp1,
                take_profit_2=tp2,
                position_size_pct=trading_cfg.get("position_size_pct", 0.02),
                confidence=confidence,
                reasons=reasons + zone.factors,
                ob_level=zone.zone_low if zone.source_type == "ob" else None,
                fvg_level=zone.zone_low if zone.source_type == "fvg" else None,
                sweep_level=sweep_high,
                market_structure=zone.market_structure,
            )

    return None


def generate_signals(htf_df: pd.DataFrame, ltf_df: pd.DataFrame,
                     vp_data: Dict, config: Dict) -> List[Signal]:
    """
    生成完整交易信号

    流程：
    1. 收集所有 SMC + VP 共振区
    2. 扫描 LTF 上所有流动性掠夺事件
    3. 匹配掠夺与共振区
    4. 生成交易信号
    """
    cfg = {
        "smc": config.get("smc", {}),
        "vp": config.get("vp", {}),
        "trading": config.get("trading", {}),
        "filters": config.get("filters", {}),
    }

    # 1. 收集所有共振区
    zones = collect_all_zones(htf_df, vp_data)
    if not zones:
        return []

    # 2. 扫描 LTF 掠夺事件
    sweeps = find_sweeps_in_ltf(ltf_df)
    if not sweeps:
        return []

    # 3. 匹配掠夺与共振区
    # 从 HTF 数据中提取前高/前低（用于止盈计算）
    # 对于每个掠夺事件，单独查找该时间之前最近的结构高点/低点
    signals = []
    for sweep in sweeps:
        # 掠夺发生后，找之前形成的共振区（时间差 15分钟-48小时内）
        for zone in zones:
            time_diff = (sweep["timestamp"] - zone.timestamp).total_seconds()
            if time_diff < 900:  # 最少 15 分钟（原1小时过于严格，经常错过日内机会）
                continue
            if time_diff > 172800:  # 最多 48 小时
                continue

            signal = match_sweep_to_zone(sweep, zone, ltf_df, cfg,
                                         vp_data=vp_data,
                                         htf_df=htf_df)
            if signal is not None:
                signal.symbol = htf_df.attrs.get("symbol", "UNKNOWN")
                signals.append(signal)
                break  # 一个掠夺只匹配一个 zone

    # 4. 去重：同一时间方向只保留一个信号
    if signals:
        signals.sort(key=lambda s: s.timestamp)
        deduped = [signals[0]]
        for s in signals[1:]:
            last = deduped[-1]
            time_diff = (s.timestamp - last.timestamp).total_seconds()
            if time_diff > 7200 or s.side != last.side:  # 2 小时内同方向只保留一个，降低信号频次
                deduped.append(s)
            elif s.confidence > last.confidence:
                deduped[-1] = s

        signals = deduped

    return signals