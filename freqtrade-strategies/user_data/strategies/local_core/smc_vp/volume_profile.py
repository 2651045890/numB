"""
Volume Profile (成交量分布) 核心指标
- POC (Point of Control / 控制点)
- VA (Value Area / 价值区: VAL, VAH)
- HVN (High Volume Node / 高量节点)
- LVN (Low Volume Node / 低量节点)
"""
from typing import Dict, Tuple

import numpy as np
import pandas as pd


def compute_daily_volume_profile(df: pd.DataFrame, num_bins: int = 24, value_area_pct: float = 0.70, hvn_threshold: float = 1.5) -> Dict:
    """
    计算每日成交量分布 (Daily Volume Profile)

    参数:
        df: 包含 'high', 'low', 'volume' 的 DataFrame
        num_bins: 价格区间分桶数
        value_area_pct: 价值区占比 (默认 70%)
        hvn_threshold: 高量节点阈值 (平均值的倍数)

    返回:
        Dict 包含 POC, VAL, VAH, HVN, 等关键价格水平
    """
    if df.empty or len(df) < 5:
        return {}

    high = df["high"].max()
    low = df["low"].min()
    price_range = high - low

    if price_range == 0:
        return {}

    bin_size = price_range / num_bins

    # 初始化价格区间
    bins = [low + i * bin_size for i in range(num_bins + 1)]
    bin_centers = [(bins[i] + bins[i + 1]) / 2 for i in range(num_bins)]
    volume_profile = np.zeros(num_bins)

    # 将每根 K 线的成交量分配到对应的价格区间
    # 使用线性分配：按 K 线高低价所覆盖的区间比例分配
    for _, row in df.iterrows():
        o, h, l, c, v = row["open"], row["high"], row["low"], row["close"], row["volume"]
        if v == 0 or np.isnan(v):
            continue

        # 确定该 K 线覆盖的区间范围
        bar_low = min(l, o)
        bar_high = max(h, c)

        # 找到覆盖的区间索引
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

    # POC: 最高成交量的价格区间中心值
    poc_idx = np.argmax(volume_profile)
    poc = bin_centers[poc_idx]
    poc_volume = volume_profile[poc_idx]

    # 价值区 (Value Area)：从 POC 开始向外扩展直到累积达到 70%
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

    # HVN / LVN 节点
    avg_volume_per_bin = total_volume / num_bins
    hvn_levels = []
    lvn_levels = []

    for i in range(num_bins):
        level = bin_centers[i]
        if volume_profile[i] >= avg_volume_per_bin * hvn_threshold:
            hvn_levels.append(level)
        elif volume_profile[i] <= avg_volume_per_bin * 0.3:
            lvn_levels.append(level)

    return {
        "poc": poc,
        "poc_volume": poc_volume,
        "val": val,
        "vah": vah,
        "value_area_pct": value_area_pct,
        "hvn_levels": hvn_levels,
        "lvn_levels": lvn_levels,
        "volume_profile": volume_profile.tolist(),
        "bin_centers": bin_centers,
        "total_volume": total_volume,
        "high": high,
        "low": low,
    }


def compute_daily_vp_for_range(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    对整个 DataFrame 按日计算每日 Volume Profile
    返回 DataFrame 附加每日的 VP 数据
    
    df 需要包含 'timestamp' 列（datetime 类型）
    """
    df = df.copy()
    df["date"] = df["timestamp"].dt.date

    # 初始化 Volume Profile 列
    df["daily_poc"] = np.nan
    df["daily_val"] = np.nan
    df["daily_vah"] = np.nan

    for date, group in df.groupby("date"):
        vp = compute_daily_volume_profile(
            group,
            num_bins=config.get("num_bins", 24),
            value_area_pct=config.get("value_area_pct", 0.70),
            hvn_threshold=config.get("hvn_threshold", 1.5),
        )
        if vp:
            mask = df["date"] == date
            df.loc[mask, "daily_poc"] = vp["poc"]
            df.loc[mask, "daily_val"] = vp["val"]
            df.loc[mask, "daily_vah"] = vp["vah"]

    return df


def compute_session_vp(df: pd.DataFrame, session_start_hour: int = 0, session_end_hour: int = 24, config: Dict = None) -> Dict:
    """
    计算特定交易时段的 Volume Profile（亚洲/欧洲/美洲盘）
    """
    if config is None:
        config = {"num_bins": 24, "value_area_pct": 0.70, "hvn_threshold": 1.5}

    session_df = df[
        (df["timestamp"].dt.hour >= session_start_hour) &
        (df["timestamp"].dt.hour < session_end_hour)
        ]

    if session_df.empty:
        return {}

    return compute_daily_volume_profile(
        session_df,
        num_bins=config.get("num_bins", 24),
        value_area_pct=config.get("value_area_pct", 0.70),
        hvn_threshold=config.get("hvn_threshold", 1.5),
    )


def check_confluence_with_vp(price_level: float, vp: Dict, tolerance_pct: float = 0.001) -> Tuple[bool, str]:
    """
    检查价格水平是否与 VP 关键区域共振
    """
    if not vp:
        return False, "no_vp_data"

    poc = vp.get("poc", 0)
    val = vp.get("val", 0)
    vah = vp.get("vah", 0)

    # 检查是否接近 POC
    if abs(price_level - poc) / poc <= tolerance_pct:
        return True, "poc_confluence"

    # 检查是否接近 VAL（做多共振区）
    if abs(price_level - val) / val <= tolerance_pct:
        return True, "val_confluence"

    # 检查是否接近 VAH（做空共振区）
    if abs(price_level - vah) / vah <= tolerance_pct:
        return True, "vah_confluence"

    # 检查是否在 HVN 区域内
    for hvn in vp.get("hvn_levels", []):
        if abs(price_level - hvn) / hvn <= tolerance_pct:
            return True, "hvn_confluence"

    # 检查是否在 VAL 与 VAH 之间（价值区内）
    if val <= price_level <= vah:
        return True, "inside_value_area"

    return False, "no_confluence"
