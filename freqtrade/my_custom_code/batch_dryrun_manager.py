#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ft_batch_dryrun.py
批量模拟盘管理器（Freqtrade）
- start/stop/status/restart
- 自动生成覆盖配置（端口/DB/名称/周期/交易对）
- 一进程=一策略=一个主timeframe

用法示例：
  python3 ft_batch_dryrun.py start
  python3 ft_batch_dryrun.py status
  python3 ft_batch_dryrun.py stop
  python3 ft_batch_dryrun.py start --write-base-config  # 若你还没有基准配置
  python3 ft_batch_dryrun.py start --exchange okx       # 想临时换交易所
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from shutil import which
import socket

# =============== 基本路径 ===============
ROOT = Path.cwd()
USER_DATA = ROOT / "user_data"
DRY_CFG_DIR = USER_DATA / "dryrun_configs"  # 具体配置文件夹
DRY_LOG_DIR = USER_DATA / "dryrun_logs"  # log日志必须
DRY_DB_DIR = USER_DATA / "dryrun_db"
DRY_RUN_DIR = USER_DATA / "dryrun_runtime"
BASE_CFG_PATH = ROOT / "config_base_dryrun.json"


# =============== 端口分配起始值 ===============
API_PORT_START = 8100
RPC_PORT_START = 11000

# =============== 计划清单（编辑这里即可批量启动） ===============
PLANS = [
    {"strategy": "MultiMa", "timeframe": "15m", "pairs": ["DOGE/USDT"]},
    {"strategy": "MultiMa", "timeframe": "30m", "pairs": ["DOGE/USDT"]},
    {"strategy": "MultiMa", "timeframe": "1h", "pairs": ["DOGE/USDT"]},
    {"strategy": "GodStra", "timeframe": "1m", "pairs": ["DOGE/USDT"]},
    {"strategy": "GodStra", "timeframe": "5m", "pairs": ["DOGE/USDT"]},
    {"strategy": "GodStra", "timeframe": "30m", "pairs": ["DOGE/USDT"]},
    {"strategy": "GodStra", "timeframe": "1h", "pairs": ["DOGE/USDT"]},
    {"strategy": "UniversalMACD", "timeframe": "1m", "pairs": ["DOGE/USDT"]},
]

# 从 .env 文件加载环境变量
from dotenv import load_dotenv
load_dotenv()  # 默认从当前工作目录加载 .env

key = os.environ["OKX_KEY"]
secret = os.environ["OKX_SECRET"]
password = os.environ["OKX_PASSWORD"]

# =============== 可选：一键写出基准配置的模板（你也可以用你现有的） ===============
BASE_CONFIG_TEMPLATE = {
    "$schema": "https://schema.freqtrade.io/schema.json",
    "bot_name": "freqtrade",
    "initial_state": "running",
    "dry_run": True,
    "dry_run_wallet": 1000,
    "trading_mode": "spot",
    "max_open_trades": 3,
    "stake_currency": "USDT",
    "stake_amount": "unlimited",
    "tradable_balance_ratio": 0.99,
    "fiat_display_currency": "USD",
    "cancel_open_orders_on_exit": False,
    "unfilledtimeout": {"entry": 10, "exit": 10, "exit_timeout_count": 0, "unit": "minutes"},
    "entry_pricing": {
        "price_side": "same",
        "use_order_book": True,
        "order_book_top": 1,
        "price_last_balance": 0.0,
        "check_depth_of_market": {"enabled": False, "bids_to_ask_delta": 1}
    },
    "exit_pricing": {"price_side": "same", "use_order_book": True, "order_book_top": 1},
    "exchange": {
        "name": "okx",
        "key": key,
        "secret": secret,
        "password": password,
        "sandbox": False,
        "ccxt_config": {
            "enableRateLimit": True,
            "options": {"defaultType": "spot"},
            "proxies": {"http": "http://127.0.0.1:7897", "https": "http://127.0.0.1:7897"}
        },
        "ccxt_async_config": {"aiohttp_proxy": "http://127.0.0.1:7897"},
        "pair_whitelist": ["DOGE/USDT"],
        "pair_blacklist": ["OKB/.*", "USDC/.*"]
    },
    "pairlists": [{"method": "StaticPairList"}],
    "telegram": {"enabled": False, "token": "", "chat_id": ""},
    "api_server": {
        "enabled": True,
        "listen_ip_address": "127.0.0.1",
        # "listen_port": 8881,  # 每实例覆盖
        "verbosity": "error",
        "enable_openapi": False,
        "jwt_secret_key": "somethingrandom",
        "CORS_origins": [],
        "username": "Freqtrader",
        "password": "SuperSecret1!",
        "ws_token": "sercet_Ws_t0ken"
    },
    "discord": {
    "enabled": True,
    "webhook_url": "https://discord.com/api/webhooks/1428041502281564220/Rf6wTMZ7zm-pREcvObfl-2et_m6P69DlbpfHlEhTfx2LTy4c1QZ67rGbKMkHg1VoToYo",
    "allow_custom_messages": True
    },
    "rpc": {
        "enabled": True,
        "listen_ip_address": "127.0.0.1",
        # "listen_port": 10001  # 每实例覆盖
    },
    "db_url": "sqlite:///user_data/dryrun_db/dryrun.sqlite",
    "internals": {"process_throttle_secs": 5}
}

# =============== 工具函数 ===============
def ensure_dirs():
    for d in (USER_DATA, DRY_CFG_DIR, DRY_LOG_DIR, DRY_DB_DIR, DRY_RUN_DIR):
        d.mkdir(parents=True, exist_ok=True)

def check_freqtrade_installed():
    if which("freqtrade") is None:
        print("[ERROR] 'freqtrade' 未找到。请先安装并确保命令可用（pipx/pip 或 Docker 中映射）。")
        sys.exit(1)

def load_base_config():
    if not BASE_CFG_PATH.exists():
        print(f"[ERROR] 找不到基准配置：{BASE_CFG_PATH}. 你可以用 --write-base-config 生成一份模板。")
        sys.exit(1)
    with open(BASE_CFG_PATH, "r") as f:
        return json.load(f)

def save_base_config_from_template(exchange_name=None, http_proxy=None):
    cfg = BASE_CONFIG_TEMPLATE.copy()
    if exchange_name:
        cfg["exchange"]["name"] = exchange_name
    if http_proxy:
        cfg["exchange"]["ccxt_config"].setdefault("proxies", {})
        cfg["exchange"]["ccxt_config"]["proxies"]["http"] = http_proxy
        cfg["exchange"]["ccxt_config"]["proxies"]["https"] = http_proxy
        cfg["exchange"]["ccxt_async_config"]["aiohttp_proxy"] = http_proxy

    with open(BASE_CFG_PATH, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    print(f"[OK] 已写出基准配置：{BASE_CFG_PATH}")

# =============== 端口冲突检测 ===============
def find_free_port(start_port):
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('127.0.0.1', port))
            if result != 0:  # 如果端口没有被占用
                return port
            port += 1  # 移动到下一个端口

def make_instance_name(strategy, timeframe, pairs):
    pairtag = "_".join(p.replace("/", "") for p in pairs)
    return f"{strategy}_{timeframe}_{pairtag}"

def write_override_config(name, timeframe, pairs, api_port, rpc_port):
    cfg = {
        "bot_name": f"dryrun-{name}",
        "timeframe": timeframe,
        "exchange": {"pair_whitelist": pairs},
        "api_server": {"listen_port": api_port},
        "rpc": {"listen_port": rpc_port},
        "db_url": f"sqlite:///{(DRY_DB_DIR / (name + '.sqlite')).as_posix()}"
    }
    path = DRY_CFG_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
    return path

def merge_base_and_override(base_template, name, timeframe, pairs, api_port, rpc_port):
    """
    合并基础模板和覆盖配置，生成最终配置。
    """
    # 复制基础配置模板
    config = base_template.copy()

    # 合并覆盖配置
    config["bot_name"] = f"dryrun-{name}"
    config["timeframe"] = timeframe
    config["exchange"]["pair_whitelist"] = pairs
    config["api_server"]["listen_port"] = api_port
    config["rpc"]["listen_port"] = rpc_port
    config["db_url"] = f"sqlite:///{(DRY_DB_DIR / (name + '.sqlite')).as_posix()}"
    
    return config


def save_merged_config(name, timeframe, pairs, api_port, rpc_port):
    # 合并基础配置和覆盖配置
    merged_config = merge_base_and_override(BASE_CONFIG_TEMPLATE, name, timeframe, pairs, api_port, rpc_port)
    
    # 保存合并后的配置到文件
    config_path = DRY_CFG_DIR / f"{name}_merged_config.json"
    with open(config_path, "w") as f:
        json.dump(merged_config, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] 合并后的配置已保存：{config_path}")
    return config_path


def launch_instance(strategy, name, timeframe, pairs, api_port, rpc_port):
    logfile = DRY_LOG_DIR / f"{name}.log"
    stdout = (DRY_RUN_DIR / f"{name}.stdout.log").open("ab")
    stderr = (DRY_RUN_DIR / f"{name}.stderr.log").open("ab")

    # 保存合并后的配置
    merged_config_path = save_merged_config(name, timeframe, pairs, api_port, rpc_port)

    cmd = [
        "freqtrade", "trade",
        "--dry-run",
        "--config", str(merged_config_path),  # 使用合并后的配置
        "--strategy", strategy,
        "--logfile", str(logfile)
    ]
    
    proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
    (DRY_RUN_DIR / f"{name}.pid").write_text(str(proc.pid))
    print(f"[STARTED] {name}  pid={proc.pid}")
    return proc.pid


def iter_pids():
    for pidfile in DRY_RUN_DIR.glob("*.pid"):
        try:
            pid = int(pidfile.read_text().strip())
            yield pidfile, pid
        except Exception:
            continue

def stop_all(timeout=10):
    pids = list(iter_pids())
    if not pids:
        print("[INFO] 没有正在运行的 dry-run 实例。")
        return

    for _, pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass

    t0 = time.time()
    while time.time() - t0 < timeout:
        alive = False
        for _, pid in pids:
            try:
                os.kill(pid, 0)
                alive = True
            except ProcessLookupError:
                pass
        if not alive:
            break
        time.sleep(0.5)

    for pidfile, pid in pids:
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            pidfile.unlink(missing_ok=True)
        except Exception:
            pass
        print(f"[STOPPED] pid={pid}")

def status():
    lines = []
    for pidfile, pid in iter_pids():
        alive = True
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            alive = False
        name = pidfile.stem
        lines.append(f"{name}: {'running' if alive else 'stopped'} (pid={pid})")
    if not lines:
        print("[INFO] 没有 dry-run 实例。")
    else:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] STATUS")
        for l in sorted(lines):
            print("  -", l)

# =============== CLI ===============
def main():
    parser = argparse.ArgumentParser(description="Freqtrade 批量模拟盘管理器")
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_start = sub.add_parser("start", help="启动所有计划中的实例")
    sub.add_parser("stop", help="停止所有实例")
    sub.add_parser("status", help="查看实例状态")
    sub.add_parser("restart", help="重启：先 stop 再 start")

    args = parser.parse_args()
    if args.cmd is None:
        args.cmd = "start"

    ensure_dirs()
    check_freqtrade_installed()

    if args.cmd == "start":
        # 启动实例时动态分配端口
        api_port = API_PORT_START
        rpc_port = RPC_PORT_START
        for plan in PLANS:
            api_port += 1
            rpc_port += 1
            name = make_instance_name(plan["strategy"], plan["timeframe"], plan["pairs"])
            launch_instance(plan["strategy"], name, plan["timeframe"], plan["pairs"], api_port, rpc_port)

        print("[OK] 全部实例已启动。你可以用 `python3 ft_batch_dryrun.py status` 查看。")

    elif args.cmd == "stop":
        stop_all()

    elif args.cmd == "status":
        status()

    elif args.cmd == "restart":
        stop_all()
        time.sleep(1)
        sys.argv = [sys.argv[0], "start"]
        main()

if __name__ == "__main__":
    main()
    

# python3 ft_batch_dryrun.py start --write-base-config
# python3 ft_batch_dryrun.py start
# python3 ft_batch_dryrun.py stop
# python3 ft_batch_dryrun.py status
# python3 ft_batch_dryrun.py restart

"""
  - GodStra_1h_DOGEUSDT: running (pid=54331)
  - GodStra_1m_DOGEUSDT: running (pid=54327)
  - GodStra_30m_DOGEUSDT: running (pid=54329)
  - GodStra_5m_DOGEUSDT: running (pid=54328)
  - MultiMa_15m_DOGEUSDT: running (pid=54324)
  - MultiMa_1h_DOGEUSDT: running (pid=54326)
  - MultiMa_30m_DOGEUSDT: running (pid=54325)
  - UniversalMACD_1m_DOGEUSDT: running (pid=54335)
"""