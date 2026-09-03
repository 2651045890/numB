"""
N型结构交易策略 - 配置文件
"""
import os
from pathlib import Path

# ============================================================
# 交易所配置
# ============================================================
EXCHANGE = {
    'name': 'okx',
    'api_key': "78d8ec37-9f91-4b1e-beca-0123ee448d1f",
    'api_secret': "19DA07F576183E72600FA9C477F0ECED",
    'password': "Li011621..",
    'testnet': False,           # 实盘接口（dry-run只拉数据不下单）
    'sandbox_mode': False,      # 不启用沙箱
}

# ============================================================
# 交易品种（多品种分散，控制在5-8个，避开高相关品种）
# ============================================================
SYMBOLS = [
    'BTC/USDT',    # 低波动率基准
    'ETH/USDT',    # 中波动率
    'SOL/USDT',    # 高波动率
    'LINK/USDT',   # 中波动率，与BTC/ETH相关性较低
    'AVAX/USDT',   # 高波动率
    # 可选：'DOGE/USDT', 'MATIC/USDT', 'ATOM/USDT'
]

# ============================================================
# 策略参数
# ============================================================
STRATEGY = {
    # ---- 核心参数 ----
    'timeframe': '15m',          # 主周期，15分钟
    'ema_period': 40,            # EMA周期（优化后：40 > 20）
    'atr_period': 14,            # ATR周期

    # ---- 波动率过滤 ----
    # 只有当 ATR(14) > ATR_SMA(20) * 0.6 时才交易
    # 优化后：阈值从0.8降至0.6，增加信号数量
    'volatility_filter_enabled': True,
    'volatility_filter_period': 20,    # ATR的SMA周期
    'volatility_filter_threshold': 0.6, # 优化后：0.6（原0.8）

    # ---- 入场 ----
    'min_n_type_candles': 5,     # 最少需要5根K线形成N型结构

    # ---- 出场（分批止盈） ----
    'tp1_ratio': 1.0,            # 第一目标：1:1 盈亏比（优化后：1.0 > 0.75）
    'tp1_size': 0.3,             # 第一目标平30%仓位（优化后：0.3 < 0.5，留更多仓位给趋势跟踪）
    'tp2_size': 0.3,             # 第二目标平30%
    'tp3_size': 0.2,             # 第三目标平20%（趋势跟踪）

    # ---- 均线出场 ----
    'trailing_stop_activated': True,
    'trailing_activation_ratio': 1.0,  # 优化后：TP1触发后立即激活（原2.0）
    'trailing_stop_distance': 0.3,     # 移动止盈距离 = 0.3倍ATR（优化后：0.3 < 0.5）
}

# ============================================================
# 风险管理（核心：单笔止损金额占总资金比例）
# ============================================================
RISK = {
    'risk_per_trade': 0.01,           # 基础单笔止损 = 总资金的1%
    'max_daily_loss': 0.03,           # 每日最大亏损限额 = 3%
    'max_consecutive_losses': 4,       # 连亏4次暂停当日交易
    'max_concurrent_positions': 4,     # 最大同时持仓数
    'min_volume_24h_usdt': 50_000_000, # 最小24h成交量(USDT)，过滤流动性差的品种
    'min_risk_reward_ratio': 0.5,      # 最小盈亏比（由tp1_ratio控制，设为较低值避免冲突）

    # ---- 动态仓位管理（反马丁格尔） ----
    # 盈利后逐步加仓，亏损后回退到基础仓位
    'dynamic_position_enabled': True,   # 是否启用动态仓位
    'anti_martingale_step': 0.0025,    # 每连赢一次增加0.25%风险
    'anti_martingale_max': 0.03,       # 最大单笔风险 = 3%
    'anti_martingale_min': 0.005,      # 最小单笔风险 = 0.5%
}

# ============================================================
# 交易时段
# 加密货币24小时交易，但凌晨流动性差、插针多
# 建议避开 2:00 - 8:00 (UTC+8)
# ============================================================
TRADING_HOURS = {
    'enabled': True,
    'start_hour': 8,     # 8:00 UTC+8
    'end_hour': 2,       # 次日2:00 UTC+8
}

# ============================================================
# 系统参数
# ============================================================
SYSTEM = {
    'check_interval': 60,                # 主循环检查间隔(秒)
    'position_check_interval': 5,        # 持仓盯盘间隔(秒)
    'max_retries': 3,                    # API调用最大重试次数
    'retry_delay': 5,                    # 重试等待(秒)
    'log_level': 'INFO',                 # DEBUG / INFO / WARNING / ERROR
    'log_to_file': True,
    'log_dir': str(Path(__file__).parent / 'logs'),
}

# ============================================================
# 杠杆设置
# ============================================================
LEVERAGE = {
    'enabled': True,
    'default_leverage': 3,  # 3倍杠杆，配合1%风险控制
    'max_leverage': 5,
}

# ============================================================
# 打印当前配置
# ============================================================
def print_config():
    print("=" * 60)
    print("N型结构交易策略 - 配置摘要")
    print("=" * 60)
    print(f"  交易所:        {EXCHANGE['name']} (模拟盘: {EXCHANGE['testnet']})")
    print(f"  交易品种:      {', '.join(SYMBOLS)}")
    print(f"  主周期:        {STRATEGY['timeframe']}")
    print(f"  EMA周期:       {STRATEGY['ema_period']}")
    print(f"  波动率过滤:    {'开启' if STRATEGY['volatility_filter_enabled'] else '关闭'}")
    print(f"  单笔风险:      {RISK['risk_per_trade']*100:.1f}%")
    print(f"  每日最大亏损:  {RISK['max_daily_loss']*100:.1f}%")
    print(f"  最大连亏暂停:  {RISK['max_consecutive_losses']}次")
    print(f"  最大同时持仓:  {RISK['max_concurrent_positions']}")
    print(f"  交易时段:      {'限制' if TRADING_HOURS['enabled'] else '不限制'}")
    print(f"  杠杆:          {LEVERAGE['default_leverage']}x (最大{LEVERAGE['max_leverage']}x)")
    print("=" * 60)


# ============================================================
# 统一配置字典（供程序内部使用）
# ============================================================
config = {
    'EXCHANGE': EXCHANGE,
    'SYMBOLS': SYMBOLS,
    'STRATEGY': STRATEGY,
    'RISK': RISK,
    'TRADING_HOURS': TRADING_HOURS,
    'SYSTEM': SYSTEM,
    'LEVERAGE': LEVERAGE,
}


if __name__ == '__main__':
    print_config()