"""
风险管理模块

核心原则:
- 单笔止损 = 总资金 * 风险比例
- 根据止损距离倒推算仓量
- 每日最大亏损限额
- 连亏N次暂停交易
- 最大同时持仓限制
"""
import datetime
import logging
from collections import deque

logger = logging.getLogger(__name__)


class RiskManager:
    """风控管理器"""

    def __init__(self, config):
        self.config = config
        risk_conf = config['RISK']

        self.risk_per_trade = risk_conf['risk_per_trade']       # 基础单笔止损比例
        self.max_daily_loss = risk_conf['max_daily_loss']       # 每日最大亏损
        self.max_consecutive_losses = risk_conf['max_consecutive_losses']  # 最大连亏
        self.max_concurrent_positions = risk_conf['max_concurrent_positions']

        # 反马丁格尔动态仓位
        self.dynamic_enabled = risk_conf.get('dynamic_position_enabled', True)
        self.anti_step = risk_conf.get('anti_martingale_step', 0.0025)
        self.anti_max = risk_conf.get('anti_martingale_max', 0.03)
        self.anti_min = risk_conf.get('anti_martingale_min', 0.005)
        self.current_risk_pct = self.risk_per_trade  # 当前使用的风险比例

        # 交易记录
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.consecutive_losses = 0
        self.consecutive_wins = 0
        self.last_loss_date = None
        self.trade_history = deque(maxlen=100)  # 保留最近100笔交易记录
        self.current_positions = 0

        # 重置日计数器
        self._reset_daily()

    def _reset_daily(self):
        """重置每日统计"""
        today = datetime.datetime.now().date()
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.current_date = today

    def _check_reset_daily(self):
        """检查是否需要重置每日统计"""
        today = datetime.datetime.now().date()
        if today != self.current_date:
            self._reset_daily()
            return True
        return False

    def calculate_position_size(self, total_balance, entry_price, stop_loss,
                               contract_size, tick_price):
        """
        根据风险控制计算可开仓量 (核心方法)

        公式:
        - 可接受止损金额 = total_balance * current_risk_pct (动态调整)
        - 每合约风险 = abs(entry_price - stop_loss) * contract_size
        - 可开仓量 = 可接受止损金额 / 每合约风险

        参数:
            total_balance: 总资金(USDT)
            entry_price: 入场价
            stop_loss: 止损价
            contract_size: 每张合约面值
            tick_price: 每张合约对应USDT价格

        返回:
            可开仓数量 (张)
        """
        if entry_price == stop_loss:
            return 0

        # 使用当前动态风险比例
        effective_risk = self.current_risk_pct

        # 每币风险距离
        risk_per_unit = abs(entry_price - stop_loss)

        # 可接受的止损金额 = 总资金 × 当前风险比例
        max_risk_amount = total_balance * effective_risk

        # 每张合约风险 = 风险距离 × 合约面值
        if contract_size == 0:
            contract_size = 1

        if contract_size > 0:
            # 如BTC-USDT永续，1张 = 0.01 BTC
            # 风险 = 0.01 * (entry - stop)
            risk_per_contract = contract_size * risk_per_unit
        else:
            risk_per_contract = risk_per_unit

        if risk_per_contract <= 0:
            return 0

        position_size = max_risk_amount / risk_per_contract

        logger.info(f"风控计算: 总资金={total_balance:.2f}, "
                    f"当前风险={effective_risk*100:.2f}%(基础={self.risk_per_trade*100:.1f}%), "
                    f"风险距离={risk_per_unit:.2f}, 每张风险={risk_per_contract:.2f}, "
                    f"开仓张数={position_size:.4f}")

        return position_size

    def check_allow_entry(self):
        """
        检查是否允许开仓

        返回:
            (allowed: bool, reason: str)
        """
        self._check_reset_daily()

        # 连亏次数检查
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"连亏{self.consecutive_losses}次，当日停止交易"

        # 每日亏损检查
        if abs(self.daily_pnl) >= self.config['RISK']['max_daily_loss'] * (self._get_total_balance() or 1):
            return False, f"当日亏损已达上限({abs(self.daily_pnl):.2f})，当日停止交易"

        # 同时持仓检查
        if self.current_positions >= self.max_concurrent_positions:
            return False, f"已达到最大同时持仓数({self.max_concurrent_positions})，无法新开仓"

        # 交易时段检查
        if self.config['TRADING_HOURS']['enabled']:
            allowed = self._check_trading_hours()
            if not allowed:
                return False, "不在允许交易时段"

        return True, None

    def _check_trading_hours(self):
        """检查当前是否在允许交易时段"""
        conf = self.config['TRADING_HOURS']
        now = datetime.datetime.now()
        hour = now.hour

        start = conf['start_hour']
        end = conf['end_hour']

        if start > end:
            # 区间跨天，比如 8:00 - 次日2:00
            return hour >= start or hour < end
        else:
            return start <= hour < end

    def _get_total_balance(self):
        """从历史估算总资金"""
        if not self.trade_history:
            return 10000.0
        return self.trade_history[-1].get('total_balance_after', 10000.0)

    def record_trade(self, pnl, is_win, total_balance_after, symbol=None):
        """记录一笔交易，并更新动态风险比例（反马丁格尔）"""
        self._check_reset_daily()

        self.daily_pnl += pnl
        self.daily_trades += 1

        if is_win:
            self.consecutive_losses = 0
            self.consecutive_wins += 1
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.last_loss_date = datetime.datetime.now()

        # 反马丁格尔：盈利上调风险比例，亏损回退
        if self.dynamic_enabled:
            if is_win:
                self.current_risk_pct = min(
                    self.current_risk_pct + self.anti_step,
                    self.anti_max
                )
            else:
                self.current_risk_pct = max(
                    self.current_risk_pct - self.anti_step,
                    self.anti_min
                )
            logger.info(f"动态仓位: {'盈利↑' if is_win else '亏损↓'} "
                        f"风险={self.current_risk_pct*100:.2f}% "
                        f"(连赢={self.consecutive_wins}, 连亏={self.consecutive_losses})")

        if pnl < 0 and self.consecutive_losses >= self.max_consecutive_losses:
            logger.warning(f"⚠️ 已连续亏损 {self.consecutive_losses} 次，建议当日停止交易")

        self.trade_history.append({
            'time': datetime.datetime.now().isoformat(),
            'pnl': pnl,
            'is_win': is_win,
            'total_balance_after': total_balance_after,
            'symbol': symbol,
        })

        if pnl < 0:
            logger.info(f"风控记录: 交易亏损，连亏={self.consecutive_losses}, 当日累计亏损={abs(self.daily_pnl):.2f}")
        else:
            logger.info(f"风控记录: 交易盈利，连亏重置为0")

    def record_entry(self):
        """记录一次开仓"""
        self.current_positions += 1

    def record_exit(self):
        """记录一次平仓"""
        self.current_positions = max(0, self.current_positions - 1)

    def get_stats(self):
        """获取当前风控统计"""
        return {
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'consecutive_losses': self.consecutive_losses,
            'current_positions': self.current_positions,
            'total_trades': len(self.trade_history),
        }

    def is_trading_allowed(self):
        """快捷检查：当前是否允许交易"""
        allowed, _ = self.check_allow_entry()
        return allowed

    def print_stats(self):
        """打印风控统计"""
        stats = self.get_stats()
        logger.info("=" * 50)
        logger.info("风控统计:")
        logger.info(f"  今日盈亏:     {stats['daily_pnl']:+.2f} USDT")
        logger.info(f"  今日交易次数: {stats['daily_trades']}")
        logger.info(f"  当前连亏:     {stats['consecutive_losses']}")
        logger.info(f"  当前持仓数:   {stats['current_positions']}")
        logger.info(f"  总交易笔数:   {stats['total_trades']}")
        logger.info("=" * 50)