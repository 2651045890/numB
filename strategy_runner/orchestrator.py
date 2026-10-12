#!/usr/bin/env python3
"""Discover strategies and run isolated Freqtrade backtests outside the framework."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import functools
import hashlib
import json
import math
import os
import pathlib
import queue
import re
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from leverage_adapter import LeverageAdapter, create_leverage_adapter, validate_leverage


ROOT = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
FRAMEWORK_DIR = PROJECT_ROOT / "freqtrade"
STRATEGY_USER_DATA = PROJECT_ROOT / "freqtrade-strategies" / "user_data"
STRATEGY_DIR = STRATEGY_USER_DATA / "strategies"
WORKSPACE_DIR = PROJECT_ROOT / "strategy_workspace"
DATA_DIR = WORKSPACE_DIR / "data" / "okx"
OUTPUTS_DIR = WORKSPACE_DIR / "outputs"
RUNS_DIR = OUTPUTS_DIR / "runs"
# Freqtrade wants a `--userdir` for its own scratch (backtest archives, log dirs,
# the skeleton of empty folders it lays down). It sits under `runs/` so that every
# artifact one of our runs produces stays under `strategy_workspace/outputs/runs`.
# Per-pair results are NOT here: `run_one` passes `--backtest-directory` per pair,
# so each pair's output lands in its own folder inside the run directory.
USER_DATA_DIR = RUNS_DIR / "_user_data"

# The ports' shared machinery (pine_engine, pine_port_base, pine_ta, sm_*) sits
# at the ports root, while Freqtrade's resolver puts only the strategy file's OWN
# folder on sys.path -- PathModifier in freqtrade/resolvers/iresolver.py inserts
# `module_path.parent` and nothing else. A port filed under
# `source_ports/batch_007/` is therefore unable to import a sibling module at the
# root, and fails with "this class does not exist". The root goes on PYTHONPATH
# for every Freqtrade subprocess so the import resolves wherever a port is filed.
SHARED_PORT_DIR = STRATEGY_DIR / "futures" / "source_ports"
SETTINGS_PATH = ROOT / "settings.json"
RESULTS_XLSX_NAME = "backtest_results.xlsx"

XLSX_COLUMN_LABELS = {
    "backtest_days": "回测天数",
    "backtest_end": "回测结束时间",
    "backtest_start": "回测开始时间",
    "cagr": "年化复合收益率",
    "calmar": "卡玛比率",
    "can_short": "是否允许做空",
    "chunked": "是否分批回测",
    "chunks": "分片数量",
    "composite_score": "综合得分",
    "draws": "持平交易数",
    "duration_avg": "平均持仓时长",
    "duration_seconds": "耗时（秒）",
    "eligibility_reason": "未入选原因",
    "eligible": "是否入选",
    "error": "错误信息",
    "expectancy": "期望收益",
    "expectancy_ratio": "期望收益比",
    "file": "策略文件",
    "final_balance": "最终余额",
    "key": "结果标识",
    "leverage": "杠杆倍数",
    "lookahead_flag": "未来函数风险标记",
    "losses": "亏损交易数",
    "market_change": "市场涨跌幅",
    "max_drawdown_abs": "最大回撤金额",
    "max_drawdown_account": "账户最大回撤率",
    "mode": "策略模式",
    "name": "策略名称",
    "p_value": "P值",
    "pair": "币种",
    "pair_backtest_end": "币种回测结束时间",
    "pair_backtest_start": "币种回测开始时间",
    "pair_count": "币种数量",
    "pair_jobs": "币种并发数",
    "pairs_attempted": "已回测币种数",
    "pairs_failed": "失败币种数",
    "pairs_resolved": "币种已解析",
    "pairs_skipped": "未启动币种数",
    "pairs_succeeded": "成功币种数",
    "pairs_timed_out": "超时币种数",
    "profit_factor": "盈亏比",
    "profit_mean": "平均单笔收益率",
    "profit_mean_pct": "平均单笔收益率（%）",
    "profit_total": "总收益率",
    "profit_total_abs": "总收益金额",
    "profit_total_pct": "总收益率（%）",
    "rank": "排名",
    "run_directory": "运行目录",
    "score_calmar": "卡玛得分",
    "score_drawdown": "回撤得分",
    "score_profit_total": "总收益得分",
    "score_sharpe": "夏普得分",
    "score_sortino": "索提诺得分",
    "sharpe": "夏普比率",
    "sortino": "索提诺比率",
    "sqn": "系统质量指数",
    "starting_balance": "初始余额",
    "status": "运行状态",
    "strict_filter": "严格筛选结果",
    "strict_filter_reason": "严格筛选未通过原因",
    "strategy_timeframe": "实际K线周期",
    "threshold_relaxed": "已放宽交易数门槛",
    "timeframe": "策略声明K线周期",
    "timerange": "回测时间范围",
    "total_trades": "总交易数",
    "trades": "交易次数（原始字段）",
    "trades_per_day": "日均交易数",
    "trading_mode": "结果交易模式",
    "winrate": "胜率",
    "wins": "盈利交易数",
}


@dataclass(frozen=True)
class StrategySpec:
    name: str
    file: str
    timeframe: str
    mode: str
    can_short: bool
    lookahead_flag: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_settings() -> dict[str, Any]:
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))


def verify_framework_unchanged() -> str:
    clean = subprocess.run(["git", "-C", str(PROJECT_ROOT), "diff", "--quiet", "HEAD", "--", "freqtrade"]).returncode == 0
    if not clean:
        raise RuntimeError("freqtrade tracked source has working-tree changes; refusing to run")
    return subprocess.check_output(["git", "-C", str(PROJECT_ROOT), "rev-parse", "HEAD:freqtrade"], text=True).strip()


def literal_assignment(node: ast.ClassDef, name: str, default: Any) -> Any:
    for item in node.body:
        if isinstance(item, ast.Assign):
            targets, value = list(item.targets), item.value
        elif isinstance(item, ast.AnnAssign):
            targets, value = [item.target], item.value
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            try:
                return ast.literal_eval(value)
            except (ValueError, TypeError):
                return default
    return default


def is_strategy_class(node: ast.ClassDef) -> bool:
    return any(
        (isinstance(base, ast.Name) and base.id == "IStrategy")
        or (isinstance(base, ast.Attribute) and base.attr == "IStrategy")
        for base in node.bases
    )


def discover_strategies() -> list[StrategySpec]:
    found: list[StrategySpec] = []
    strategy_roots = (("futures", STRATEGY_DIR / "futures"), ("spot", STRATEGY_DIR / "spot"))
    for mode, strategy_root in strategy_roots:
        for path in sorted(strategy_root.rglob("*.py")):
            relative = path.relative_to(STRATEGY_DIR)
            try:
                source = path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=str(path))
            except SyntaxError:
                continue
            for node in tree.body:
                if not isinstance(node, ast.ClassDef) or not is_strategy_class(node):
                    continue
                timeframe = str(literal_assignment(node, "timeframe", "5m"))
                can_short = bool(literal_assignment(node, "can_short", False))
                if mode == "spot" and can_short:
                    raise ValueError(
                        f"现货策略不能启用做空：{relative.as_posix()} ({node.name})"
                    )
                found.append(
                    StrategySpec(
                        name=node.name,
                        file=relative.as_posix(),
                        timeframe=timeframe,
                        mode=mode,
                        can_short=can_short,
                        lookahead_flag="lookahead_bias" in {part.lower() for part in relative.parts},
                    )
                )
    return found


def write_inventory(specs: list[StrategySpec], destination: pathlib.Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": utc_now(),
        "strategy_root": str(STRATEGY_DIR),
        "count": len(specs),
        "strategies": [asdict(spec) for spec in specs],
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def freqtrade_command(settings: dict[str, Any]) -> list[str]:
    configured = os.environ.get("FREQTRADE_BIN") or str(settings.get("freqtrade_bin") or "freqtrade")
    candidate = pathlib.Path(configured).expanduser()
    if candidate.is_absolute() or candidate.parent != pathlib.Path("."):
        executable = candidate if candidate.is_absolute() else (PROJECT_ROOT / candidate).resolve()
        if executable.is_file():
            return [str(executable)]
    python_dir = pathlib.Path(sys.executable).resolve().parent
    environment_candidates = (
        python_dir / "freqtrade",
        python_dir / "freqtrade.exe",
        python_dir / "Scripts" / "freqtrade.exe",
    )
    for executable in environment_candidates:
        if executable.is_file():
            return [str(executable)]
    discovered = shutil.which(configured) or (shutil.which("freqtrade") if configured != "freqtrade" else None)
    if discovered:
        return [discovered]
    raise FileNotFoundError(
        f"Freqtrade executable not found: {configured!r}. Activate the Conda environment "
        "or set FREQTRADE_BIN to the full executable path."
    )


def subprocess_env(settings: dict[str, Any]) -> dict[str, str]:
    env = dict(**os.environ)
    inherited = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        [str(SHARED_PORT_DIR), *([inherited] if inherited else [])]
    )
    proxy = resolve_proxy(settings)
    proxy_keys = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")
    if not proxy:
        for key in proxy_keys:
            env.pop(key, None)
        return env
    for key in proxy_keys:
        env[key] = proxy
    return env


def log_proxy_settings(settings: dict[str, Any]) -> None:
    print(f"[环境] 代理={resolve_proxy(settings) or '已禁用'}", flush=True)
    if _PROXY_NOTE:
        print(f"[环境] {_PROXY_NOTE}", flush=True)


# WSL2 gives the distro its own network namespace: `127.0.0.1` inside WSL is WSL
# itself, NOT the Windows host where the desktop proxy (Clash/mihomo/…) listens.
# A settings.json shared with macOS therefore cannot hardcode either address, so
# an unreachable loopback proxy is swapped for the Windows host address that WSL
# itself keeps in its default route. Non-loopback values are never touched, and
# nothing here runs outside WSL.
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1", "[::1]", "0.0.0.0"}
PROXY_PROBE_TIMEOUT = 0.6
_PROXY_NOTE = ""


@functools.lru_cache(maxsize=1)
def running_under_wsl() -> bool:
    """True inside a WSL2 distro — env marker first, kernel release string second."""
    if os.environ.get("WSL_DISTRO_NAME") or os.environ.get("WSL_INTEROP"):
        return True
    try:
        release = pathlib.Path("/proc/sys/kernel/osrelease").read_text(encoding="utf-8")
    except OSError:
        return False
    return "microsoft" in release.lower() or "wsl" in release.lower()


@functools.lru_cache(maxsize=1)
def wsl_windows_host_ip() -> str:
    """The Windows host's IPv4 as seen from inside WSL2.

    `/proc/net/route` carries the default route (destination 00000000) with the
    gateway as little-endian hex, which is what `ip route show default` prints —
    read directly so the answer needs no `ip` binary.
    """
    try:
        lines = pathlib.Path("/proc/net/route").read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    for line in lines[1:]:
        fields = line.split()
        if len(fields) < 3 or fields[1] != "00000000" or len(fields[2]) != 8:
            continue
        octets = [int(fields[2][i : i + 2], 16) for i in (6, 4, 2, 0)]
        if any(part == 0 for part in octets):
            continue
        return ".".join(str(part) for part in octets)
    return ""


@functools.lru_cache(maxsize=8)
def proxy_is_reachable(host: str, port: int) -> bool:
    """One TCP connect attempt, cached: `subprocess_env` calls this per child process."""
    try:
        with socket.create_connection((host, port), timeout=PROXY_PROBE_TIMEOUT):
            return True
    except OSError:
        return False


def relocate_wsl_loopback_proxy(proxy: str) -> tuple[str, str]:
    """Return (proxy, note). Rewrites a dead loopback proxy to the Windows host."""
    if not proxy or not running_under_wsl():
        return proxy, ""
    parsed = urllib.parse.urlsplit(proxy)
    host = parsed.hostname or ""
    if host not in LOOPBACK_HOSTS:
        return proxy, ""
    try:
        port = parsed.port
    except ValueError:
        return proxy, ""
    if port is None or proxy_is_reachable(host, port):
        return proxy, ""
    # Mirrored WSL networking shares Windows' localhost, so reaching here means
    # NAT mode (or a proxy that simply is not running yet).
    windows_ip = wsl_windows_host_ip()
    if windows_ip and proxy_is_reachable(windows_ip, port):
        moved = urllib.parse.urlunsplit(
            (parsed.scheme, f"{windows_ip}:{port}", parsed.path, parsed.query, parsed.fragment)
        )
        return moved, (
            f"WSL：{host}:{port} 在 WSL 内是 WSL 自己，不是 Windows，"
            f"已自动改用 Windows 主机地址 {windows_ip}:{port}"
        )
    return proxy, (
        f"WSL：{host}:{port} 上没有代理，Windows 主机地址也连不上。"
        f"请在 Windows 的代理客户端里打开「允许局域网连接」（Allow LAN），"
        f"或设 STRATEGY_RUNNER_PROXY 指向真正可用的代理"
    )


def resolve_proxy(settings: dict[str, Any]) -> str:
    """Return the single proxy used by both Freqtrade and CCXT."""
    global _PROXY_NOTE
    override = os.environ.get("STRATEGY_RUNNER_PROXY")
    configured = settings.get("proxy") if isinstance(settings, dict) else None
    # Accept the old object shape temporarily so existing local settings keep working.
    if isinstance(configured, dict):
        configured = configured.get("https") or configured.get("http")
    proxy = str(override if override is not None else configured or "").strip()
    resolved, _PROXY_NOTE = relocate_wsl_loopback_proxy(proxy)
    return resolved


def describe_pairs(config: dict[str, Any]) -> str:
    pairs = extract_whitelist(config)
    return ", ".join(pairs) if pairs else "(empty)"


def data_directory_stats(directory: pathlib.Path) -> tuple[int, int, float | None]:
    """Return file count, byte size and newest modification time."""
    count = 0
    size = 0
    newest: float | None = None
    if not directory.exists():
        return count, size, newest
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        count += 1
        size += stat.st_size
        newest = stat.st_mtime if newest is None else max(newest, stat.st_mtime)
    return count, size, newest


def human_size(byte_count: int) -> str:
    value = float(byte_count)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TiB"


def timeframe_seconds(timeframe: str) -> int | None:
    match = re.fullmatch(r"(\d+)([mhdw])", timeframe)
    if not match:
        return None
    value = int(match.group(1))
    multiplier = {"m": 60, "h": 3600, "d": 86400, "w": 604800}[match.group(2)]
    return value * multiplier


def parse_data_filename(path: pathlib.Path, data_dir: pathlib.Path) -> tuple[str, str] | None:
    """Return mode and timeframe for primary OHLCV files (not mark/funding data)."""
    relative = path.relative_to(data_dir)
    mode = "futures" if relative.parts[0] == "futures" else "spot"
    suffix = r"-futures\.feather" if mode == "futures" else r"\.feather"
    match = re.search(rf"-(\d+[mhdw]){suffix}$", path.name)
    if not match:
        return None
    return mode, match.group(1)


def audit_data_coverage(data_dir: pathlib.Path, requested_start: str, mode: str | None = None) -> dict[str, Any]:
    """Inspect candle boundaries and internal timestamp gaps without loading price columns."""
    try:
        import numpy as np
        import pyarrow as pa
        import pyarrow.ipc as ipc
    except ImportError as exc:
        print(f"[audit] skipped: {exc}", flush=True)
        return {"files": [], "summary": {"skipped": str(exc)}}

    desired_start = datetime.strptime(requested_start[:8], "%Y%m%d").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    rows: list[dict[str, Any]] = []
    for path in sorted(data_dir.rglob("*.feather")):
        parsed = parse_data_filename(path, data_dir)
        if parsed is None:
            continue
        file_mode, timeframe = parsed
        if mode is not None and file_mode != mode:
            continue
        step = timeframe_seconds(timeframe)
        if step is None:
            continue
        try:
            with pa.memory_map(str(path), "r") as source:
                reader = ipc.open_file(source)
                date_chunks = [reader.get_batch(index).column("date") for index in range(reader.num_record_batches)]
                dates = pa.chunked_array(date_chunks).combine_chunks()
            if len(dates) == 0:
                raise ValueError("empty date column")
            start = dates[0].as_py()
            end = dates[-1].as_py()
            timestamps = dates.to_numpy(zero_copy_only=False).astype("datetime64[ms]").astype(np.int64)
            differences = np.diff(timestamps)
            expected_ms = step * 1000
            gap_mask = differences > expected_ms * 1.5
            gap_count = int(np.count_nonzero(gap_mask))
            missing_candles = int(np.maximum(differences[gap_mask] // expected_ms - 1, 0).sum()) if gap_count else 0
            leading = start > desired_start
            stale = end < now - timedelta(seconds=step * 2)
            rows.append(
                {
                    "file": str(path.relative_to(data_dir)),
                    "mode": file_mode,
                    "timeframe": timeframe,
                    "rows": len(dates),
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                    "starts_after_requested": leading,
                    "latest_lag_seconds": max(0, int((now - end).total_seconds())),
                    "stale_tail": stale,
                    "internal_gap_count": gap_count,
                    "estimated_missing_candles": missing_candles,
                }
            )
        except Exception as exc:
            rows.append({"file": str(path.relative_to(data_dir)), "mode": file_mode, "timeframe": timeframe, "error": str(exc)})
    summary = {
        "audited_at": utc_now(),
        "requested_start": desired_start.isoformat(),
        "files": len(rows),
        "read_errors": sum("error" in row for row in rows),
        "starts_after_requested": sum(bool(row.get("starts_after_requested")) for row in rows),
        "stale_tails": sum(bool(row.get("stale_tail")) for row in rows),
        "files_with_internal_gaps": sum(int(row.get("internal_gap_count") or 0) > 0 for row in rows),
    }
    payload = {"summary": summary, "files": rows}
    report = data_dir / f"data_coverage_{mode or 'all'}.json"
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"[audit] mode={mode or 'all'} files={summary['files']}, "
        f"starts_after_requested={summary['starts_after_requested']}, "
        f"stale_tails={summary['stale_tails']}, "
        f"internal_gaps={summary['files_with_internal_gaps']}, report={report}",
        flush=True,
    )
    return payload


def run_download_with_live_output(command: list[str], settings: dict[str, Any], data_dir: pathlib.Path) -> tuple[int, list[str]]:
    """Stream download events without repeating idle progress messages."""
    # Use the configured Freqtrade environment without modifying its installed package.
    # The active environment already imports Freqtrade and is portable across
    # Unix's python and Windows' python.exe/Scripts layout.
    command = [sys.executable, str(ROOT / "download_checked.py"), *command[1:]]
    process = subprocess.Popen(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=subprocess_env(settings),
        bufsize=1,
    )
    output_queue: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            output_queue.put(line.rstrip())
        output_queue.put(None)

    reader = threading.Thread(target=read_output, daemon=True)
    reader.start()
    lines: list[str] = []
    stream_closed = False
    while not stream_closed or process.poll() is None:
        try:
            line = output_queue.get(timeout=1)
            if line is None:
                stream_closed = True
            elif line:
                lines.append(line)
                print(f"[freqtrade] {line}", flush=True)
        except queue.Empty:
            pass
    reader.join(timeout=1)
    return process.wait(), lines


def config_path_for_mode(mode: str) -> pathlib.Path:
    return ROOT / "configs" / f"{mode}.json"


def local_pair_count(mode: str, timeframe: str) -> int:
    """Estimate the number of locally available pairs for a strategy timeframe."""
    directory = DATA_DIR / "futures" if mode == "futures" else DATA_DIR
    suffix = f"-{timeframe}-futures.feather" if mode == "futures" else f"-{timeframe}.feather"
    return sum(path.name.endswith(suffix) for path in directory.glob("*.feather"))


def strategy_needs_market_pricing(spec: StrategySpec) -> bool:
    """Whether a strategy places market orders and therefore needs price_side=other.

    The Pine source ports inherit `order_types` with market entries; Freqtrade
    refuses to start those under the repository's `price_side: "same"` and says
    so explicitly. Strategies that keep Freqtrade's default limit orders are
    left on the existing config so their results do not move.
    """
    return "source_ports" in pathlib.PurePosixPath(spec.file).parts


def port_source_settings(spec: StrategySpec) -> dict[str, Any] | None:
    """Read a Pine port's declared source settings straight from its AST.

    Returns None for any strategy that is not a source port. The values are the
    ORIGINAL strategy's (`initial_capital`, sizing), which the generated config
    has to mirror -- Freqtrade's own wallet and stake defaults are not a
    substitute for the source's and would change every position size.
    """
    path = STRATEGY_DIR / spec.file
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:
        return None
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or node.name != spec.name:
            continue
        if not any(isinstance(b, ast.Name) and b.id == "PinePortBase" for b in node.bases):
            return None
        return {
            "initial_capital": literal_assignment(node, "source_initial_capital", None),
            "qty_type": literal_assignment(node, "source_qty_type", "fixed"),
            "qty_value": literal_assignment(node, "source_qty_value", 1.0),
            "commission_percent": literal_assignment(
                node, "source_commission_percent", 0.0
            ),
        }
    return None


def prepare_runtime_config(
    mode: str,
    settings: dict[str, Any],
    pair_whitelist: list[str] | None = None,
    suffix: str = "",
    market_pricing: bool = False,
    source_wallet: float | None = None,
    source_fee: float | None = None,
    directory: pathlib.Path | None = None,
) -> pathlib.Path:
    """Create a generated Freqtrade config with the shared proxy injected.

    `directory` defaults to the shared `runtime_configs/`. Per-pair configs pass
    the run's own directory instead: the default path is keyed only on
    (mode, suffix), so two strategies running concurrently would write the same
    file and one would silently backtest with the other's wallet and fee.
    """
    source = config_path_for_mode(mode)
    config = json.loads(source.read_text(encoding="utf-8"))
    if market_pricing:
        # Freqtrade's documented pairing: market orders require price_side "other".
        config.setdefault("entry_pricing", {})["price_side"] = "other"
        config.setdefault("exit_pricing", {})["price_side"] = "other"
        # The ports size every entry themselves (custom_stake_amount), so the
        # fixed 100 USDT stake would either cap or reject their notional.
        config["stake_amount"] = "unlimited"
    if source_wallet:
        # Reproduce the source's own bankroll instead of Freqtrade's default,
        # which percent_of_equity sizing depends on directly.
        config["dry_run_wallet"] = float(source_wallet)
        # Freqtrade keeps 1% of the wallet back and refuses any stake above
        # `tradable_balance_ratio * wallet`. The source has no such reserve --
        # Pine will commit 100% of equity -- so a `percent_of_equity = 100`
        # source has EVERY entry vetoed here, silently, and the backtest
        # reports zero trades rather than a sizing mismatch. The engine is the
        # authority on what the source commits, so the framework's reserve
        # must not be able to overrule it.
        config["tradable_balance_ratio"] = 1.0
    if source_fee is not None:
        # Reproduce the source's OWN commission instead of letting Freqtrade
        # resolve the exchange's taker fee from market metadata. A TradingView
        # source that declares 0% (or 0.1%) has that cost baked into the equity
        # curve it reports; substituting the venue's real fee would silently
        # restate every port's return on a basis the source never used.
        config["fee"] = float(source_fee)
        config.pop("fee_open", None)
        config.pop("fee_close", None)
    proxy = resolve_proxy(settings)
    exchange = config.setdefault("exchange", {})
    if pair_whitelist:
        exchange["pair_whitelist"] = pair_whitelist
    ccxt_config = exchange.setdefault("ccxt_config", {})
    ccxt_config.pop("proxies", None)
    async_config = exchange.setdefault("ccxt_async_config", {})
    async_config.pop("aiohttp_proxy", None)
    if proxy:
        ccxt_config["proxies"] = {"http": proxy, "https": proxy}
        async_config["aiohttp_proxy"] = proxy
    destination = (directory or (USER_DATA_DIR / "runtime_configs")) / f"{mode}{suffix}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination


def extract_whitelist(config: dict[str, Any]) -> list[str]:
    exchange = config.get("exchange") or {}
    pairs = exchange.get("pair_whitelist") or []
    return [str(pair) for pair in pairs if str(pair).strip()]


def extract_blacklist(config: dict[str, Any]) -> list[str]:
    exchange = config.get("exchange") or {}
    pairs = exchange.get("pair_blacklist") or []
    return [str(pair) for pair in pairs if str(pair).strip()]


def local_pair_names(mode: str, timeframe: str) -> list[str]:
    """List the pairs that actually have local candles for this mode/timeframe.

    Freqtrade expands the whitelist regex against exchange markets; we expand it
    against local candle files instead, so the chunking matches the data that a
    backtest will really load.
    """
    directory = DATA_DIR / "futures" if mode == "futures" else DATA_DIR
    suffix = f"-{timeframe}-futures.feather" if mode == "futures" else f"-{timeframe}.feather"
    names: list[str] = []
    for path in directory.glob("*.feather"):
        if not path.name.endswith(suffix):
            continue
        stem = path.name[: -len(suffix)]
        parts = stem.split("_")
        if len(parts) >= 3:
            names.append(f"{parts[0]}/{parts[1]}:{parts[2]}")
        elif len(parts) == 2:
            names.append(f"{parts[0]}/{parts[1]}")
    return sorted(set(names))


def resolve_pairs(mode: str, timeframe: str, whitelist: list[str], blacklist: list[str]) -> list[str] | None:
    """Expand whitelist regexes against local candles; None when nothing resolves."""
    available = local_pair_names(mode, timeframe)
    if not available:
        return None
    matched = [pair for pair in available if any(re.fullmatch(p, pair, re.IGNORECASE) for p in whitelist)]
    if blacklist:
        matched = [pair for pair in matched if not any(re.fullmatch(p, pair, re.IGNORECASE) for p in blacklist)]
    return matched or None


def slug_token(text: Any) -> str:
    """Same slug rule the leverage adapter uses, so directory names look alike."""
    return re.sub(r"\W+", "_", str(text))


def pair_slugs(pairs: list[str]) -> dict[str, str]:
    """Map each pair to a unique directory name.

    `BTC/USDT:USDT` -> `BTC_USDT_USDT`. The slug rule is lossy (`A-B/USDT:USDT`
    and `A_B/USDT:USDT` both collapse to `A_B_USDT_USDT`) and macOS compares
    paths case-insensitively, so distinct pairs that collide get a short digest
    appended. Without this, two pairs would share one directory and one
    `backtest.log`, which is the exact thing per-pair logs exist to prevent.
    """
    slugs: dict[str, str] = {}
    owners: dict[str, str] = {}
    for pair in pairs:
        slug = slug_token(pair)
        existing = owners.get(slug)
        if existing is not None and existing != pair:
            slug = f"{slug}_{hashlib.sha1(pair.encode('utf-8')).hexdigest()[:6]}"
            print(f"[警告] 币种目录名冲突：{existing} 与 {pair} 都被转成 {slug_token(existing)}，后者改用 {slug}", flush=True)
        owners.setdefault(slug, pair)
        slugs[pair] = slug
    return slugs


FAILED_DIR_PREFIX = "00_error_"


def mark_failed_dir(pair_dir: pathlib.Path) -> pathlib.Path:
    """Rename a failed pair's directory to `00_error_<slug>`.

    One run writes 400+ pair directories that look alike; the failed ones are
    exactly the ones worth finding later, and mtime alone does not separate them.
    The prefix both makes them a single glob away (`ls -d 00_error_*`) and puts
    them at the TOP of the listing: `0` sorts before every letter, and the second
    `0` beats the pair slugs that themselves start with a digit (`0G_USDT_USDT`,
    `1000SATS_USDT_USDT`) — a bare `error_` or `_error_` prefix would sort them
    last instead. Returns the directory the pair's files live in afterwards.
    """
    if not pair_dir.exists() or pair_dir.name.startswith(FAILED_DIR_PREFIX):
        # 币种 slug 来自交易对符号，不会自己以 00_error_ 开头，所以这个前缀只可能
        # 是本函数加的。重复报告同一个币种时不至于叠成 00_error_00_error_xxx。
        return pair_dir
    target = pair_dir.parent / f"{FAILED_DIR_PREFIX}{pair_dir.name}"
    if target.exists():
        # run_dir 每次都是新建的，正常撞不上；真撞上说明这个目录被人手工动过，
        # 这时既不覆盖也不合并（合并会把两批文件混成一个），保留原名并报出来。
        print(f"[警告] 失败目录未改名：{target} 已存在，保留 {pair_dir.name}", flush=True)
        return pair_dir
    pair_dir.rename(target)
    return target


def describe_failure(returncode: int | None, stdout: str) -> str:
    """Explain why a backtest failed instead of quoting the last log line."""
    if returncode is None:
        return "回测超时（超过 --backtest-timeout）"
    if returncode < 0:
        try:
            name = signal.Signals(-returncode).name
        except ValueError:
            name = str(-returncode)
        hint = "，疑似内存不足被系统杀死" if -returncode == int(signal.SIGKILL) else ""
        return f"进程被信号 {name} 杀死{hint}"
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    return lines[-1][:500] if lines else f"退出码 {returncode}"


def run_backtest_command(
    command: list[str], settings: dict[str, Any], timeout: int, log_path: pathlib.Path,
) -> tuple[int | None, str]:
    """Write child output live to disk. None returncode means timeout."""
    env = subprocess_env(settings)
    env["PYTHONUNBUFFERED"] = "1"
    with log_path.open("w", encoding="utf-8") as log:
        try:
            process = subprocess.run(
                command, stdout=log, stderr=subprocess.STDOUT,
                env=env, timeout=timeout or None,
            )
            returncode = process.returncode
        except subprocess.TimeoutExpired:
            returncode = None
    return returncode, log_path.read_text(encoding="utf-8", errors="replace")


def combine_chunk_results(raws: list[dict[str, Any]]) -> dict[str, Any]:
    """Pool trade lists from several independently-run pair processes.

    Ratios that describe an equity curve (sharpe/sortino/calmar/cagr/drawdown)
    are NOT additive across separate runs and are deliberately left unset here
    rather than faked. Per-pair rows carry their own valid copies; strategy-level
    ranking reads the pair dimension instead.

    `profit_total_abs` sums each run's absolute PnL, but every run starts from a
    FULL wallet, so the sum is "what each pair made on its own bankroll", not the
    return of one portfolio holding all of them. Wallet sizes are therefore
    reported as unknown instead of being borrowed from an arbitrary first run.
    """
    trades = [trade for raw in raws for trade in (raw.get("trades") or [])]
    pair_results = [item for raw in raws for item in (raw.get("results_per_pair") or [])]
    total = len(trades)
    wins = sum(1 for trade in trades if float(trade.get("profit_ratio") or 0) > 0)
    losses = sum(1 for trade in trades if float(trade.get("profit_ratio") or 0) < 0)
    profit_abs = sum(float(trade.get("profit_abs") or 0) for trade in trades)
    starts = sorted(str(raw["backtest_start"]) for raw in raws if raw.get("backtest_start"))
    ends = sorted(str(raw["backtest_end"]) for raw in raws if raw.get("backtest_end"))
    return {
        "trades": trades,
        "results_per_pair": pair_results,
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "draws": total - wins - losses,
        "winrate": (wins / total) if total else None,
        "profit_total_abs": profit_abs,
        "profit_mean": (profit_abs / total) if total else None,
        "profit_total": None,
        "profit_factor": None,
        "sharpe": None,
        "sortino": None,
        "calmar": None,
        "sqn": None,
        "cagr": None,
        "max_drawdown_account": None,
        "max_drawdown_abs": None,
        "final_balance": None,
        "starting_balance": None,
        "backtest_start": starts[0] if starts else None,
        "backtest_end": ends[-1] if ends else None,
        "strategy_timeframe": raws[0].get("timeframe") if raws else None,
        "trading_mode": raws[0].get("trading_mode") if raws else None,
    }


def refresh_market_data(
    settings: dict[str, Any],
    specs: list[StrategySpec],
    timeranges: list[str],
    config_paths: dict[str, pathlib.Path],
) -> None:
    by_mode: dict[str, set[str]] = {}
    for spec in specs:
        by_mode.setdefault(spec.mode, set()).add(spec.timeframe)
    if not by_mode:
        return
    print(f"[数据] 刷新目标：{', '.join(f'{mode}({','.join(sorted(timeframes))})' for mode, timeframes in sorted(by_mode.items()))}", flush=True)
    for mode, timeframes in sorted(by_mode.items()):
        # 必须读 command_run 传进来的运行时配置（config_paths，已含 --pair 覆盖），
        # 不能读基础配置 configs/<mode>.json —— 后者的白名单是 .*/USDT:USDT，
        # 会让 --pair 完全管不住下载，指定 3 个币也会去拉全市场 463 个。
        config = json.loads(config_paths[mode].read_text(encoding="utf-8"))
        pairs = extract_whitelist(config)
        if not pairs:
            continue
        print(f"[数据] 市场={mode} 币种={describe_pairs(config)}", flush=True)
        print(f"[数据] 市场={mode} K线周期={', '.join(sorted(timeframes))}", flush=True)
        explicit_ranges = [item for item in timeranges if item.lower() != "auto"]
        timerange = explicit_ranges[-1] if explicit_ranges else str(settings.get("data_timerange") or "20170101-")
        command = freqtrade_command(settings) + [
            "download-data",
            "--config", str(config_paths[mode]),
            "--userdir", str(USER_DATA_DIR),
            "--datadir", str(DATA_DIR),
            "--trading-mode", mode,
            "--timerange", timerange,
        ]
        command.extend(["--pairs", *pairs])
        command.extend(["--timeframes", *sorted(timeframes)])
        data_dir = DATA_DIR
        before_count, before_size, _ = data_directory_stats(data_dir)
        print("[数据进度] 执行顺序：整体检查 → 缺失数据首次下载 → 已有数据增量更新", flush=True)
        returncode, output_lines = run_download_with_live_output(command, settings, data_dir)
        if returncode != 0:
            raise RuntimeError(
                f"data refresh failed for {mode}: {output_lines[-1] if output_lines else 'unknown error'}"
            )
        after_count, after_size, _ = data_directory_stats(data_dir)
        audit_data_coverage(data_dir, timerange, mode=mode)
        print(
            f"[数据] 市场={mode} 下载完成：文件数={after_count} "
            f"({after_count - before_count:+d})，总大小={human_size(after_size)} "
            f"(新增 {human_size(max(0, after_size - before_size))})",
            flush=True,
        )


def find_result(directory: pathlib.Path, strategy_name: str) -> dict[str, Any] | None:
    for archive in sorted(directory.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
        with zipfile.ZipFile(archive) as handle:
            names = [name for name in handle.namelist() if name.endswith(".json") and not name.endswith(".meta.json") and not name.endswith("_config.json")]
            for name in names:
                payload = json.loads(handle.read(name))
                if strategy_name in payload.get("strategy", {}):
                    return payload["strategy"][strategy_name]
    for path in sorted(directory.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if strategy_name in payload.get("strategy", {}):
            return payload["strategy"][strategy_name]
    return None


def numeric(value: Any) -> float | int | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return value
    return None


# Which Freqtrade result fields reach the xlsx, for BOTH strategy and pair rows.
# Every name here must also exist in XLSX_COLUMN_LABELS, and anything absent from
# this list never leaves the raw JSON -- that is what keeps unvetted Freqtrade
# keys (and their unlabeled columns) out of the report.
METRIC_KEYS = (
    "total_trades", "wins", "draws", "losses", "winrate", "profit_total",
    "profit_total_abs", "profit_mean", "profit_factor", "expectancy",
    "expectancy_ratio", "sharpe", "sortino", "calmar", "sqn", "cagr",
    "max_drawdown_account", "max_drawdown_abs", "trades_per_day",
    "market_change", "backtest_days", "final_balance", "starting_balance",
    "p_value",
)


def normalize_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    result = {key: numeric(raw.get(key)) for key in METRIC_KEYS}
    result.update({
        "backtest_start": raw.get("backtest_start"),
        "backtest_end": raw.get("backtest_end"),
        "strategy_timeframe": raw.get("timeframe"),
        "trading_mode": raw.get("trading_mode"),
    })
    return result


TRADE_SUMMARY_MARKER = "[回测交易统计]"


def write_trade_summary(log_path: pathlib.Path, metrics: dict[str, Any]) -> None:
    """Keep the most useful trade counts visible at the end of each pair log."""
    summary = (
        f"{TRADE_SUMMARY_MARKER} "
        f"总交易次数={int(metrics.get('total_trades') or 0)} "
        f"盈利次数={int(metrics.get('wins') or 0)} "
        f"亏损次数={int(metrics.get('losses') or 0)} "
        f"持平次数={int(metrics.get('draws') or 0)}\n"
    )
    existing = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
    lines = [line for line in existing.splitlines() if not line.startswith(TRADE_SUMMARY_MARKER)]
    body = "\n".join(lines).rstrip()
    log_path.write_text(f"{body}\n\n{summary}" if body else summary, encoding="utf-8")


def backtest_command(
    settings: dict[str, Any],
    config: pathlib.Path,
    adapter: LeverageAdapter,
    spec: StrategySpec,
    timerange: str | None,
    destination: pathlib.Path,
) -> list[str]:
    """Build one freqtrade backtesting invocation.

    Shared by the per-pair path and the no-local-candles fallback so the two
    cannot drift apart.
    """
    command = freqtrade_command(settings) + [
        "backtesting",
        "--config", str(config),
        "--userdir", str(USER_DATA_DIR),
        "--datadir", str(DATA_DIR),
        "--strategy-path", str(adapter.strategy_path),
        "--strategy", adapter.strategy_name,
        "--timeframe", spec.timeframe,
        "--cache", "none",
        "--export", "trades",
        "--backtest-directory", str(destination),
    ]
    if timerange:
        command.extend(["--timerange", timerange])
    return command


def pair_rows_for(strategy_row: dict[str, Any], entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Turn per-pair outcomes into report rows, one row per pair, always.

    A pair that failed still gets a row (`status == "failed"`), so a failure is
    visible in the ranking sheet instead of silently shrinking the table.
    """
    rows: list[dict[str, Any]] = []
    for entry in entries:
        pair = entry["pair"]
        row: dict[str, Any] = {
            "pair": pair,
            "name": strategy_row.get("name"),
            "file": strategy_row.get("file"),
            "mode": strategy_row.get("mode"),
            "timeframe": strategy_row.get("timeframe"),
            "timerange": strategy_row.get("timerange"),
            "leverage": strategy_row.get("leverage"),
            "run_directory": strategy_row.get("run_directory"),
            # 未来函数风险是策略级属性，币种自身没有这一列
            "lookahead_flag": strategy_row.get("lookahead_flag"),
            "error": entry.get("error") or "",
        }
        raw = entry.get("result")
        if raw is None:
            row["status"] = "failed"
        else:
            row.update(normalize_metrics(raw))
            # 能解析到该币种的 Freqtrade 结果，就说明这个币种已成功完成。
            # 不能继承 strategy_row.status：生成币种行时策略总状态尚未从
            # 初始化的 failed 更新为 success，会把所有成功币种误判成失败。
            row["status"] = "success"
        rows.append(row)
    return rows


def run_one(
    spec: StrategySpec,
    timerange: str,
    run_dir: pathlib.Path,
    settings: dict[str, Any],
    adapter: LeverageAdapter,
    leverage: float,
    config_path: pathlib.Path,
    pair_jobs: int = 4,
    timeout: int = 0,
    timerange_segment: str = "",
) -> dict[str, Any]:
    """Backtest one strategy over one timerange, one process per pair.

    Freqtrade writes a single log per process and offers no way to split it by
    pair, so a faithful per-pair log requires a per-pair process. Each pair gets
    its own directory, its own generated config (whitelisted to that one pair,
    so the process cannot backtest anything else) and its own `backtest.log`.
    """
    started = time.monotonic()
    strategy_dir = run_dir / spec.mode / spec.name
    if timerange_segment:
        strategy_dir = strategy_dir / timerange_segment
    strategy_dir.mkdir(parents=True, exist_ok=True)
    effective_timerange = None if timerange.lower() == "auto" else timerange
    available_pairs = local_pair_count(spec.mode, spec.timeframe)
    mode_label = {"spot": "现货", "futures": "合约"}.get(spec.mode, spec.mode)
    print(
        f"[开始] 策略={spec.name} 市场={mode_label} K线周期={spec.timeframe} "
        f"回测时间={effective_timerange or '本地全部历史'} 本地币种数={available_pairs}",
        flush=True,
    )
    base_config = json.loads(config_path.read_text(encoding="utf-8"))
    resolved = resolve_pairs(
        spec.mode,
        spec.timeframe,
        extract_whitelist(base_config),
        extract_blacklist(base_config),
    )
    market_pricing = strategy_needs_market_pricing(spec)
    market_suffix = "_market" if market_pricing else ""
    port_settings = port_source_settings(spec) if market_pricing else None
    source_wallet = (port_settings or {}).get("initial_capital")
    commission_percent = (port_settings or {}).get("commission_percent")
    source_fee = None if commission_percent is None else float(commission_percent) / 100.0
    pairs = list(resolved or [])
    slugs = pair_slugs(pairs)
    row: dict[str, Any] = {
        **asdict(spec),
        "timerange": timerange,
        "status": "failed",
        "error": "",
        "run_directory": str(strategy_dir.relative_to(PROJECT_ROOT)),
        "leverage": leverage,
        "pairs_resolved": resolved is not None,
        "pair_count": len(pairs),
        # 三个数相加恒等于 pair_count：已回测 + 未启动 = 币种总数，
        # 成功 + 失败 = 已回测。哪条路径返回都不能让它们对不上账。
        "pairs_attempted": 0,
        "pairs_succeeded": 0,
        "pairs_failed": 0,
        "pairs_skipped": 0,
        "pair_jobs": max(1, int(pair_jobs)),
    }

    def finalize() -> dict[str, Any]:
        row["duration_seconds"] = round(time.monotonic() - started, 2)
        return row

    if not pairs:
        # 白名单在当前周期没有任何本地K线：沿用整表单进程回测，明确指出拿不到每币种日志
        print(
            f"[警告] 策略={spec.name} 在 K线周期={spec.timeframe} 下解析不到任何本地币种，"
            f"退回整表单进程回测；本次将只有一份合并日志，没有每币种日志",
            flush=True,
        )
        fallback_config = prepare_runtime_config(
            spec.mode, settings, extract_whitelist(base_config),
            suffix=f"_{spec.name}_fallback{market_suffix}_{slug_token(timerange)}",
            market_pricing=market_pricing,
            source_wallet=source_wallet,
            source_fee=source_fee,
            directory=run_dir / "configs",
        )
        command = backtest_command(
            settings, fallback_config, adapter, spec, effective_timerange, strategy_dir
        )
        returncode, stdout = run_backtest_command(command, settings, timeout, strategy_dir / "backtest.log")
        if returncode != 0:
            row["error"] = describe_failure(returncode, stdout)
            return finalize()
        raw = find_result(strategy_dir, adapter.strategy_name)
        if raw is None:
            row["error"] = "Freqtrade 正常退出但未找到结果 JSON"
            return finalize()
        write_trade_summary(strategy_dir / "backtest.log", raw)
        row["status"] = "success"
        row["pairs_resolved"] = False
        row["pair_count"] = 0
        row["pairs_succeeded"] = 0
        row["pairs_failed"] = 0
        row.update(normalize_metrics(raw))
        return finalize()

    def backtest_pair(pair: str) -> dict[str, Any]:
        """Run one pair in its own process with a live log."""
        slug = slugs[pair]
        pair_dir = strategy_dir / slug
        pair_dir.mkdir(parents=True, exist_ok=True)
        pair_config = prepare_runtime_config(
            spec.mode, settings, [pair],
            suffix=f"_{spec.name}_{slug}{market_suffix}_{slug_token(timerange)}",
            market_pricing=market_pricing,
            source_wallet=source_wallet,
            source_fee=source_fee,
            directory=run_dir / "configs",
        )
        command = backtest_command(
            settings, pair_config, adapter, spec, effective_timerange, pair_dir
        )
        print(
            f"[币种开始] 策略={spec.name} 币种={pair} 时间={timerange} 日志={pair_dir / 'backtest.log'}",
            flush=True,
        )
        returncode, stdout = run_backtest_command(command, settings, timeout, pair_dir / "backtest.log")
        if returncode != 0:
            return {
                "pair": pair,
                "result": None,
                "error": describe_failure(returncode, stdout),
                "timed_out": returncode is None,
            }
        raw = find_result(pair_dir, adapter.strategy_name)
        if raw is None:
            return {"pair": pair, "result": None, "error": "Freqtrade 正常退出但未找到结果 JSON"}
        write_trade_summary(pair_dir / "backtest.log", raw)
        return {"pair": pair, "result": raw, "error": ""}

    workers = max(1, int(pair_jobs))
    # 一个坏掉的策略会让每个币种都以同样的方式失败。今天第一个失败就整体中止；
    # 逐币种隔离后改成"前 N 个全失败才中止"，N = 并发数，既保住这个代价上限，
    # 又不会因为个别币种数据有问题而放弃整个策略。
    abort_after = max(1, min(len(pairs), workers))
    outcomes: dict[str, dict[str, Any]] = {}
    aborted = ""
    completed = 0
    succeeded = 0

    def report_pair(pair: str) -> None:
        outcome = outcomes[pair]
        successes = sum(entry["result"] is not None for entry in outcomes.values())
        failed = outcome["result"] is None
        log_dir = strategy_dir / slugs[pair]
        # 失败目录改名放在这里，而不是 backtest_pair 里：超时、非零退出、找不到
        # 结果 JSON、orchestrator 自己抛异常，四条失败路径最后都在这里汇合，
        # 分散改的话迟早漏掉一条。未启动的币种没有目录，也就不改名。
        if failed and not outcome.get("skipped"):
            log_dir = mark_failed_dir(log_dir)
        status = "失败" if failed else "成功"
        error = f" 原因={outcome['error']}" if outcome.get("error") else ""
        # 失败行带上最终日志路径：`[币种开始]` 那行打印的是改名前的路径，改名后
        # 直接复制它是打不开的。
        where = f" 日志={log_dir / 'backtest.log'}" if failed and log_dir.is_dir() else ""
        print(
            f"[币种完成] 策略={spec.name} 币种={pair} 时间={timerange} 状态={status} "
            f"进度={len(outcomes)}/{len(pairs)} 成功={successes} 失败={len(outcomes) - successes}{error}{where}",
            flush=True,
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(backtest_pair, pair): pair for pair in pairs}
        for future in concurrent.futures.as_completed(futures):
            pair = futures[future]
            try:
                outcomes[pair] = future.result()
            except Exception as exc:
                outcomes[pair] = {"pair": pair, "result": None, "error": f"orchestrator error: {exc}"}
            completed += 1
            report_pair(pair)
            if outcomes[pair]["result"] is not None:
                succeeded += 1
            elif succeeded == 0 and completed >= abort_after:
                aborted = f"前 {completed} 个币种全部回测失败，已中止该策略"
                for pending in futures:
                    pending.cancel()
                # 已经起来的 worker 停不下来，`with` 退出时本来也要等它们跑完；
                # 顺手把结果收回来，否则那几个真跑过的币种会被算成"未启动"，
                # 「已回测 N 个 / 失败 M 个 / 未启动 K 个」就对不上账。
                # cancel() 只对还没被取走的生效，所以"没被取消"== "正在跑或已经跑完"，
                # 这两种都要收。别再加 `and not f.done()`：那会漏掉恰好在 break 和
                # 这一行之间跑完的 future，它的结果就永久丢了。
                # 注意 CancelledError 继承 BaseException 而非 Exception，接不住，
                # 所以先滤掉已取消的，别让它冒到 as_completed 里。
                running = [f for f in futures if not f.cancelled()]
                for finished in concurrent.futures.as_completed(running):
                    pair = futures[finished]
                    if pair in outcomes:
                        continue
                    try:
                        outcomes[pair] = finished.result()
                    except Exception as exc:
                        outcomes[pair] = {"pair": pair, "result": None, "error": f"orchestrator error: {exc}"}
                    report_pair(pair)
                break
    skipped = 0
    for pair in pairs:
        if pair not in outcomes:
            # "进程根本没起来"和"起来了但回测失败"是两回事：前者没有日志、没有
            # 指标。混成一个数的话，一次网络故障会被记成"447 个币种全部回测失败"。
            outcomes[pair] = {"pair": pair, "result": None, "error": aborted or "未运行", "skipped": True}
            skipped += 1
    # 按 pairs 原顺序回填，保证 raws / _pair_rows / xlsx 行序不随并发度变化
    ordered = [outcomes[pair] for pair in pairs]
    attempted = [entry for entry in ordered if not entry.get("skipped")]
    raws = [entry["result"] for entry in attempted if entry["result"] is not None]
    row["pair_count"] = len(pairs)
    row["pairs_attempted"] = len(attempted)
    row["pairs_succeeded"] = len(raws)
    row["pairs_failed"] = len(attempted) - len(raws)
    row["pairs_skipped"] = skipped
    # --backtest-timeout 是每个币种的预算，不是每个策略的：一个卡住的策略最坏会耗
    # timeout × ⌈币种数 ÷ pair_jobs⌉，所以超时要单独报出来，别让它藏在"失败"里。
    timed_out = sum(1 for entry in attempted if entry.get("timed_out"))
    row["pairs_timed_out"] = timed_out
    if skipped:
        print(f"[警告] 策略={spec.name} 有 {skipped} 个币种未启动：{aborted}", flush=True)
    if timed_out:
        print(
            f"[警告] 策略={spec.name} 有 {timed_out} 个币种超过单币种预算 {timeout} 秒被放弃，"
            f"该策略总耗时因此可能达到 {timeout}×⌈{len(pairs)}÷{workers}⌉",
            flush=True,
        )
    # 中止路径也要落币种行：跑过并失败的币种必须留在排名表里，否则一次中止之后
    # 只剩策略级一句"失败"，哪几个币种失败过、日志在哪都查不到。未启动的不进表
    # ——它们没有日志也没有指标，几百行"未运行"只会把主表淹掉，那个数走
    # `pairs_skipped` 列和上面那条警告。
    row["_pair_rows"] = pair_rows_for(row, attempted)
    if not raws:
        row["error"] = aborted or next((entry["error"] for entry in attempted if entry["error"]), "") or "未产生任何回测结果"
        return finalize()
    row["status"] = "success"
    # 单个币种进程本身就是完整回测，比率有效，直接沿用；多个币种才走池化并置 null。
    combined = raws[0] if len(raws) == 1 else combine_chunk_results(raws)
    row.update(normalize_metrics(combined))
    if len(raws) > 1:
        # 每个币种进程各跑一条独立资金曲线，其比率不可相加
        row["backtest_start"] = combined.get("backtest_start")
        row["backtest_end"] = combined.get("backtest_end")
    return finalize()


def collect_pair_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten the per-pair rows that `run_one` attached to each strategy row."""
    return [item for row in rows for item in (row.get("_pair_rows") or [])]


def write_json_atomic(path: pathlib.Path, payload: Any) -> None:
    """Write via a temp file + rename.

    `results.json` grows to thousands of pair rows and is rewritten after every
    task; a kill mid-write would leave unparseable JSON exactly when
    `summarize` is the recovery path that needs to read it.
    """
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def write_results(
    rows: list[dict[str, Any]],
    run_dir: pathlib.Path,
    settings: dict[str, Any],
    pair_rows: list[dict[str, Any]] | None = None,
) -> None:
    """Persist strategy rows plus one row per pair.

    `pair_rows=None` means "collect from the rows themselves" (the `run` path,
    where `run_one` already built them). Callers that only have already-persisted
    rows -- `merge` -- pass the rows through explicitly, because the pair rows
    were stripped from the strategy rows on the way to disk.

    严格筛选在这里落盘：三条命令（run/summarize/merge）都经过它，所以 `summarize`
    能把筛选结果补进已有运行，不用重跑回测。落盘前就地盖章，同一个字典对象随后
    还会被 `write_rankings` 读到，两张 xlsx 表因此不会和 results.json 说两套话。
    """
    resolved_pairs = pair_rows if pair_rows is not None else collect_pair_rows(rows)
    thresholds = strict_filter_thresholds(settings)
    apply_strict_filter(rows, thresholds)
    apply_strict_filter(resolved_pairs, thresholds)
    strategy_rows = [
        {key: value for key, value in row.items() if not str(key).startswith("_")}
        for row in rows
    ]
    payload = {
        "generated_at": utc_now(),
        "settings": settings,
        # 记下本次实际用的阈值：口径（尤其是账户百分比类指标）随钱包大小变化，
        # 事后读 JSON 的人得知道这一批「候选」是按哪组数判的。
        "strict_filter_thresholds": thresholds,
        "rows": strategy_rows,
        "pair_rows": [normalize_pair_row(item) for item in resolved_pairs],
    }
    write_json_atomic(run_dir / "results.json", payload)


PERCENTAGE_COLUMNS = {
    "cagr", "market_change", "max_drawdown_account", "profit_mean",
    "profit_total", "winrate",
}


def write_sheet(writer: Any, rows: list[dict[str, Any]], sheet_name: str) -> None:
    import pandas as pd
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    columns = sorted({key for row in rows for key in row})
    column_labels = [XLSX_COLUMN_LABELS[column] for column in columns]
    dataframe = pd.DataFrame(rows).reindex(columns=columns)
    dataframe.to_excel(writer, index=False, header=column_labels, sheet_name=sheet_name)
    worksheet = writer.sheets[sheet_name]
    worksheet.freeze_panes = "A2"
    worksheet.auto_filter.ref = worksheet.dimensions
    worksheet.sheet_view.showGridLines = False
    header_fill = PatternFill("solid", fgColor="1F4E78")
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = Font(color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center")
    worksheet.row_dimensions[1].height = 24
    for column_index, column_name in enumerate(columns, start=1):
        values = [XLSX_COLUMN_LABELS[column_name], *("" if value is None else str(value) for value in dataframe[column_name])]
        worksheet.column_dimensions[get_column_letter(column_index)].width = min(max(max(map(len, values)) + 2, 11), 32)
        if column_name in PERCENTAGE_COLUMNS and worksheet.max_row >= 2:
            for cell in worksheet.iter_cols(
                min_col=column_index,
                max_col=column_index,
                min_row=2,
                max_row=worksheet.max_row,
            ):
                for item in cell:
                    item.number_format = "0.00%"


def write_xlsx_report(
    run_dir: pathlib.Path,
    pair_rows: list[dict[str, Any]],
    strategy_rows: list[dict[str, Any]],
) -> pathlib.Path:
    """Write the pair ranking (main sheet) and the strategy overview."""
    import pandas as pd

    xlsx_path = run_dir / RESULTS_XLSX_NAME
    sheets = [("币种排名", pair_rows), ("策略汇总", strategy_rows)]
    # 标签校验对两张表的列取并集，在打开 writer 之前完成
    missing_labels = sorted({
        key
        for _, rows in sheets
        for row in rows
        for key in row
        if key not in XLSX_COLUMN_LABELS
    })
    if missing_labels:
        raise ValueError(f"XLSX 字段缺少中文名称：{', '.join(missing_labels)}")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for sheet_name, rows in sheets:
            write_sheet(writer, rows, sheet_name)
    return xlsx_path


def percentile(value: float, values: list[float], inverse: bool = False) -> float:
    if len(values) <= 1:
        return 1.0
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    rank = (below + 0.5 * max(0, equal - 1)) / (len(values) - 1)
    rank = max(0.0, min(1.0, rank))
    return 1.0 - rank if inverse else rank


METRIC_MAP = {
    "profit_total": ("profit_total", False),
    "sharpe": ("sharpe", False),
    "sortino": ("sortino", False),
    "calmar": ("calmar", False),
    "drawdown": ("max_drawdown_account", True),
}


def score_rows(
    rows: list[dict[str, Any]],
    settings: dict[str, Any],
    trades_field: str = "total_trades",
    minimum_trades: float | None = None,
    group_keys: tuple[str, ...] = ("mode", "timerange"),
    relax_when_empty: bool = False,
) -> list[dict[str, Any]]:
    """Score rows by percentile within their peer group.

    Percentiles are only meaningful against comparable rows, so `group_keys`
    must separate populations that differ structurally. For pairs that means
    `timeframe` as well: a 1m strategy's pairs trade hundreds of times and a 1d
    strategy's trade a handful, so pooling them ranks trading frequency rather
    than edge.

    `relax_when_empty` retries a group that produced zero eligible rows with the
    trade floor dropped to 1, and stamps every row it admits that way with
    `threshold_relaxed` -- so a thin sheet stays possible without becoming
    silently dishonest.
    """
    threshold = int(settings["minimum_trades"] if minimum_trades is None else minimum_trades)
    weights = settings["scoring_weights"]
    scored = [dict(row) for row in rows]

    def group_of(row: dict[str, Any]) -> tuple[Any, ...]:
        return tuple(row.get(key) for key in group_keys)

    def mark(members: list[dict[str, Any]], floor: int, relaxed: bool) -> None:
        for row in members:
            reasons: list[str] = []
            # 缺失 status 不等于失败：旧版 pair_rows 根本不写这个字段，按失败处理会把
            # 整张历史币种表判成 0 入选。只有明确不是 success 才算失败。
            if row.get("status") not in (None, "success"):
                reasons.append("backtest_failed")
            if (row.get(trades_field) or 0) < floor:
                reasons.append("insufficient_trades")
            if row.get("lookahead_flag"):
                reasons.append("lookahead_bias_flag")
            admitted = not reasons
            row["eligible"] = admitted
            row["threshold_relaxed"] = bool(relaxed and admitted)
            reason = ",".join(reasons)
            # admitted 意味着 reasons 为空，所以这里只会是这条门槛说明本身
            row["eligibility_reason"] = "已放宽交易数门槛" if (relaxed and admitted) else reason
            row["composite_score"] = None
            row.pop("rank", None)
            for label in METRIC_MAP:
                row.pop(f"score_{label}", None)

    def score_group(candidates: list[dict[str, Any]]) -> None:
        if not candidates:
            return
        distributions = {
            label: [float(row[field]) for row in candidates if numeric(row.get(field)) is not None]
            for label, (field, _) in METRIC_MAP.items()
        }
        for row in candidates:
            total = 0.0
            used_weight = 0.0
            for label, (field, inverse) in METRIC_MAP.items():
                value = numeric(row.get(field))
                values = distributions[label]
                if value is None or not values:
                    continue
                component = percentile(float(value), values, inverse=inverse)
                row[f"score_{label}"] = round(component * 100, 4)
                weight = float(weights[label])
                total += component * weight
                used_weight += weight
            row["composite_score"] = round(100 * total / used_weight, 4) if used_weight else None
        ranked = sorted(candidates, key=lambda row: float(row.get("composite_score") or -1), reverse=True)
        for position, row in enumerate(ranked, start=1):
            row["rank"] = position

    for group in sorted({group_of(row) for row in scored}, key=lambda item: tuple(str(part) for part in item)):
        members = [row for row in scored if group_of(row) == group]
        mark(members, threshold, False)
        eligible = [row for row in members if row["eligible"]]
        if not eligible and relax_when_empty:
            mark(members, 1, True)
            eligible = [row for row in members if row["eligible"]]
        score_group(eligible)
    return scored


# 严格筛选（“核心池”）的阈值，与 settings.json 的 `strict_filter` 块一一对应。
# settings 里没有这个块时整体回退到这里的默认值；块里少写几个键也只回退到对应的
# 默认值。阈值口径与 xlsx 那几列一致：比例是小数不是百分数，0.10 表示 10%。
DEFAULT_STRICT_FILTER: dict[str, float] = {
    "min_total_trades": 200,
    "min_cagr": 0.10,
    "min_profit_total_abs": 0.0,
    "max_max_drawdown_account": 0.10,
    "min_sharpe": 1.5,
    "min_sortino": 2.0,
    "min_calmar": 1.5,
    "min_winrate": 0.35,
    "min_profit_factor": 2.0,
    "min_expectancy": 0.0,
    "min_profit_mean": 0.0,
    "max_p_value": 0.05,
}

# 每条门槛：(阈值键, 指标字段, 比较符, 未通过原因)。
# `min_total_trades` 是 >=，其余下限一律严格大于、上限一律严格小于，与原始筛选口径一致。
STRICT_FILTER_RULES: tuple[tuple[str, str, str, str], ...] = (
    ("min_total_trades", "total_trades", ">=", "insufficient_trades"),
    ("min_cagr", "cagr", ">", "cagr_below_threshold"),
    ("min_profit_total_abs", "profit_total_abs", ">", "profit_total_abs_not_positive"),
    ("max_max_drawdown_account", "max_drawdown_account", "<", "max_drawdown_account_above_threshold"),
    ("min_sharpe", "sharpe", ">", "sharpe_below_threshold"),
    ("min_sortino", "sortino", ">", "sortino_below_threshold"),
    ("min_calmar", "calmar", ">", "calmar_below_threshold"),
    ("min_winrate", "winrate", ">", "winrate_below_threshold"),
    ("min_profit_factor", "profit_factor", ">", "profit_factor_below_threshold"),
    ("min_expectancy", "expectancy", ">", "expectancy_not_positive"),
    ("min_profit_mean", "profit_mean", ">", "profit_mean_not_positive"),
    ("max_p_value", "p_value", "<", "p_value_above_threshold"),
)

STRICT_FILTER_CANDIDATE = "候选"
STRICT_FILTER_REJECTED = "剔除"


def strict_filter_thresholds(settings: dict[str, Any]) -> dict[str, float]:
    """本次运行实际使用的严格筛选阈值，逐键合并 settings 的覆盖值。"""
    thresholds = dict(DEFAULT_STRICT_FILTER)
    for key, value in (settings.get("strict_filter") or {}).items():
        if key not in DEFAULT_STRICT_FILTER:
            raise ValueError(f"settings.json 的 strict_filter 里有未知键：{key}")
        thresholds[key] = float(value)
    return thresholds


def passes(value: float | int | None, operator: str, bound: float) -> bool:
    if value is None:
        return False
    if operator == ">=":
        return float(value) >= bound
    if operator == ">":
        return float(value) > bound
    return float(value) < bound


def apply_strict_filter(rows: list[dict[str, Any]], thresholds: dict[str, float]) -> None:
    """In place: stamp every row with `strict_filter` and why it was rejected.

    The thresholds are deliberately absolute rather than percentile-scored: the
    xlsx ranking answers "better than its peers", this answers "good in absolute
    terms, on the numbers a live decision would be made from". A missing metric
    fails the comparison -- the same thing pandas does with NaN, and the same
    reason a row whose backtest never produced stats cannot be a candidate.
    """
    for row in rows:
        reasons: list[str] = []
        # 与 score_rows 同一口径：缺失 status 不算失败，只有明确不是 success 才算。
        if row.get("status") not in (None, "success"):
            reasons.append("backtest_failed")
        if row.get("lookahead_flag"):
            reasons.append("lookahead_bias_flag")
        for key, field, operator, reason in STRICT_FILTER_RULES:
            if not passes(numeric(row.get(field)), operator, thresholds[key]):
                reasons.append(reason)
        row["strict_filter"] = STRICT_FILTER_REJECTED if reasons else STRICT_FILTER_CANDIDATE
        row["strict_filter_reason"] = ",".join(reasons)


def normalize_pair_row(row: dict[str, Any]) -> dict[str, Any]:
    """Give a pair row the names the rest of the pipeline reads.

    Rows written by the old chunked code spell things differently: the pair is
    `key` and the trade count is `trades`. Rows produced now are already in the
    canonical shape, so this is a no-op for them -- but `summarize` and `merge`
    also run over runs recorded before this change, and a missing bridge there
    silently reads zero trades for every pair.
    """
    cleaned = {key: value for key, value in row.items() if not str(key).startswith("_")}
    if not cleaned.get("pair"):
        cleaned["pair"] = cleaned.pop("key", None)
    elif "key" in cleaned:
        cleaned.pop("key")
    if cleaned.get("total_trades") is None and cleaned.get("trades") is not None:
        cleaned["total_trades"] = cleaned["trades"]
    # 2026-09-29 之前的逐币种实现会让已产生完整指标、且没有错误信息的币种
    # 继承策略行初始化时的 failed。兼容旧运行，使 summarize 能原地修复结果。
    if (
        cleaned.get("status") == "failed"
        and not cleaned.get("error")
        and cleaned.get("total_trades") is not None
        and cleaned.get("strategy_timeframe")
    ):
        cleaned["status"] = "success"
    return cleaned


def write_rankings(
    strategy_rows: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    run_dir: pathlib.Path,
    settings: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Score both dimensions and write the two-sheet report."""
    minimum_pairs = settings.get("minimum_trades_per_pair", 10)
    # `_`-prefixed keys are internal transport between run_one and write_results.
    # Dropping them here covers every caller, including the ones that hold the
    # in-memory rows where those keys are still attached.
    strategy_rows = [{k: v for k, v in row.items() if not str(k).startswith("_")} for row in strategy_rows]
    pair_rows = [normalize_pair_row(row) for row in pair_rows]
    ranked_strategy = score_rows(strategy_rows, settings)
    ranked_pairs = score_rows(
        pair_rows,
        settings,
        minimum_trades=minimum_pairs,
        group_keys=("mode", "timeframe", "timerange"),
        relax_when_empty=True,
    )
    ordered_pairs = sorted(
        ranked_pairs,
        key=lambda row: (
            not bool(row.get("eligible")),
            str(row.get("mode")),
            str(row.get("timeframe")),
            -(float(row.get("composite_score") or -1)),
            str(row.get("name")),
            str(row.get("pair")),
        ),
    )
    ordered_strategy = sorted(
        ranked_strategy,
        key=lambda row: (
            not bool(row.get("eligible")),
            str(row.get("mode")),
            -(float(row.get("composite_score") or -1)),
            str(row.get("name")),
            str(row.get("timerange")),
        ),
    )
    write_xlsx_report(run_dir, ordered_pairs, ordered_strategy)
    return ordered_strategy, ordered_pairs


def command_inventory(args: argparse.Namespace) -> int:
    """Scan strategies without importing them, and report what was found.

    Without `--output` this prints to stdout and writes nothing: the snapshot is
    pure derived data that nothing in the pipeline reads, so letting it default
    to a file just left a stale copy sitting in the repository. `run` still
    records its own filtered snapshot per run, which is the copy that answers
    "what did this run actually select".
    """
    verify_framework_unchanged()
    print("[inventory] scanning strategies...", flush=True)
    specs = discover_strategies()
    counts = {mode: sum(spec.mode == mode for spec in specs) for mode in ("spot", "futures")}
    if args.output:
        destination = pathlib.Path(args.output)
        write_inventory(specs, destination)
        print(f"[inventory] found {len(specs)} strategies -> spot={counts['spot']} futures={counts['futures']}", flush=True)
        print(json.dumps({"count": len(specs), "modes": counts, "output": str(destination)}, ensure_ascii=False))
        return 0
    print(f"[inventory] found {len(specs)} strategies -> spot={counts['spot']} futures={counts['futures']}", flush=True)
    print(json.dumps({
        "generated_at": utc_now(),
        "strategy_root": str(STRATEGY_DIR),
        "count": len(specs),
        "strategies": [asdict(spec) for spec in specs],
    }, ensure_ascii=False, indent=2))
    return 0


def select_modes(specs: list[StrategySpec], mode: str) -> list[StrategySpec]:
    """Select strategies whose market data and backtests were requested."""
    requested = {"spot", "futures"} if mode == "all" else {mode}
    return [spec for spec in specs if spec.mode in requested]


def command_run(args: argparse.Namespace) -> int:
    verify_framework_unchanged()
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings = load_settings()
    if args.proxy is not None:
        # The CLI is the most specific statement of intent, so it beats both the
        # environment override and the settings file. Writing to `settings` (not
        # just the environment) is what makes the value land in results.json,
        # where a later reader can tell which egress a run actually used.
        settings["proxy"] = args.proxy
        os.environ["STRATEGY_RUNNER_PROXY"] = args.proxy
    leverage = validate_leverage(args.leverage if args.leverage is not None else settings.get("leverage", 1.0))
    log_proxy_settings(settings)
    timeranges = args.timerange or list(settings["timeranges"])
    print("[运行] 正在扫描策略……", flush=True)
    specs = discover_strategies()
    specs = select_modes(specs, args.mode)
    if args.strategy:
        wanted = set(args.strategy)
        specs = [spec for spec in specs if spec.name in wanted]
    if args.path_prefix:
        prefixes = tuple(args.path_prefix)
        specs = [spec for spec in specs if spec.file.startswith(prefixes)]
    if args.limit:
        specs = specs[: args.limit]
    counts = {mode: sum(spec.mode == mode for spec in specs) for mode in ("spot", "futures")}
    config_paths = {
        mode: prepare_runtime_config(mode, settings, args.pair)
        for mode in counts if counts[mode]
    }
    configured_pairs = args.pair or ["全部 USDT 交易对"]
    print(
        f"[运行] 已选择 {len(specs)} 个策略：现货={counts['spot']}，"
        f"合约={counts['futures']}，币种={configured_pairs}，"
        f"回测时间={timeranges}，杠杆={leverage}x",
        flush=True,
    )
    if args.stage in {"data", "all"}:
        print("[运行] 正在刷新市场数据……", flush=True)
        refresh_market_data(settings, specs, timeranges, config_paths)
        print("[运行] 市场数据刷新完成", flush=True)
    else:
        print("[运行] 当前阶段=回测：使用现有本地数据，不执行下载", flush=True)
    if args.stage == "data":
        print("[运行] 数据阶段完成，未启动回测", flush=True)
        return 0
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    adapter_dir = run_dir / "leverage_adapters"
    # 按 (模式, 策略名) 索引：现货与合约出现同名类时不能串用适配器
    adapters = {
        (spec.mode, spec.name): create_leverage_adapter(
            spec.name,
            STRATEGY_DIR / spec.file,
            adapter_dir / f"{spec.mode}_{spec.name}",
            leverage,
        )
        for spec in specs
    }
    write_inventory(specs, run_dir / "inventory.json")
    print(f"[运行] 输出目录：{run_dir}", flush=True)
    work = [(spec, timerange) for timerange in timeranges for spec in specs]
    if len(timeranges) > 1:
        # 一个策略回测多个时间范围时，输出目录必须再分一层，否则两个范围会互相覆盖
        print(f"[警告] 指定了 {len(timeranges)} 个回测时间范围，输出目录会按时间范围再分一层", flush=True)
    pair_jobs = max(1, int(args.pair_jobs))
    jobs = max(1, int(args.jobs))
    rows: list[dict[str, Any]] = []
    print(
        f"[运行] 开始回测：共 {len(work)} 个任务；每个任务按币种拆成独立进程，"
        f"策略并发={jobs}，币种并发={pair_jobs}",
        flush=True,
    )
    if jobs * pair_jobs > 8:
        print(
            f"[警告] 同时运行的 freqtrade 进程数 = {jobs}×{pair_jobs} = {jobs * pair_jobs}，超过 8 个；"
            f"回测很吃内存，进程被系统杀死时请调小 --jobs 或 --pair-jobs",
            flush=True,
        )
    with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
        futures = {
            executor.submit(
                run_one,
                spec=spec,
                timerange=timerange,
                run_dir=run_dir,
                settings=settings,
                adapter=adapters[(spec.mode, spec.name)],
                leverage=leverage,
                config_path=config_paths[spec.mode],
                pair_jobs=pair_jobs,
                timeout=args.backtest_timeout,
                timerange_segment=slug_token(timerange) if len(timeranges) > 1 else "",
            ): (spec, timerange)
            for spec, timerange in work
        }
        for future in concurrent.futures.as_completed(futures):
            spec, timerange = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                row = {**asdict(spec), "timerange": timerange, "status": "failed", "error": f"orchestrator error: {exc}"}
            rows.append(row)
            pair_rows = row.get("_pair_rows") or []
            # 分母是"真起了进程的币种数"，不是 pair_rows 的行数：正常与中止路径下
            # 两者相等，但兜底路径（退回整表回测）没有币种行，用行数会把比例写成 0/0。
            # 用币种行里的 status 统计也不行——失败币种也在表里，且策略级异常时
            # 根本没有 _pair_rows，那行是 command_run 现拼的。
            succeeded = int(row.get("pairs_succeeded") or 0)
            attempted = row.get("pairs_attempted")
            if attempted is None:  # 历史 run 落下的行没有这个字段
                attempted = len(pair_rows)
            skipped = int(row.get("pairs_skipped") or 0)
            skipped_text = f"，另有 {skipped} 个未启动" if skipped else ""
            failed_pairs = [str(item.get("pair")) for item in pair_rows if item.get("status") != "success"]
            status_label = {"success": "成功", "failed": "失败"}.get(str(row["status"]), str(row["status"]))
            timerange_label = "自动（本地全部历史）" if timerange.lower() == "auto" else timerange
            more = "（退回整表回测，无每币种日志）" if not row.get("pairs_resolved", True) else ""
            print(
                f"[{len(rows)}/{len(work)}] {status_label}：策略={spec.name} "
                f"K线周期={spec.timeframe} 回测时间={timerange_label} "
                f"币种成功={succeeded}/{attempted}{skipped_text}{more} "
                f"实际数据范围={row.get('backtest_start') or '未知'} 至 {row.get('backtest_end') or '未知'}",
                flush=True,
            )
            if failed_pairs:
                shown = ", ".join(failed_pairs[:5]) + ("……" if len(failed_pairs) > 5 else "")
                print(f"  [失败币种] 策略={spec.name} 共 {len(failed_pairs)} 个：{shown}", flush=True)
            if args.verbose_pairs:
                for item in pair_rows:
                    profit = item.get("profit_total")
                    profit_text = f"{float(profit):.2%}" if isinstance(profit, (int, float)) else "未知"
                    print(
                        f"  [币种] 策略={spec.name} 币种={item.get('pair')} K线周期={spec.timeframe} "
                        f"回测时间={timerange_label} 交易次数={item.get('total_trades') or 0} "
                        f"收益率={profit_text} 状态={item.get('status')}",
                        flush=True,
                    )
            write_results(rows, run_dir, settings)
    rows.sort(key=lambda row: (str(row.get("mode")), str(row.get("name")), str(row.get("timerange"))))
    write_results(rows, run_dir, settings)
    ranked_strategy, ranked_pairs = write_rankings(rows, collect_pair_rows(rows), run_dir, settings)
    print(f"[运行] 全部完成。原始结果：{run_dir / 'results.json'}", flush=True)
    print(
        f"[运行] 汇总表：{run_dir / RESULTS_XLSX_NAME}"
        f"（币种排名 {len(ranked_pairs)} 行，策略汇总 {len(ranked_strategy)} 行）",
        flush=True,
    )
    print(
        f"[运行] 严格筛选候选：币种 "
        f"{sum(item.get('strict_filter') == STRICT_FILTER_CANDIDATE for item in ranked_pairs)}"
        f"/{len(ranked_pairs)}，策略 "
        f"{sum(item.get('strict_filter') == STRICT_FILTER_CANDIDATE for item in ranked_strategy)}"
        f"/{len(ranked_strategy)}",
        flush=True,
    )
    print(run_dir)
    return 0 if any(row.get("status") == "success" for row in rows) else 2


def command_summarize(args: argparse.Namespace) -> int:
    """Rebuild the xlsx and the rankings from a run's persisted results.json.

    Nothing is re-backtested. Pair rows are normalized and persisted so old
    status-format bugs are repaired in both results.json and the xlsx report.
    """
    run_dir = pathlib.Path(args.run_dir).resolve()
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    settings = payload.get("settings") or load_settings()
    rows = payload.get("rows") or []
    pair_rows = payload.get("pair_rows") or []
    if not rows:
        print(f"[汇总] {run_dir / 'results.json'} 里没有策略行，无法重建", flush=True)
        return 2
    pair_rows = [normalize_pair_row(row) for row in pair_rows]
    # Older runs already contain the counts in results.json, but their Freqtrade
    # logs only show them inside an English table. Add the same concise Chinese
    # summary used by new runs without re-running any backtests.
    pairs_by_run: dict[str, list[dict[str, Any]]] = {}
    for row in pair_rows:
        if row.get("status") == "success" and row.get("pair") and row.get("run_directory"):
            pairs_by_run.setdefault(str(row["run_directory"]), []).append(row)
    for relative_dir, members in pairs_by_run.items():
        slugs = pair_slugs([str(row["pair"]) for row in members])
        strategy_dir = PROJECT_ROOT / relative_dir
        for row in members:
            log_path = strategy_dir / slugs[str(row["pair"])] / "backtest.log"
            if log_path.exists():
                write_trade_summary(log_path, row)
    write_results(rows, run_dir, settings, pair_rows=pair_rows)
    ranked_strategy, ranked_pairs = write_rankings(rows, pair_rows, run_dir, settings)
    print(json.dumps({
        "策略行": len(ranked_strategy),
        "币种行": len(ranked_pairs),
        "入选策略": sum(bool(item.get("eligible")) for item in ranked_strategy),
        "入选币种": sum(bool(item.get("eligible")) for item in ranked_pairs),
        "严格筛选候选策略": sum(item.get("strict_filter") == STRICT_FILTER_CANDIDATE for item in ranked_strategy),
        "严格筛选候选币种": sum(item.get("strict_filter") == STRICT_FILTER_CANDIDATE for item in ranked_pairs),
        "xlsx": str(run_dir / RESULTS_XLSX_NAME),
    }, ensure_ascii=False))
    return 0


def command_merge(args: argparse.Namespace) -> int:
    """Merge runs, preferring a successful retry for each strategy.

    The chosen row's pair rows travel with it: `write_results` strips per-pair
    detail out of the strategy rows on the way to disk, so copying `rows` alone
    would produce a merged run with an empty 币种排名 sheet.
    """
    destination = RUNS_DIR / args.run_id
    destination.mkdir(parents=True, exist_ok=False)
    selected: dict[tuple[str, str, str], tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    settings = load_settings()
    for source_name in args.source:
        source = pathlib.Path(source_name).resolve()
        payload = json.loads((source / "results.json").read_text(encoding="utf-8"))
        settings = payload.get("settings") or settings
        pairs_by_key: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
        for item in payload.get("pair_rows") or []:
            key = (str(item.get("mode")), str(item.get("name")), str(item.get("timerange")))
            pairs_by_key.setdefault(key, []).append(item)
        for row in payload["rows"]:
            key = (str(row.get("mode")), str(row.get("name")), str(row.get("timerange")))
            current = selected.get(key)
            if current is None or (current[0].get("status") != "success" and row.get("status") == "success") or current[0].get("status") == row.get("status"):
                selected[key] = (row, pairs_by_key.get(key, []))
    order = sorted(selected, key=lambda key: (key[0], key[1], key[2]))
    rows = [selected[key][0] for key in order]
    pair_rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for key in order:
        for item in selected[key][1]:
            pair_key = (*key, str(item.get("pair") or item.get("key") or ""))
            if pair_key in seen:
                continue
            seen.add(pair_key)
            pair_rows.append(item)
    write_results(rows, destination, settings, pair_rows=pair_rows)
    ranked_strategy, ranked_pairs = write_rankings(rows, pair_rows, destination, settings)
    print(json.dumps({
        "策略行": len(ranked_strategy),
        "币种行": len(ranked_pairs),
        "output": str(destination),
    }, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="Discover strategy classes without importing them")
    inventory.add_argument("--output", help="Write the snapshot to this file. Without it, print to stdout.")
    inventory.set_defaults(func=command_inventory)
    run = commands.add_parser("run", help="Backtest strategies with one isolated freqtrade process per pair")
    run.add_argument(
        "--mode",
        choices=["spot", "futures", "all"],
        default="futures",
        help="Market to download/backtest: spot, futures, or both (all).",
    )
    run.add_argument("--timerange", action="append")
    run.add_argument(
        "--pair",
        action="append",
        help="Temporarily override pair_whitelist; repeat to select multiple pairs.",
    )
    run.add_argument("--strategy", action="append")
    run.add_argument("--path-prefix", action="append", help="Run strategy files below this relative directory prefix")
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--jobs", type=int, default=1, help="How many (strategy, timerange) tasks run at once.")
    run.add_argument(
        "--pair-jobs",
        type=int,
        default=4,
        help="How many pairs run at once within one strategy. One freqtrade process per pair.",
    )
    run.add_argument(
        "--verbose-pairs",
        action="store_true",
        help="Print one line per pair. Without it, only failures are listed.",
    )
    run.add_argument(
        "--backtest-timeout",
        type=int,
        default=7200,
        help="Seconds before a single pair's freqtrade backtest is abandoned (0 waits forever).",
    )
    run.add_argument("--leverage", type=float, help="Controlled futures leverage (1-100); capped by the exchange")
    run.add_argument(
        "--proxy",
        help=(
            "Proxy for this run only. Beats STRATEGY_RUNNER_PROXY and settings.json's proxy; "
            "pass an empty string to force a direct connection."
        ),
    )
    run.add_argument(
        "--stage",
        choices=["data", "backtest", "all"],
        default="all",
        help="Run only data refresh, only backtesting, or both (default: all)",
    )
    run.add_argument("--run-id")
    run.set_defaults(func=command_run)
    summarize = commands.add_parser("summarize", help="Rebuild rankings for an existing run")
    summarize.add_argument("run_dir")
    summarize.set_defaults(func=command_summarize)
    merge = commands.add_parser("merge", help="Merge runs, preferring a successful retry for each strategy")
    merge.add_argument("--run-id", required=True)
    merge.add_argument("source", nargs="+")
    merge.set_defaults(func=command_merge)
    return parser


if __name__ == "__main__":
    parser = build_parser()
    arguments = parser.parse_args()
    raise SystemExit(arguments.func(arguments))
