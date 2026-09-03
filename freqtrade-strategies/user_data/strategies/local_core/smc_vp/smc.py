"""
SMC (Smart Money Concepts) 核心指标
- Order Blocks (订单块)
- FVG (Fair Value Gap / 公允价值缺口)
- BOS (Break of Structure / 结构突破)
- CHOCH (Change of Character / 特性改变)
- 流动性池 (Liquidity Pools)
"""
import numpy as np
import pandas as pd
from typing import List, Optional, Dict


def detect_swing_high_low(df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
    """
    检测波段高点与低点
    """
    df = df.copy()
    df["swing_high"] = False
    df["swing_low"] = False

    for i in range(lookback, len(df) - lookback):
        # 波段高点：左右各 lookback 根中的最高点
        if df["high"].iloc[i] == max(df["high"].iloc[i - lookback:i + lookback + 1]):
            if df["high"].iloc[i] > df["high"].iloc[i - lookback] and \
               df["high"].iloc[i] > df["high"].iloc[i + lookback]:
                df.loc[df.index[i], "swing_high"] = True

        # 波段低点：左右各 lookback 根中的最低点
        if df["low"].iloc[i] == min(df["low"].iloc[i - lookback:i + lookback + 1]):
            if df["low"].iloc[i] < df["low"].iloc[i - lookback] and \
               df["low"].iloc[i] < df["low"].iloc[i + lookback]:
                df.loc[df.index[i], "swing_low"] = True

    return df


def detect_bos(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
    """
    检测 Break of Structure (结构突破)
    BOS 定义：
      - 多头 BOS：价格突破前一个波段高点（上升结构延续）
      - 空头 BOS：价格跌破前一个波段低点（下降结构延续）
    """
    df = df.copy()
    df["bos_bullish"] = False
    df["bos_bearish"] = False

    swing_highs = df[df["swing_high"]].index
    swing_lows = df[df["swing_low"]].index

    for i in range(1, len(df)):
        # 找最近的前一个波段高点
        recent_highs = swing_highs[swing_highs < i]
        if len(recent_highs) > 0:
            last_high_idx = recent_highs[-1]
            if df["high"].iloc[i] > df["high"].iloc[last_high_idx]:
                if i - last_high_idx <= lookback:
                    df.loc[df.index[i], "bos_bullish"] = True

        # 找最近的前一个波段低点
        recent_lows = swing_lows[swing_lows < i]
        if len(recent_lows) > 0:
            last_low_idx = recent_lows[-1]
            if df["low"].iloc[i] < df["low"].iloc[last_low_idx]:
                if i - last_low_idx <= lookback:
                    df.loc[df.index[i], "bos_bearish"] = True

    return df


def detect_market_structure(df: pd.DataFrame) -> pd.DataFrame:
    """
    判断市场结构：上升趋势 (Uptrend) / 下降趋势 (Downtrend) / 盘整 (Ranging)
    基于 HH/HL (Higher High/Higher Low) 与 LH/LL (Lower High/Lower Low) 序列
    """
    df = df.copy()
    df["market_structure"] = "ranging"

    swing_highs_idx = df[df["swing_high"]].index.tolist()
    swing_lows_idx = df[df["swing_low"]].index.tolist()

    for i in range(1, len(df)):
        recent_highs = [h for h in swing_highs_idx if h < i]
        recent_lows = [l for l in swing_lows_idx if l < i]

        if len(recent_highs) >= 2 and len(recent_lows) >= 2:
            last_2_highs = recent_highs[-2:]
            last_2_lows = recent_lows[-2:]

            hh = df["high"].iloc[last_2_highs[-1]] > df["high"].iloc[last_2_highs[-2]]
            hl = df["low"].iloc[last_2_lows[-1]] > df["low"].iloc[last_2_lows[-2]]
            lh = df["high"].iloc[last_2_highs[-1]] < df["high"].iloc[last_2_highs[-2]]
            ll = df["low"].iloc[last_2_lows[-1]] < df["low"].iloc[last_2_lows[-2]]

            if hh and hl:
                df.loc[df.index[i], "market_structure"] = "uptrend"
            elif lh and ll:
                df.loc[df.index[i], "market_structure"] = "downtrend"
            else:
                df.loc[df.index[i], "market_structure"] = "ranging"

    return df


def detect_chooch(df: pd.DataFrame) -> pd.DataFrame:
    """
    检测 Change of Character (CHOCH / 特性改变)
    - 多头 CHOCH：下降结构中，价格突破前一个波段高点 (BOS to the upside after downtrend)
    - 空头 CHOCH：上升结构中，价格跌破前一个波段低点 (BOS to the downside after uptrend)
    """
    df = df.copy()
    df["chooch_bullish"] = False
    df["chooch_bearish"] = False

    for i in range(1, len(df)):
        # 检查前一段是否为下降趋势
        lookback_window = 30
        start = max(0, i - lookback_window)
        prev_structure = df["market_structure"].iloc[start:i].value_counts()

        # 空头 CHOCH：前一段是下降趋势，现在出现多头 BOS
        if df["bos_bullish"].iloc[i]:
            downtrend_count = prev_structure.get("downtrend", 0)
            uptrend_count = prev_structure.get("uptrend", 0)
            if downtrend_count > uptrend_count and downtrend_count >= 5:
                df.loc[df.index[i], "chooch_bullish"] = True

        # 多头 CHOCH：前一段是上升趋势，现在出现空头 BOS
        if df["bos_bearish"].iloc[i]:
            uptrend_count = prev_structure.get("uptrend", 0)
            downtrend_count = prev_structure.get("downtrend", 0)
            if uptrend_count > downtrend_count and uptrend_count >= 5:
                df.loc[df.index[i], "chooch_bearish"] = True

    return df


def detect_order_blocks(df: pd.DataFrame, min_body_bps: float = 5.0) -> pd.DataFrame:
    """
    检测订单块 (Order Blocks)
    - 看涨 OB (Bullish OB)：在上升趋势中，最后一根下跌 K 线（实体）的范围
    - 看跌 OB (Bearish OB)：在下降趋势中，最后一根上涨 K 线（实体）的范围
    - 确认条件：OB 形成后，价格需出现 strong move（突破式移动）
    """
    df = df.copy()
    df["bullish_ob_top"] = np.nan
    df["bullish_ob_bottom"] = np.nan
    df["bearish_ob_top"] = np.nan
    df["bearish_ob_bottom"] = np.nan

    for i in range(2, len(df) - 1):
        # 看涨订单块：下跌阳线 → 后续强势上涨
        prev_body = df["close"].iloc[i - 1] - df["open"].iloc[i - 1]
        curr_body = df["close"].iloc[i] - df["open"].iloc[i]

        # 前一根是下跌（或阴线实体为负/小于零），且当根强势上涨
        is_bearish_prev = df["close"].iloc[i - 1] < df["open"].iloc[i - 1]
        is_bullish_jump = curr_body > 0 and abs(curr_body) > abs(prev_body) * 1.5

        if is_bearish_prev and is_bullish_jump:
            body_size_bps = (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) / df["close"].iloc[i - 1] * 10000
            if body_size_bps >= min_body_bps:
                df.loc[df.index[i], "bullish_ob_top"] = max(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
                df.loc[df.index[i], "bullish_ob_bottom"] = min(df["open"].iloc[i - 1], df["close"].iloc[i - 1])

        # 看跌订单块：上涨阳线 → 后续强势下跌
        is_bullish_prev = df["close"].iloc[i - 1] > df["open"].iloc[i - 1]
        is_bearish_drop = curr_body < 0 and abs(curr_body) > abs(prev_body) * 1.5

        if is_bullish_prev and is_bearish_drop:
            body_size_bps = (df["high"].iloc[i - 1] - df["low"].iloc[i - 1]) / df["close"].iloc[i - 1] * 10000
            if body_size_bps >= min_body_bps:
                df.loc[df.index[i], "bearish_ob_top"] = max(df["open"].iloc[i - 1], df["close"].iloc[i - 1])
                df.loc[df.index[i], "bearish_ob_bottom"] = min(df["open"].iloc[i - 1], df["close"].iloc[i - 1])

    return df


def detect_fvg(df: pd.DataFrame, min_gap_bps: float = 3.0) -> pd.DataFrame:
    """
    检测公允价值缺口 (Fair Value Gap / FVG)
    三根 K 线模式：第一根的高 < 第三根的低（看涨 FVG）
    或第一根的低 > 第三根的高（看跌 FVG）
    FVG 区域 = 未重叠的价格区间
    """
    df = df.copy()
    df["bullish_fvg_top"] = np.nan
    df["bullish_fvg_bottom"] = np.nan
    df["bearish_fvg_top"] = np.nan
    df["bearish_fvg_bottom"] = np.nan

    for i in range(2, len(df)):
        # 看涨 FVG：第一根高 < 第三根低 → 中间有未被填补的缺口
        if df["high"].iloc[i - 2] < df["low"].iloc[i]:
            gap_bps = (df["low"].iloc[i] - df["high"].iloc[i - 2]) / df["close"].iloc[i] * 10000
            if gap_bps >= min_gap_bps:
                df.loc[df.index[i], "bullish_fvg_top"] = df["low"].iloc[i]
                df.loc[df.index[i], "bullish_fvg_bottom"] = df["high"].iloc[i - 2]

        # 看跌 FVG：第一根低 > 第三根高
        if df["low"].iloc[i - 2] > df["high"].iloc[i]:
            gap_bps = (df["low"].iloc[i - 2] - df["high"].iloc[i]) / df["close"].iloc[i] * 10000
            if gap_bps >= min_gap_bps:
                df.loc[df.index[i], "bearish_fvg_top"] = df["low"].iloc[i - 2]
                df.loc[df.index[i], "bearish_fvg_bottom"] = df["high"].iloc[i]

    return df


def detect_liquidity_levels(df: pd.DataFrame, lookback: int = 50) -> pd.DataFrame:
    """
    检测流动性池 (Liquidity Pools)
    - BSL (Buy-side Liquidity)：上方流动性（前高、双顶）
    - SSL (Sell-side Liquidity)：下方流动性（前低、双底）
    """
    df = df.copy()
    df["bsl_level"] = np.nan
    df["ssl_level"] = np.nan

    for i in range(lookback, len(df)):
        window = df.iloc[i - lookback:i]
        # BSL：最近 N 根的最高点
        bsl = window["high"].max()
        # SSL：最近 N 根的最低点
        ssl = window["low"].min()

        # 确认该流动性池未被突破
        if bsl > df["high"].iloc[i]:
            df.loc[df.index[i], "bsl_level"] = bsl
        if ssl < df["low"].iloc[i]:
            df.loc[df.index[i], "ssl_level"] = ssl

    return df


def detect_liquidity_sweep(df: pd.DataFrame, tolerance_bps: float = 2.0) -> pd.DataFrame:
    """
    检测流动性掠夺 (Liquidity Sweep)
    - 多头掠夺 (Sell-side Sweep)：价格跌破前低(SSL)后迅速收回
    - 空头掠夺 (Buy-side Sweep)：价格突破前高(BSL)后迅速收回
    - 用下影线/上影线来判断「收回」
    """
    df = df.copy()
    df["sweep_bullish"] = False
    df["sweep_bearish"] = False
    df["sweep_low"] = np.nan
    df["sweep_high"] = np.nan

    for i in range(1, len(df) - 1):
        # 多头掠夺：跌破 SSL 后收回
        if not pd.isna(df["ssl_level"].iloc[i - 1]):
            ssl = df["ssl_level"].iloc[i - 1]
            if df["low"].iloc[i] < ssl and df["close"].iloc[i] > ssl:
                bps_below = (ssl - df["low"].iloc[i]) / ssl * 10000
                if bps_below <= tolerance_bps * 3:
                    df.loc[df.index[i], "sweep_bullish"] = True
                    df.loc[df.index[i], "sweep_low"] = df["low"].iloc[i]

        # 空头掠夺：突破 BSL 后收回
        if not pd.isna(df["bsl_level"].iloc[i - 1]):
            bsl = df["bsl_level"].iloc[i - 1]
            if df["high"].iloc[i] > bsl and df["close"].iloc[i] < bsl:
                bps_above = (df["high"].iloc[i] - bsl) / bsl * 10000
                if bps_above <= tolerance_bps * 3:
                    df.loc[df.index[i], "sweep_bearish"] = True
                    df.loc[df.index[i], "sweep_high"] = df["high"].iloc[i]

    return df


def compute_full_smc(df: pd.DataFrame, config: Dict) -> pd.DataFrame:
    """
    完整 SMC 指标计算流水线
    """
    df = df.copy()
    lookback = config.get("bos_lookback", 20)

    # 1. 波段高低点
    df = detect_swing_high_low(df, lookback=5)

    # 2. 市场结构
    df = detect_market_structure(df)

    # 3. BOS
    df = detect_bos(df, lookback=lookback)

    # 4. CHOCH
    df = detect_chooch(df)

    # 5. 订单块
    df = detect_order_blocks(df, min_body_bps=config.get("min_ob_size_bps", 5))

    # 6. FVG
    df = detect_fvg(df, min_gap_bps=config.get("fvg_min_gap_bps", 3))

    # 7. 流动性池
    df = detect_liquidity_levels(df, lookback=config.get("liquidity_lookback", 50))

    # 8. 流动性掠夺
    df = detect_liquidity_sweep(df, tolerance_bps=config.get("sweep_tolerance_bps", 2))

    return df