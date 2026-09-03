"""
SMC + VP 日内交易系统 — 完整配置参数
支持交易所: Binance (免Key) / OKX (免Key 或 API Key) / Hotcoin (热币，无需 Key)
运行模式: backtest(回测) / live(实盘)
"""
from datetime import datetime, timedelta


# ============================================================
# 运行模式
# ============================================================
# "backtest" — 回测模式，仅下载历史数据并回测，不下单
# "live"     — 实盘模式，连接交易所真实账户，实时下单交易
TRADING_MODE = "live"



# ============================================================
# 交易所选择（数据源）
# ============================================================
# "binance"  — 使用 Binance 永续合约 API（实盘需要 API Key）
# "okx"      — 使用 OKX 永续合约 API（实盘需要 API Key）
# "hotcoin"  — 使用 Hotcoin（热币）永续合约 API（实盘需要 API Key）
EXCHANGE = "okx"


# ============================================================
# OKX 实盘 API 配置（仅 TRADING_MODE="live" 且 EXCHANGE="okx" 时需要）
# ============================================================
# 请到 OKX 官网 https://www.okx.com/account/my-api 创建 API Key
# 需要开通交易权限（Trade）
OKX_LIVE_CONFIG = {
    "api_key": "78d8ec37-9f91-4b1e-beca-0123ee448d1f",              # 你的 OKX API Key
    "api_secret": "19DA07F576183E72600FA9C477F0ECED",           # 你的 OKX Secret Key
    "passphrase": "Li011621..",           # 你的 OKX Passphrase
    "sandbox": False,            # 小资金实盘验证，设为 False 使用真实交易
    # 当 sandbox=True 时，请使用沙盒 URL: https://www.okx.com/account/my-api
    # 沙盒环境不需要真实资金，可以放心测试
}

# ============================================================
# Hotcoin（热币）合约 API 配置（仅 TRADING_MODE="live" 且 EXCHANGE="hotcoin" 时需要）
# ============================================================
# 请到 Hotcoin 官网 https://www.hotcoin.com/ 注册并创建 API Key
# 需要开通交易权限
# 合约 API 文档: https://www.hotcoin.com/zh_CN/docs/?navId=2
HOTCOIN_LIVE_CONFIG = {
    "api_key": "155d2759534c47a8ab802bbeb0364103",              # 你的 Hotcoin API Key（必填！管理后台：[账户中心]→[API管理]→创建API）
    "api_secret": "D763B3F376A71C2DC6506AD2F487C109",           # 你的 Hotcoin Secret Key（必填！创建API后复制保存）
    "base_url": "https://api-ct.hotcoin.fit",  # 合约 API 地址（注意与现货不同）
    # 合约交易对格式: 小写无分隔符，如 btcusdt、ethusdt
    # 下单方向: open_long / open_short / close_long / close_short
    # 订单类型: "10"=限价单, "11"=市价单
    # ⚠️ 重要: 请务必填写以上 api_key 和 api_secret，否则无法连接！
}

# ============================================================
# 币安（Binance）永续合约 API 配置（仅 TRADING_MODE="live" 且 EXCHANGE="binance" 时需要）
# ============================================================
# 请到币安官网 https://www.binance.com/ 创建 API Key
# 需要开通合约交易权限和允许期货交易
# 合约 API 文档: https://binance-docs.github.io/apidocs/futures/en/
BINANCE_LIVE_CONFIG = {
    "api_key": "i4eLqg2l9wqqnwLRyjPDED50nHdkVVdfks0L4wbdyjdZsyXmRKGhAQbKtk507H6C",              # 你的 Binance API Key
    "api_secret": "cBbzcHq0Vsgsx4tTujXYyG6V981s173gthZS1O9waAMz8S0Gd3sz9ntAxuPzvXBw",        # 你的 Binance Secret Key
    "base_url": "https://fapi.binance.com",         # 永续合约 API 地址
    # 合约交易对格式: 大写无分隔符，如 BTCUSDT、ETHUSDT
    # 下单方向: BUY / SELL
    # 持仓方向: BOTH（单向持仓模式）
    # 订单类型: MARKET / LIMIT / STOP_MARKET / TAKE_PROFIT_MARKET
    # ⚠️ 重要: 请务必填写以上 api_key 和 api_secret，否则无法连接！
}


# ============================================================
# 回测时间范围（近 90 天）
# ============================================================
BACKTEST_START = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
BACKTEST_END = datetime.now().strftime("%Y-%m-%d")

# ============================================================
# 交易币种（主流前 20 大，排除稳定币，可自由增删）
# ============================================================
# 注意: Hotcoin 上的交易对与 Binance/OKX 可能略有不同
# 已自动适配 Hotcoin 的可用币种，缺失的币种会自动跳过
TRADING_SYMBOLS = [
    "BTC/USDT", "ETH/USDT",
]

# ============================================================
# 时间级别
# ============================================================
TIMEFRAMES = {
    "HTF": "15m",        # 主图：市场结构 + 日内 VP
    "LTF": "5m",         # 进场级别：微观 CHOCH
}

# ============================================================
# SMC 参数
# ============================================================
SMC_CONFIG = {
    "bos_lookback": 20,          # BOS 回看窗口（HTF 根数）
    "ob_formation_bars": 3,      # 订单块形成确认根数
    "min_ob_size_bps": 5,        # 最小订单块大小（基点）
    "fvg_min_gap_bps": 3,        # 最小 FVG 缺口（基点）
    "sweep_tolerance_bps": 2,    # 流动性掠夺穿透容忍度（基点）
    "chooch_confirmation_bars": 2,  # CHOCH 确认根数
    "liquidity_lookback": 50,    # 流动性池回看窗口
}

# ============================================================
# Volume Profile 参数
# ============================================================
VP_CONFIG = {
    "num_bins": 24,              # VP 价格区间分桶数
    "value_area_pct": 0.70,      # 价值区占比 70%
    "hvn_threshold": 1.5,        # HVN 阈值（平均值的倍数）
}

# ============================================================
# 交易管理参数
# ============================================================
TRADING_CONFIG = {
    "initial_capital": 10000.0,   # 初始资金（USDT，回测用）
    "position_size_pct": 0.02,    # 每笔 2% 动态仓位
    "max_risk_per_trade": 0.03,   # 每笔最大风险 3%（策略止损基于sweep低点，非固定1%）
    "default_sl_pct": 0.02,       # 加载持仓时默认止损距离（2%，兜底用，ATR不可用时回退到此值）
    "rr_long": 2.0,               # 做多兜底盈亏比（策略优先用VAH/BSL，兜底用此值）
    "rr_short": 2.0,              # 做空兜底盈亏比（策略优先用VAL/SSL，兜底用此值）
    "max_concurrent_trades": 2,   # 最大同时持仓数
    "tp1_ratio": 0.5,             # TP1 为目标距离的 50%（兜底用）
    "tp2_ratio": 1.0,             # TP2 为完整目标距离（兜底用）
    "tp1_size_pct": 0.5,          # TP1 平仓 50% 仓位，让 TP2 也能执行
    "leverage": 150,               # 合约杠杆倍数（止盈=收益率/杠杆，如 40%/150=0.267% 价格涨幅）
    "commission": 0.0005,         # 手续费 0.05%（合约）
    "slippage": 0.0003,           # 滑点 0.03%
    # ============================================================
    # ATR 自适应止损参数（方案二）
    # ============================================================
    # ATR（平均真实波幅）根据市场波动率自动调整止损距离：
    # - 波动大时 → SL 自动放宽，避免被插针打掉
    # - 波动小时 → SL 自动收紧，控制风险
    # ============================================================
    "atr_period": 14,             # ATR 计算周期（14根5m K线）
    "atr_sl_multiplier": 3.0,     # ATR 止损倍数（3倍ATR，让ATR在大波动时真正生效）
    "atr_sl_min_bps": 130,        # 最小止损缓冲（基点，1%，对齐旧代码1%标准）手动加到1.3吧
    "atr_sl_max_bps": 300,        # 最大止损缓冲（基点，3%，大波动时放松）
}

# ============================================================
# 实盘专用参数（仅 TRADING_MODE="live" 时生效）
# ============================================================
LIVE_CONFIG = {
    "scan_interval_seconds": 60,           # 每 60 秒扫描一次市场
    "max_daily_trades": 200,                # 每日最大交易次数限制
    "max_daily_loss_usdt": 200.0,          # 每日最大亏损限额（USDT）
    "min_signal_confidence": 0.6,          # 最小信号置信度（低于此值不交易）
    "order_type": "limit",                 # 订单类型: "market" 市价 / "limit" 限价
    "slippage_tolerance_bps": 5,           # 限价单滑点容忍度（基点）
    "telegram_bot_token": "",              # Telegram 通知（可选）
    "telegram_chat_id": "",                # Telegram 通知（可选）
}

# ============================================================
# 过滤条件
# ============================================================
FILTERS = {
    "min_ob_volume_ratio": 1.2,          # OB 区域成交量 > 平均 1.2 倍
    "max_spread_bps": 10,                # 最大价差 10 基点
    "require_trend_alignment": True,      # 需要趋势一致
    "min_confluence_factors": 2,          # 最少共振因子数
}