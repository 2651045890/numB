"""
N型结构策略核心模块

策略逻辑（均线之上等向上N型，均线之下等向下N型）：

多头N型：
  H2 ────┐  ← 突破前高，入场做多
          │
  H1 ──┐  │
       │  │
  L1 ──┘  │  ← 回调不破均线，形成更高低点
       │
  ─────EMA─────  ← 价格站上均线
       │

空头N型（对称）：
  ─────EMA─────
       │
  H1 ──┐  │  ← 反弹不破均线，形成更低高点
       │  │
  L1 ──┘  │
          │
  L2 ──────┘  ← 跌破前低，入场做空

状态机：IDLE → ABOVE_EMA → H1_FOUND → PULLBACK_L1 → ENTRY_TRIGGER
        IDLE → BELOW_EMA → L1_FOUND → PULLBACK_H1 → ENTRY_TRIGGER
"""
import numpy as np
import pandas as pd
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class SignalType(Enum):
    """信号类型"""
    NONE = 0
    LONG = 1   # 多头N型突破
    SHORT = 2  # 空头N型突破


class ExitReason(Enum):
    """出场原因"""
    STOP_LOSS = 'stop_loss'
    TAKE_PROFIT_1 = 'take_profit_1'
    TAKE_PROFIT_2 = 'take_profit_2'
    TRAILING_STOP = 'trailing_stop'
    EMA_BREAK = 'ema_break'
    MANUAL = 'manual'


class NTypeState:
    """单个品种的N型结构状态机"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.reset()

    def reset(self):
        self.state = 'IDLE'           # 当前状态
        self.direction = None         # 'bullish' | 'bearish' | None
        self.h1 = None                # 第一个摆动高点
        self.h1_idx = None            # 摆动高点索引
        self.l1 = None                # 回调摆动低点
        self.l1_idx = None            # 回调低点索引
        self.cross_idx = None         # 穿越均线的索引
        self.latest_signal = None     # 最新信号

    def __repr__(self):
        return (f"NTypeState({self.symbol}, state={self.state}, "
                f"dir={self.direction}, h1={self.h1}, l1={self.l1})")


class NTypeStrategy:
    """
    N型结构策略

    核心逻辑：
    1. 价格站上EMA后，寻找第一个摆动高点H1
    2. 回调不破EMA，形成更高低点L1
    3. 突破H1时入场做多
    4. 反之亦然做空

    附加过滤：
    - 波动率过滤（ATR > SMA）
    - 最小盈亏比过滤
    - 连续性检查（回调后必须再次突破）
    """

    def __init__(self, config):
        self.config = config
        sc = config['STRATEGY']
        self.ema_period = sc['ema_period']
        self.atr_period = sc['atr_period']
        self.vol_filter_enabled = sc['volatility_filter_enabled']
        self.vol_filter_period = sc['volatility_filter_period']
        self.vol_filter_threshold = sc['volatility_filter_threshold']
        self.min_risk_reward = config['RISK']['min_risk_reward_ratio']

        # 每个品种独立的状态机
        self.states: dict[str, NTypeState] = {}

    def _get_state(self, symbol):
        if symbol not in self.states:
            self.states[symbol] = NTypeState(symbol)
        return self.states[symbol]

    # ================================================================
    # 技术指标计算
    # ================================================================

    def _calc_ema(self, close, period=None):
        """计算EMA"""
        return pd.Series(close).ewm(span=period or self.ema_period, adjust=False).mean().values

    def _calc_atr(self, high, low, close):
        """计算ATR（平均真实波幅）"""
        tr = np.zeros(len(close))
        for i in range(1, len(close)):
            hl = high[i] - low[i]
            hc = abs(high[i] - close[i - 1])
            lc = abs(low[i] - close[i - 1])
            tr[i] = max(hl, hc, lc)
        tr[0] = tr[1] if len(tr) > 1 else 0
        return pd.Series(tr).rolling(self.atr_period).mean().values

    def _calc_volume_sma(self, volume, period=20):
        """计算成交量均线"""
        return pd.Series(volume).rolling(period).mean().values

    # ================================================================
    # 波动率过滤
    # ================================================================

    def _check_volatility(self, atr_values):
        """
        波动率过滤：判断市场是否处于可交易状态
        当 ATR(14) > ATR_SMA(20) * 0.8 时认为市场有趋势/波动
        否则认为处于横盘震荡，不交易
        """
        if not self.vol_filter_enabled:
            return True, 0

        current_atr = atr_values[-1]
        atr_sma = pd.Series(atr_values).rolling(self.vol_filter_period).mean().iloc[-1]
        threshold = atr_sma * self.vol_filter_threshold

        if np.isnan(current_atr) or np.isnan(atr_sma):
            return False, 0

        is_tradeable = current_atr >= threshold
        if not is_tradeable:
            logger.debug(f"波动率过滤: ATR={current_atr:.4f} < 阈值={threshold:.4f}，不交易")
        return is_tradeable, current_atr

    # ================================================================
    # 摆动点检测
    # ================================================================

    def _is_swing_high(self, high, idx, lookback=2):
        """检测idx是否为摆动高点（两侧各lookback根K线内最高）"""
        start = max(0, idx - lookback)
        end = min(len(high), idx + lookback + 1)
        if idx - start < lookback or end - idx - 1 < lookback:
            return False
        return high[idx] == max(high[start:end])

    def _is_swing_low(self, low, idx, lookback=2):
        """检测idx是否为摆动低点"""
        start = max(0, idx - lookback)
        end = min(len(low), idx + lookback + 1)
        if idx - start < lookback or end - idx - 1 < lookback:
            return False
        return low[idx] == min(low[start:end])

    # ================================================================
    # 回调确认
    # ================================================================

    def _confirm_pullback(self, high, low, close, ema, idx, direction):
        """
        确认回调结束
        direction='bullish': 回调不破EMA，然后出现阳线
        direction='bearish': 回调不破EMA，然后出现阴线
        """
        if idx < 1 or idx >= len(close) - 1:
            return False

        if direction == 'bullish':
            if low[idx] <= ema[idx]:
                return False
            # 回调后的第一根K线收阳
            return close[idx] > close[idx - 1]
        else:
            if high[idx] >= ema[idx]:
                return False
            return close[idx] < close[idx - 1]

    # ================================================================
    # 趋势方向判断（用于过滤N型的方向）
    # ================================================================

    def _is_uptrend(self, close, ema):
        """判断短期趋势方向：价格是否在EMA之上"""
        return close[-1] > ema[-1]

    # ================================================================
    # 核心：N型结构检测
    # ================================================================

    def analyze(self, symbol, ohlcv_data):
        """
        分析最新K线，检测N型结构信号

        参数:
            symbol: 交易对
            ohlcv_data: 原始K线数据 [[timestamp, open, high, low, close, volume], ...]

        返回:
            dict or None: {
                'signal': 'long' | 'short',
                'entry_price': float,
                'stop_loss': float,
                'take_profit_1': float,
                'take_profit_2': float,
                'atr': float,
                'current_price': float,
            }
        """
        if not ohlcv_data or len(ohlcv_data) < 50:
            logger.warning(f"[{symbol}] K线数据不足")
            return None

        # 转为DataFrame并计算指标
        df = pd.DataFrame(
            ohlcv_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        df['ema'] = self._calc_ema(df['close'].values)
        df['atr'] = self._calc_atr(
            df['high'].values, df['low'].values, df['close'].values
        )

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        ema = df['ema'].values
        atr = df['atr'].values
        latest = len(df) - 1

        # ---- 波动率过滤 ----
        vol_ok, current_atr = self._check_volatility(atr)
        if not vol_ok:
            self._get_state(symbol).reset()
            return None

        # ---- 状态机 ----
        state_obj = self._get_state(symbol)
        current_close = close[latest]
        current_ema = ema[latest]
        current_high = high[latest]
        current_low = low[latest]

        # 重置条件：价格穿越到EMA对面
        if state_obj.state not in ('IDLE',):
            if state_obj.direction == 'bullish' and current_close < current_ema:
                logger.debug(f"[{symbol}] 价格跌破EMA，重置多头状态")
                state_obj.reset()
            elif state_obj.direction == 'bearish' and current_close > current_ema:
                logger.debug(f"[{symbol}] 价格突破EMA，重置空头状态")
                state_obj.reset()

        # ================================================================
        # 状态机流转
        # ================================================================

        if state_obj.state == 'IDLE':
            # 判断方向：价格在EMA之上还是之下
            if current_close > current_ema:
                # 可能构建多头N型
                if close[latest - 1] <= ema[latest - 1]:
                    # 刚穿越EMA
                    state_obj.state = 'ABOVE_EMA'
                    state_obj.direction = 'bullish'
                    state_obj.cross_idx = latest
                    logger.debug(f"[{symbol}] 穿越EMA↑，开始寻找多头N型")
                elif close[latest - 1] > ema[latest - 1]:
                    # 已经在EMA之上
                    state_obj.state = 'ABOVE_EMA'
                    state_obj.direction = 'bullish'
                    state_obj.cross_idx = latest - 5
                    logger.debug(f"[{symbol}] 已在EMA之上，寻找多头N型")
            else:
                # 可能构建空头N型
                if close[latest - 1] >= ema[latest - 1]:
                    state_obj.state = 'BELOW_EMA'
                    state_obj.direction = 'bearish'
                    state_obj.cross_idx = latest
                    logger.debug(f"[{symbol}] 穿越EMA↓，开始寻找空头N型")
                elif close[latest - 1] < ema[latest - 1]:
                    state_obj.state = 'BELOW_EMA'
                    state_obj.direction = 'bearish'
                    state_obj.cross_idx = latest - 5
                    logger.debug(f"[{symbol}] 已在EMA之下，寻找空头N型")

        # ---- 多头N型：在EMA之上寻找H1-L1-H2结构 ----
        elif state_obj.state == 'ABOVE_EMA':
            if current_close < current_ema:
                state_obj.reset()
                return None

            # 寻找摆动高点H1
            if state_obj.h1 is None:
                for i in range(max(state_obj.cross_idx + 1, latest - 3), latest + 1):
                    if i < 2 or i >= len(high) - 1:
                        continue
                    if (self._is_swing_high(high, i) and
                            high[i] > ema[i] and
                            close[i] > ema[i]):
                        state_obj.h1 = high[i]
                        state_obj.h1_idx = i
                        state_obj.state = 'H1_FOUND'
                        logger.debug(f"[{symbol}] 多头H1形成: {high[i]:.2f}")
                        break

        elif state_obj.state == 'H1_FOUND':
            if current_close < current_ema:
                logger.debug(f"[{symbol}] 多头H1后跌破EMA，重置")
                state_obj.reset()
                return None

            # 寻找回调低点L1（不破EMA）
            if state_obj.l1 is None:
                for i in range(max(state_obj.h1_idx + 1, latest - 3), latest + 1):
                    if i < 2 or i >= len(low) - 1:
                        continue
                    if (self._is_swing_low(low, i) and
                            low[i] > ema[i] and
                            low[i] < state_obj.h1):
                        state_obj.l1 = low[i]
                        state_obj.l1_idx = i
                        state_obj.state = 'PULLBACK_L1'
                        logger.debug(f"[{symbol}] 多头L1形成: {low[i]:.2f}")

                        # 立即检查：L1之前是否已有K线突破H1
                        for j in range(state_obj.h1_idx + 1, i + 1):
                            if high[j] > state_obj.h1:
                                entry_price = state_obj.h1
                                stop_loss = state_obj.l1
                                risk_dist = entry_price - stop_loss
                                if risk_dist <= 0 or risk_dist / entry_price < 0.0001:
                                    break
                                tp1 = entry_price + risk_dist * self.config['STRATEGY']['tp1_ratio']
                                rr = (tp1 - entry_price) / risk_dist
                                if rr < self.min_risk_reward:
                                    break
                                signal = {
                                    'signal': 'long',
                                    'entry_price': round(entry_price, 2),
                                    'stop_loss': round(stop_loss, 2),
                                    'take_profit_1': round(tp1, 2),
                                    'atr': round(current_atr, 4),
                                    'current_price': round(current_close, 2),
                                }
                                logger.info(f"[{symbol}] ★ 多头N型信号(即时)! 入场={entry_price:.2f}, "
                                           f"止损={stop_loss:.2f}, 目标={tp1:.2f}")
                                state_obj.reset()
                                return signal
                        break

        elif state_obj.state == 'PULLBACK_L1':
            if current_close < current_ema:
                state_obj.reset()
                return None

            # 突破H1，入场信号
            # 修复：扫描L1之后的所有K线，不只看最新一根
            for i in range(state_obj.l1_idx + 1, latest + 1):
                if high[i] > state_obj.h1:
                    entry_price = state_obj.h1
                    stop_loss = state_obj.l1
                    risk_dist = entry_price - stop_loss

                    if risk_dist <= 0 or risk_dist / entry_price < 0.0001:
                        state_obj.reset()
                        return None

                    # 计算止盈
                    tp1 = entry_price + risk_dist * self.config['STRATEGY']['tp1_ratio']

                    # 盈亏比检查
                    rr = (tp1 - entry_price) / risk_dist
                    if rr < self.min_risk_reward:
                        logger.debug(f"[{symbol}] 盈亏比不足: {rr:.2f} < {self.min_risk_reward}")
                        state_obj.reset()
                        return None

                    signal = {
                        'signal': 'long',
                        'entry_price': round(entry_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'take_profit_1': round(tp1, 2),
                        'atr': round(current_atr, 4),
                        'current_price': round(current_close, 2),
                    }
                    logger.info(f"[{symbol}] ★ 多头N型信号! 入场={entry_price:.2f}, "
                               f"止损={stop_loss:.2f}, 目标={tp1:.2f}")
                    state_obj.reset()
                    return signal

        # ---- 空头N型：在EMA之下寻找L1-H1-L2结构 ----
        elif state_obj.state == 'BELOW_EMA':
            if current_close > current_ema:
                state_obj.reset()
                return None

            if state_obj.l1 is None:
                for i in range(max(state_obj.cross_idx + 1, latest - 3), latest + 1):
                    if i < 2 or i >= len(low) - 1:
                        continue
                    if (self._is_swing_low(low, i) and
                            low[i] < ema[i] and
                            close[i] < ema[i]):
                        state_obj.l1 = low[i]
                        state_obj.l1_idx = i
                        state_obj.state = 'L1_FOUND'
                        logger.debug(f"[{symbol}] 空头L1形成: {low[i]:.2f}")
                        break

        elif state_obj.state == 'L1_FOUND':
            if current_close > current_ema:
                state_obj.reset()
                return None

            if state_obj.h1 is None:
                for i in range(max(state_obj.l1_idx + 1, latest - 3), latest + 1):
                    if i < 2 or i >= len(high) - 1:
                        continue
                    if (self._is_swing_high(high, i) and
                            high[i] < ema[i] and
                            high[i] > state_obj.l1):
                        state_obj.h1 = high[i]
                        state_obj.h1_idx = i
                        state_obj.state = 'PULLBACK_H1'
                        logger.debug(f"[{symbol}] 空头H1形成: {high[i]:.2f}")

                        # 立即检查：H1之前是否已有K线跌破L1
                        for j in range(state_obj.l1_idx + 1, i + 1):
                            if low[j] < state_obj.l1:
                                entry_price = state_obj.l1
                                stop_loss = state_obj.h1
                                risk_dist = stop_loss - entry_price
                                if risk_dist <= 0 or risk_dist / entry_price < 0.0001:
                                    break
                                tp1 = entry_price - risk_dist * self.config['STRATEGY']['tp1_ratio']
                                rr = (entry_price - tp1) / risk_dist
                                if rr < self.min_risk_reward:
                                    break
                                signal = {
                                    'signal': 'short',
                                    'entry_price': round(entry_price, 2),
                                    'stop_loss': round(stop_loss, 2),
                                    'take_profit_1': round(tp1, 2),
                                    'atr': round(current_atr, 4),
                                    'current_price': round(current_close, 2),
                                }
                                logger.info(f"[{symbol}] ★ 空头N型信号(即时)! 入场={entry_price:.2f}, "
                                           f"止损={stop_loss:.2f}, 目标={tp1:.2f}")
                                state_obj.reset()
                                return signal
                        break

        elif state_obj.state == 'PULLBACK_H1':
            if current_close > current_ema:
                state_obj.reset()
                return None

            # 修复：扫描H1之后的所有K线，不只看最新一根
            for i in range(state_obj.h1_idx + 1, latest + 1):
                if low[i] < state_obj.l1:
                    entry_price = state_obj.l1
                    stop_loss = state_obj.h1
                    risk_dist = stop_loss - entry_price

                    if risk_dist <= 0 or risk_dist / entry_price < 0.0001:
                        state_obj.reset()
                        return None

                    tp1 = entry_price - risk_dist * self.config['STRATEGY']['tp1_ratio']
                    rr = (entry_price - tp1) / risk_dist
                    if rr < self.min_risk_reward:
                        logger.debug(f"[{symbol}] 盈亏比不足: {rr:.2f} < {self.min_risk_reward}")
                        state_obj.reset()
                        return None

                    signal = {
                        'signal': 'short',
                        'entry_price': round(entry_price, 2),
                        'stop_loss': round(stop_loss, 2),
                        'take_profit_1': round(tp1, 2),
                        'atr': round(current_atr, 4),
                        'current_price': round(current_close, 2),
                    }
                    logger.info(f"[{symbol}] ★ 空头N型信号! 入场={entry_price:.2f}, "
                               f"止损={stop_loss:.2f}, 目标={tp1:.2f}")
                    state_obj.reset()
                    return signal

        return None

    # ================================================================
    # 出场逻辑
    # ================================================================

    def check_exit(self, symbol, position, current_price, entry_price,
                   stop_loss, take_profit_1, atr, direction):
        """
        检查出场条件

        出场规则：
        1. 止损：价格触及止损位
        2. 第一目标(TP1)：1:1盈亏比，平50%
        3. 第二目标(TP2)：价格破EMA/均线，平30%
        4. 第三目标(TP3)：移动止盈，平20%

        返回:
            {
                'should_exit': bool,
                'exit_size': float,      # 0.0-1.0
                'exit_reason': str,
                'close_all': bool,
            }
        """
        if position is None:
            return None

        contracts = float(position.get('contracts', 0))
        if contracts <= 0:
            return None

        result = {
            'should_exit': False,
            'exit_size': 0.0,
            'exit_reason': None,
            'close_all': False,
        }

        if direction == 'long':
            # 止损
            if current_price <= stop_loss:
                result['should_exit'] = True
                result['exit_size'] = 1.0
                result['exit_reason'] = 'stop_loss'
                result['close_all'] = True
                return result

            # TP1 (1:1)
            if current_price >= take_profit_1:
                result['should_exit'] = True
                result['exit_size'] = self.config['STRATEGY']['tp1_size']
                result['exit_reason'] = 'take_profit_1'
                return result

        else:
            if current_price >= stop_loss:
                result['should_exit'] = True
                result['exit_size'] = 1.0
                result['exit_reason'] = 'stop_loss'
                result['close_all'] = True
                return result

            if current_price <= take_profit_1:
                result['should_exit'] = True
                result['exit_size'] = self.config['STRATEGY']['tp1_size']
                result['exit_reason'] = 'take_profit_1'
                return result

        return result

    def check_trailing_exit(self, symbol, position, current_price,
                            entry_price, stop_loss, atr, direction,
                            highest_price=None, lowest_price=None):
        """
        检查移动止盈出场（用于TP1之后的剩余仓位）

        规则（从config读取）：
        - trailing_activation_ratio: TP1后达到该盈亏比即激活（优化值：1.0）
        - trailing_stop_distance: 移动止盈距离 = N倍ATR（优化值：0.3）
        """
        act_ratio = self.config['STRATEGY']['trailing_activation_ratio']
        trail_dist = self.config['STRATEGY']['trailing_stop_distance']
        if direction == 'long':
            if highest_price and current_price >= entry_price + atr * act_ratio:
                trail_stop = highest_price - atr * trail_dist
                if current_price <= trail_stop:
                    return {
                        'should_exit': True,
                        'exit_size': 1.0,
                        'exit_reason': 'trailing_stop',
                        'close_all': True,
                    }
        else:
            if lowest_price and current_price <= entry_price - atr * act_ratio:
                trail_stop = lowest_price + atr * trail_dist
                if current_price >= trail_stop:
                    return {
                        'should_exit': True,
                        'exit_size': 1.0,
                        'exit_reason': 'trailing_stop',
                        'close_all': True,
                    }

        return None

    def reset_all_states(self):
        """重置所有品种的状态"""
        for state in self.states.values():
            state.reset()
        logger.info("所有品种状态已重置")