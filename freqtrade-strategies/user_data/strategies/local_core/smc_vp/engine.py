"""
回测引擎 — 执行 SMC + VP 策略的历史回测
"""
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from strategy.smc_vp_strategy import Signal
from utils.helpers import (
    calculate_sharpe_ratio, calculate_max_drawdown,
    calculate_win_rate, calculate_profit_factor,
    calculate_avg_holding_time, calculate_sortino_ratio,
    calculate_calmar_ratio
)


@dataclass
class Trade:
    """成交记录"""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    position_size: float  # 合约数量
    position_value: float  # 名义价值 (USDT)
    pnl: float  # 盈亏 (USDT)
    pnl_pct: float  # 盈亏百分比
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    exit_reason: str  # "tp1", "tp2", "stop_loss", "manual"
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    max_favorable: float = 0.0
    max_adverse: float = 0.0


@dataclass
class BacktestResult:
    """回测结果汇总"""
    symbol: str
    total_trades: int
    win_rate: float
    profit_factor: float
    total_pnl: float
    total_pnl_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    avg_holding_time: float
    avg_win: float
    avg_loss: float
    best_trade: float
    worst_trade: float
    consecutive_wins: int
    consecutive_losses: int
    trades: List[Trade] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    daily_returns: List[float] = field(default_factory=list)


class BacktestEngine:
    """
    回测引擎

    支持：
    - 多币种独立回测
    - 动态仓位管理（2% 资金）
    - TP1/SL/TP2 三级目标
    - 手续费与滑点
    - 最大同时持仓限制
    """

    def __init__(self, config: Dict):
        self.config = config
        self.trading_cfg = config.get("trading", {})
        self.initial_capital = self.trading_cfg.get("initial_capital", 10000.0)
        self.position_size_pct = self.trading_cfg.get("position_size_pct", 0.02)
        self.commission = self.trading_cfg.get("commission", 0.0005)
        self.slippage = self.trading_cfg.get("slippage", 0.0003)
        self.max_concurrent = self.trading_cfg.get("max_concurrent_trades", 3)
        self.tp1_size_pct = self.trading_cfg.get("tp1_size_pct", 0.5)

    def run_single(self, symbol: str, htf_df: pd.DataFrame, ltf_df: pd.DataFrame, vp_data: Dict, signals: List[Signal]) -> BacktestResult:
        """
        对单一币种执行回测
        """
        trades = []
        equity = [self.initial_capital]
        balance = self.initial_capital
        active_positions = []  # 当前持仓列表

        # 将信号按时间排序
        signals = sorted(signals, key=lambda s: s.timestamp)

        # 将 LTF 数据转为时间索引字典，便于快速查找
        ltf_dict = {}
        for _, row in ltf_df.iterrows():
            ltf_dict[row["timestamp"]] = row

        for signal in signals:
            # 检查是否达到最大同时持仓
            if len(active_positions) >= self.max_concurrent:
                continue

            # 检查是否有足够资金
            if balance <= 0:
                break

            # 计算仓位大小（动态 2%）
            position_value = balance * self.position_size_pct
            entry_price = signal.entry_price * (1 + self.slippage * (1 if signal.side == "long" else -1))
            position_size = position_value / entry_price

            # 找出该信号的时间范围内 LTF 数据
            entry_idx = signal.timestamp
            # 往后看最多 48 根 LTF（5m * 48 = 4 小时）
            max_lookahead = 48

            # 找到 entry 在 LTF 中的位置
            entry_loc = None
            for idx, t in enumerate(ltf_df["timestamp"]):
                if t >= entry_idx:
                    entry_loc = idx
                    break

            if entry_loc is None:
                continue

            # 模拟持仓过程
            position = {
                "signal": signal,
                "entry_price": entry_price,
                "entry_time": entry_idx,
                "position_size": position_size,
                "position_value": position_value,
                "remaining_size": position_size,
                "remaining_pct": 1.0,
                "tp1_hit": False,
                "max_fav": 0.0,
                "max_adv": 0.0,
            }
            active_positions.append(position)  # 添加到持仓列表，确保 max_concurrent_trades 生效

            trade_closed = False
            exit_price = entry_price
            exit_reason = "manual"

            for j in range(entry_loc, min(entry_loc + max_lookahead, len(ltf_df))):
                bar = ltf_df.iloc[j]
                bar_time = bar["timestamp"]

                # 更新最大有利/不利波动
                if signal.side == "long":
                    position["max_fav"] = max(position["max_fav"], bar["high"] - entry_price)
                    position["max_adv"] = min(position["max_adv"], bar["low"] - entry_price)
                else:
                    position["max_fav"] = max(position["max_fav"], entry_price - bar["low"])
                    position["max_adv"] = min(position["max_adv"], entry_price - bar["high"])

                # 检查止损
                if signal.side == "long":
                    if bar["low"] <= signal.stop_loss:
                        exit_price = signal.stop_loss * (1 - self.slippage)
                        exit_reason = "stop_loss"
                        trade_closed = True
                        break
                else:
                    if bar["high"] >= signal.stop_loss:
                        exit_price = signal.stop_loss * (1 + self.slippage)
                        exit_reason = "stop_loss"
                        trade_closed = True
                        break

                # 检查 TP1（先平一半）
                if not position["tp1_hit"]:
                    tp1_hit = False
                    if signal.side == "long":
                        if bar["high"] >= signal.take_profit_1:
                            tp1_hit = True
                    else:
                        if bar["low"] <= signal.take_profit_1:
                            tp1_hit = True

                    if tp1_hit:
                        position["tp1_hit"] = True
                        # TP1 平一半
                        tp1_exit = signal.take_profit_1
                        tp1_exit_price = tp1_exit * (1 - self.slippage * (1 if signal.side == "long" else -1))
                        partial_size = position["remaining_size"] * self.tp1_size_pct
                        partial_pnl = (tp1_exit_price - entry_price) * partial_size if signal.side == "long" \
                            else (entry_price - tp1_exit_price) * partial_size
                        partial_pnl -= partial_pnl * self.commission * 2

                        # 记录部分平仓
                        trades.append(Trade(
                            entry_time=entry_idx,
                            exit_time=bar_time,
                            symbol=symbol,
                            side=signal.side,
                            entry_price=entry_price,
                            exit_price=tp1_exit_price,
                            position_size=partial_size,
                            position_value=partial_size * entry_price,
                            pnl=partial_pnl,
                            pnl_pct=partial_pnl / (partial_size * entry_price) * 100,
                            stop_loss=signal.stop_loss,
                            take_profit_1=signal.take_profit_1,
                            take_profit_2=signal.take_profit_2,
                            exit_reason="tp1",
                            confidence=signal.confidence,
                            reasons=signal.reasons,
                            max_favorable=position["max_fav"],
                            max_adverse=position["max_adv"],
                        ))

                        balance += partial_pnl
                        position["remaining_size"] -= partial_size
                        position["remaining_pct"] = position["remaining_size"] / position_size

                # 检查 TP2（剩余仓位）
                tp2_hit = False
                if signal.side == "long":
                    if bar["high"] >= signal.take_profit_2:
                        tp2_hit = True
                else:
                    if bar["low"] <= signal.take_profit_2:
                        tp2_hit = True

                if tp2_hit:
                    tp2_exit_price = signal.take_profit_2 * (1 - self.slippage * (1 if signal.side == "long" else -1))
                    remaining_pnl = (tp2_exit_price - entry_price) * position["remaining_size"] if signal.side == "long" \
                        else (entry_price - tp2_exit_price) * position["remaining_size"]
                    remaining_pnl -= remaining_pnl * self.commission * 2

                    trades.append(Trade(
                        entry_time=entry_idx,
                        exit_time=bar_time,
                        symbol=symbol,
                        side=signal.side,
                        entry_price=entry_price,
                        exit_price=tp2_exit_price,
                        position_size=position["remaining_size"],
                        position_value=position["remaining_size"] * entry_price,
                        pnl=remaining_pnl,
                        pnl_pct=remaining_pnl / (position["remaining_size"] * entry_price) * 100,
                        stop_loss=signal.stop_loss,
                        take_profit_1=signal.take_profit_1,
                        take_profit_2=signal.take_profit_2,
                        exit_reason="tp2",
                        confidence=signal.confidence,
                        reasons=signal.reasons,
                        max_favorable=position["max_fav"],
                        max_adverse=position["max_adv"],
                    ))

                    balance += remaining_pnl
                    trade_closed = True
                    break

            # 如果持仓未平仓，在最后一根 K 线强制平仓
            if not trade_closed and position["remaining_size"] > 0:
                last_bar = ltf_df.iloc[min(entry_loc + max_lookahead - 1, len(ltf_df) - 1)]
                exit_price = last_bar["close"]
                exit_reason = "time_exit"
                remaining_pnl = (exit_price - entry_price) * position["remaining_size"] if signal.side == "long" \
                    else (entry_price - exit_price) * position["remaining_size"]
                remaining_pnl -= remaining_pnl * self.commission * 2

                trades.append(Trade(
                    entry_time=entry_idx,
                    exit_time=last_bar["timestamp"],
                    symbol=symbol,
                    side=signal.side,
                    entry_price=entry_price,
                    exit_price=exit_price,
                    position_size=position["remaining_size"],
                    position_value=position["remaining_size"] * entry_price,
                    pnl=remaining_pnl,
                    pnl_pct=remaining_pnl / (position["remaining_size"] * entry_price) * 100,
                    stop_loss=signal.stop_loss,
                    take_profit_1=signal.take_profit_1,
                    take_profit_2=signal.take_profit_2,
                    exit_reason=exit_reason,
                    confidence=signal.confidence,
                    reasons=signal.reasons,
                    max_favorable=position["max_fav"],
                    max_adverse=position["max_adv"],
                ))
                balance += remaining_pnl

            equity.append(balance)

            # 从持仓列表中移除已完成的持仓，释放 max_concurrent_trades 名额
            if position in active_positions:
                active_positions.remove(position)

        # 计算回测统计
        return self._compute_results(symbol, trades, equity)

    def _compute_results(self, symbol: str, trades: List[Trade], equity: List[float]) -> BacktestResult:
        """计算回测统计数据"""
        if not trades:
            return BacktestResult(
                symbol=symbol, total_trades=0, win_rate=0.0,
                profit_factor=0.0, total_pnl=0.0, total_pnl_pct=0.0,
                sharpe_ratio=0.0, sortino_ratio=0.0, calmar_ratio=0.0,
                max_drawdown=0.0, avg_holding_time=0.0,
                avg_win=0.0, avg_loss=0.0, best_trade=0.0,
                worst_trade=0.0, consecutive_wins=0, consecutive_losses=0,
                trades=[], equity_curve=equity, daily_returns=[]
            )

        pnls = [t.pnl for t in trades]
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl < 0]

        total_pnl = sum(pnls)
        total_pnl_pct = (equity[-1] - self.initial_capital) / self.initial_capital * 100

        win_rate = calculate_win_rate([{"pnl": t.pnl} for t in trades])
        profit_factor = calculate_profit_factor([{"pnl": t.pnl} for t in trades])

        # 日收益率
        if len(equity) > 1:
            daily_returns = [
                (equity[i] - equity[i - 1]) / equity[i - 1]
                for i in range(1, len(equity))
            ]
        else:
            daily_returns = []

        sharpe = calculate_sharpe_ratio(daily_returns)
        sortino = calculate_sortino_ratio(daily_returns)
        max_dd = calculate_max_drawdown(equity)
        calmar = calculate_calmar_ratio(daily_returns, equity)

        avg_holding = calculate_avg_holding_time([{
            "entry_time": t.entry_time, "exit_time": t.exit_time
        } for t in trades])

        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0.0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0.0
        best_trade = max(t.pnl for t in trades)
        worst_trade = min(t.pnl for t in trades)

        # 连续胜/败
        cons_wins = 0
        cons_losses = 0
        max_cons_wins = 0
        max_cons_losses = 0
        for t in trades:
            if t.pnl > 0:
                cons_wins += 1
                cons_losses = 0
                max_cons_wins = max(max_cons_wins, cons_wins)
            else:
                cons_losses += 1
                cons_wins = 0
                max_cons_losses = max(max_cons_losses, cons_losses)

        return BacktestResult(
            symbol=symbol,
            total_trades=len(trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_pnl=total_pnl,
            total_pnl_pct=total_pnl_pct,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            max_drawdown=max_dd,
            avg_holding_time=avg_holding,
            avg_win=avg_win,
            avg_loss=avg_loss,
            best_trade=best_trade,
            worst_trade=worst_trade,
            consecutive_wins=max_cons_wins,
            consecutive_losses=max_cons_losses,
            trades=trades,
            equity_curve=equity,
            daily_returns=daily_returns,
        )


def run_backtest_for_symbol(symbol: str, htf_data: pd.DataFrame, ltf_data: pd.DataFrame, vp_data: Dict, signals: List[Signal], config: Dict) -> BacktestResult:
    """
    对单一币种执行完整回测
    """
    engine = BacktestEngine(config)
    return engine.run_single(symbol, htf_data, ltf_data, vp_data, signals)
