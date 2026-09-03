"""
工具函数
"""
import numpy as np
from typing import Dict, List


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """计算夏普比率"""
    if len(returns) < 2:
        return 0.0
    returns_arr = np.array(returns)
    excess_returns = returns_arr - risk_free_rate / 365
    if np.std(excess_returns) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(365)


def calculate_max_drawdown(equity_curve: List[float]) -> float:
    """计算最大回撤"""
    if len(equity_curve) < 2:
        return 0.0
    peak = equity_curve[0]
    max_dd = 0.0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = (peak - value) / peak
        if dd > max_dd:
            max_dd = dd
    return max_dd


def calculate_win_rate(trades: List[Dict]) -> float:
    """计算胜率"""
    if not trades:
        return 0.0
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    return wins / len(trades)


def calculate_profit_factor(trades: List[Dict]) -> float:
    """计算获利因子（总盈利/总亏损）"""
    if not trades:
        return 0.0
    gross_profit = sum(t["pnl"] for t in trades if t["pnl"] > 0)
    gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] < 0))
    if gross_loss == 0:
        return float("inf") if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def calculate_avg_holding_time(trades: List[Dict]) -> float:
    """计算平均持仓时间（分钟）"""
    if not trades:
        return 0.0
    times = []
    for t in trades:
        if "entry_time" in t and "exit_time" in t:
            delta = (t["exit_time"] - t["entry_time"]).total_seconds() / 60
            times.append(delta)
    return np.mean(times) if times else 0.0


def calculate_sortino_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
    """计算索提诺比率（只考虑下行波动）"""
    if len(returns) < 2:
        return 0.0
    returns_arr = np.array(returns)
    excess_returns = returns_arr - risk_free_rate / 365
    downside = returns_arr[returns_arr < 0]
    if len(downside) == 0 or np.std(downside) == 0:
        return 0.0
    return np.mean(excess_returns) / np.std(downside) * np.sqrt(365)


def calculate_calmar_ratio(returns: List[float], equity_curve: List[float]) -> float:
    """计算卡尔玛比率（年化收益率/最大回撤）"""
    if len(returns) < 2:
        return 0.0
    total_return = np.prod([1 + r for r in returns]) - 1
    annual_return = (1 + total_return) ** (365 / len(returns)) - 1
    max_dd = calculate_max_drawdown(equity_curve)
    if max_dd == 0:
        return 0.0
    return annual_return / max_dd