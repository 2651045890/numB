#!/usr/bin/env python3
"""Discover strategies and run isolated Freqtrade backtests outside the framework."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import csv
import hashlib
import json
import math
import os
import pathlib
import queue
import re
import shutil
import subprocess
import sys
import threading
import time
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
USER_DATA_DIR = OUTPUTS_DIR / "user_data"
RUNS_DIR = OUTPUTS_DIR / "runs"
SETTINGS_PATH = ROOT / "settings.json"
RESULTS_XLSX_NAME = "backtest_results.xlsx"

XLSX_COLUMN_LABELS = {
    "backtest_days": "回测天数",
    "backtest_end": "回测结束时间",
    "backtest_start": "回测开始时间",
    "cagr": "年化复合收益率",
    "calmar": "卡玛比率",
    "can_short": "是否允许做空",
    "composite_score": "综合得分",
    "draws": "持平交易数",
    "duration_seconds": "耗时（秒）",
    "eligibility_reason": "未入选原因",
    "eligible": "是否入选",
    "error": "错误信息",
    "expectancy": "期望收益",
    "expectancy_ratio": "期望收益比",
    "file": "策略文件",
    "final_balance": "最终余额",
    "leverage": "杠杆倍数",
    "lookahead_flag": "未来函数风险标记",
    "losses": "亏损交易数",
    "market_change": "市场涨跌幅",
    "max_drawdown_abs": "最大回撤金额",
    "max_drawdown_account": "账户最大回撤率",
    "mode": "策略模式",
    "name": "策略名称",
    "profit_factor": "盈亏比",
    "profit_mean": "平均单笔收益率",
    "profit_total": "总收益率",
    "profit_total_abs": "总收益金额",
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
    "strategy_timeframe": "结果策略周期",
    "timeframe": "配置策略周期",
    "timerange": "回测时间范围",
    "total_trades": "总交易数",
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
    spot_config = settings.get("proxy", {}) if isinstance(settings, dict) else {}
    proxy = str(spot_config.get("http") or "http://127.0.0.1:7897")
    https_proxy = str(spot_config.get("https") or proxy)
    env["HTTP_PROXY"] = proxy
    env["HTTPS_PROXY"] = https_proxy
    env["ALL_PROXY"] = proxy
    env["http_proxy"] = proxy
    env["https_proxy"] = https_proxy
    env["all_proxy"] = proxy
    return env


def log_proxy_settings(settings: dict[str, Any]) -> None:
    proxy = (settings.get("proxy", {}) or {}).get("http") or "http://127.0.0.1:7897"
    print(f"[env] proxy={proxy}", flush=True)


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


def history_marker(data_dir: pathlib.Path, mode: str, pairs: list[str], timeframes: set[str], timerange: str) -> pathlib.Path:
    """Identify a completed backward-history bootstrap for this exact dataset."""
    identity = json.dumps(
        {
            "mode": mode,
            "pairs": sorted(pairs),
            "timeframes": sorted(timeframes),
            "timerange": timerange,
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return data_dir / ".history_complete" / f"{mode}-{digest}.json"


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


def extract_whitelist(config: dict[str, Any]) -> list[str]:
    exchange = config.get("exchange") or {}
    pairs = exchange.get("pair_whitelist") or []
    return [str(pair) for pair in pairs if str(pair).strip()]


def refresh_market_data(settings: dict[str, Any], specs: list[StrategySpec], timeranges: list[str]) -> None:
    by_mode: dict[str, set[str]] = {}
    for spec in specs:
        by_mode.setdefault(spec.mode, set()).add(spec.timeframe)
    if not by_mode:
        return
    print(f"[data] refresh targets: {', '.join(f'{mode}({','.join(sorted(timeframes))})' for mode, timeframes in sorted(by_mode.items()))}", flush=True)
    for mode, timeframes in sorted(by_mode.items()):
        config = json.loads(config_path_for_mode(mode).read_text(encoding="utf-8"))
        pairs = extract_whitelist(config)
        if not pairs:
            continue
        print(f"[data] mode={mode} pairs={describe_pairs(config)}", flush=True)
        print(f"[data] mode={mode} timeframes={', '.join(sorted(timeframes))}", flush=True)
        timerange = timeranges[-1] if timeranges else "20210101-"
        command = freqtrade_command(settings) + [
            "download-data",
            "--config", str(config_path_for_mode(mode)),
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
            f"[data] mode={mode} download complete: files={after_count} "
            f"({after_count - before_count:+d}), size={human_size(after_size)} "
            f"({human_size(max(0, after_size - before_size))} added)",
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


def normalize_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "total_trades", "wins", "draws", "losses", "winrate", "profit_total",
        "profit_total_abs", "profit_mean", "profit_factor", "expectancy",
        "expectancy_ratio", "sharpe", "sortino", "calmar", "sqn", "cagr",
        "max_drawdown_account", "max_drawdown_abs", "trades_per_day",
        "market_change", "backtest_days", "final_balance", "starting_balance",
    ]
    result = {key: numeric(raw.get(key)) for key in keys}
    result.update({
        "backtest_start": raw.get("backtest_start"),
        "backtest_end": raw.get("backtest_end"),
        "strategy_timeframe": raw.get("timeframe"),
        "trading_mode": raw.get("trading_mode"),
    })
    return result


def run_one(
    spec: StrategySpec,
    timerange: str,
    run_dir: pathlib.Path,
    settings: dict[str, Any],
    adapter: LeverageAdapter,
    leverage: float,
) -> dict[str, Any]:
    started = time.monotonic()
    target = run_dir / spec.mode / spec.name / timerange
    target.mkdir(parents=True, exist_ok=True)
    command = freqtrade_command(settings) + [
        "backtesting",
        "--config", str(ROOT / "configs" / f"{spec.mode}.json"),
        "--userdir", str(USER_DATA_DIR),
        "--datadir", str(DATA_DIR),
        "--strategy-path", str(adapter.strategy_path),
        "--strategy", adapter.strategy_name,
        "--timeframe", spec.timeframe,
        "--timerange", timerange,
        "--cache", "none",
        "--export", "trades",
        "--backtest-directory", str(target),
    ]
    process = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=subprocess_env(settings))
    (target / "backtest.log").write_text(process.stdout, encoding="utf-8")
    row: dict[str, Any] = {
        **asdict(spec),
        "timerange": timerange,
        "status": "success" if process.returncode == 0 else "failed",
        "error": "",
        "duration_seconds": round(time.monotonic() - started, 2),
        "run_directory": str(target.relative_to(PROJECT_ROOT)),
        "leverage": leverage,
    }
    if process.returncode != 0:
        lines = [line.strip() for line in process.stdout.splitlines() if line.strip()]
        row["error"] = lines[-1][:500] if lines else f"exit code {process.returncode}"
        return row
    raw = find_result(target, adapter.strategy_name)
    if raw is None:
        row["status"] = "failed"
        row["error"] = "Freqtrade completed but no result JSON was found"
        return row
    row.update(normalize_metrics(raw))
    return row


def write_results(rows: list[dict[str, Any]], run_dir: pathlib.Path, settings: dict[str, Any]) -> None:
    payload = {"generated_at": utc_now(), "settings": settings, "rows": rows}
    (run_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_xlsx_report(run_dir: pathlib.Path, rows: list[dict[str, Any]]) -> pathlib.Path:
    import pandas as pd
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    xlsx_path = run_dir / RESULTS_XLSX_NAME
    columns = sorted({key for row in rows for key in row})
    missing_labels = [column for column in columns if column not in XLSX_COLUMN_LABELS]
    if missing_labels:
        raise ValueError(f"XLSX 字段缺少中文名称：{', '.join(missing_labels)}")
    column_labels = [XLSX_COLUMN_LABELS[column] for column in columns]
    dataframe = pd.DataFrame(rows).reindex(columns=columns)
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        dataframe.to_excel(writer, index=False, header=column_labels, sheet_name="回测汇总")
        worksheet = writer.sheets["回测汇总"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions
        worksheet.sheet_view.showGridLines = False
        header_fill = PatternFill("solid", fgColor="1F4E78")
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center", vertical="center")
        worksheet.row_dimensions[1].height = 24
        percentage_columns = {
            "cagr", "market_change", "max_drawdown_account", "profit_mean",
            "profit_total", "winrate",
        }
        for column_index, column_name in enumerate(columns, start=1):
            values = [XLSX_COLUMN_LABELS[column_name], *("" if value is None else str(value) for value in dataframe[column_name])]
            worksheet.column_dimensions[get_column_letter(column_index)].width = min(max(max(map(len, values)) + 2, 11), 32)
            if column_name in percentage_columns:
                for cell in worksheet.iter_cols(
                    min_col=column_index,
                    max_col=column_index,
                    min_row=2,
                    max_row=max(2, worksheet.max_row),
                ):
                    for item in cell:
                        item.number_format = "0.00%"
    return xlsx_path


def percentile(value: float, values: list[float], inverse: bool = False) -> float:
    if len(values) <= 1:
        return 1.0
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    rank = (below + 0.5 * max(0, equal - 1)) / (len(values) - 1)
    rank = max(0.0, min(1.0, rank))
    return 1.0 - rank if inverse else rank


def score_rows(rows: list[dict[str, Any]], settings: dict[str, Any]) -> list[dict[str, Any]]:
    minimum_trades = int(settings["minimum_trades"])
    weights = settings["scoring_weights"]
    scored = [dict(row) for row in rows]
    for row in scored:
        trades = row.get("total_trades") or 0
        reasons: list[str] = []
        if row.get("status") != "success":
            reasons.append("backtest_failed")
        if trades < minimum_trades:
            reasons.append("insufficient_trades")
        if row.get("lookahead_flag"):
            reasons.append("lookahead_bias_flag")
        row["eligible"] = not reasons
        row["eligibility_reason"] = ",".join(reasons)
        row["composite_score"] = None
    groups = sorted({(row.get("mode"), row.get("timerange")) for row in scored})
    metric_map = {
        "profit_total": ("profit_total", False),
        "sharpe": ("sharpe", False),
        "sortino": ("sortino", False),
        "calmar": ("calmar", False),
        "drawdown": ("max_drawdown_account", True),
    }
    for group in groups:
        candidates = [row for row in scored if (row.get("mode"), row.get("timerange")) == group and row["eligible"]]
        if not candidates:
            continue
        distributions = {
            label: [float(row[field]) for row in candidates if numeric(row.get(field)) is not None]
            for label, (field, _) in metric_map.items()
        }
        for row in candidates:
            total = 0.0
            used_weight = 0.0
            for label, (field, inverse) in metric_map.items():
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
    return scored


def write_rankings(rows: list[dict[str, Any]], run_dir: pathlib.Path, settings: dict[str, Any]) -> list[dict[str, Any]]:
    ranked = score_rows(rows, settings)
    ordered = sorted(ranked, key=lambda row: (not bool(row.get("eligible")), str(row.get("mode")), -(float(row.get("composite_score") or -1)), str(row.get("name"))))
    write_xlsx_report(run_dir, ordered)
    return ordered


def command_inventory(args: argparse.Namespace) -> int:
    verify_framework_unchanged()
    print("[inventory] scanning strategies...", flush=True)
    specs = discover_strategies()
    destination = pathlib.Path(args.output) if args.output else ROOT / "inventory.json"
    write_inventory(specs, destination)
    counts = {mode: sum(spec.mode == mode for spec in specs) for mode in ("spot", "futures")}
    print(f"[inventory] found {len(specs)} strategies -> spot={counts['spot']} futures={counts['futures']}", flush=True)
    print(json.dumps({"count": len(specs), "modes": counts, "output": str(destination)}, ensure_ascii=False))
    return 0


def select_modes(specs: list[StrategySpec], mode: str) -> list[StrategySpec]:
    """Select strategies whose market data and backtests were requested."""
    requested = {"spot", "futures"} if mode == "all" else {mode}
    return [spec for spec in specs if spec.mode in requested]


def command_run(args: argparse.Namespace) -> int:
    verify_framework_unchanged()
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings = load_settings()
    leverage = validate_leverage(args.leverage if args.leverage is not None else settings.get("leverage", 1.0))
    log_proxy_settings(settings)
    timeranges = args.timerange or list(settings["timeranges"])
    print("[run] scanning strategies...", flush=True)
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
    print(
        f"[run] selected {len(specs)} strategies: spot={counts['spot']}, "
        f"futures={counts['futures']}, timeranges={timeranges}, leverage={leverage}x",
        flush=True,
    )
    if args.stage in {"data", "all"}:
        print("[run] refreshing market data...", flush=True)
        refresh_market_data(settings, specs, timeranges)
        print("[run] market data refreshed", flush=True)
    else:
        print("[run] stage=backtest: using existing local data without downloading", flush=True)
    if args.stage == "data":
        print("[run] stage=data complete; backtesting was not started", flush=True)
        return 0
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    adapter_dir = run_dir / "leverage_adapters"
    adapters = {
        spec.name: create_leverage_adapter(
            spec.name,
            STRATEGY_DIR / spec.file,
            adapter_dir / spec.name,
            leverage,
        )
        for spec in specs
    }
    write_inventory(specs, run_dir / "inventory.json")
    print(f"[run] output directory: {run_dir}", flush=True)
    work = [(spec, timerange) for timerange in timeranges for spec in specs]
    rows: list[dict[str, Any]] = []
    print(f"[run] starting backtests: {len(work)} task(s)", flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        futures = {
            executor.submit(run_one, spec, timerange, run_dir, settings, adapters[spec.name], leverage): (spec, timerange)
            for spec, timerange in work
        }
        for future in concurrent.futures.as_completed(futures):
            spec, timerange = futures[future]
            try:
                row = future.result()
            except Exception as exc:
                row = {**asdict(spec), "timerange": timerange, "status": "failed", "error": f"orchestrator error: {exc}"}
            rows.append(row)
            print(f"[{len(rows)}/{len(work)}] {row['status']}: {spec.name} ({timerange})", flush=True)
            write_results(rows, run_dir, settings)
    rows.sort(key=lambda row: (str(row.get("mode")), str(row.get("name")), str(row.get("timerange"))))
    write_results(rows, run_dir, settings)
    write_rankings(rows, run_dir, settings)
    print(f"[run] finished. results: {run_dir / 'backtest_results.xlsx'}", flush=True)
    print(run_dir)
    return 0 if any(row.get("status") == "success" for row in rows) else 2


def command_summarize(args: argparse.Namespace) -> int:
    run_dir = pathlib.Path(args.run_dir).resolve()
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    ranked = write_rankings(payload["rows"], run_dir, payload.get("settings") or load_settings())
    eligible = [row for row in ranked if row.get("eligible")]
    print(json.dumps({"rows": len(ranked), "eligible": len(eligible), "best": eligible[0].get("name") if eligible else None}, ensure_ascii=False))
    return 0


def command_merge(args: argparse.Namespace) -> int:
    destination = RUNS_DIR / args.run_id
    destination.mkdir(parents=True, exist_ok=False)
    selected: dict[tuple[str, str, str], dict[str, Any]] = {}
    settings = load_settings()
    for source_name in args.source:
        source = pathlib.Path(source_name).resolve()
        payload = json.loads((source / "results.json").read_text(encoding="utf-8"))
        settings = payload.get("settings") or settings
        for row in payload["rows"]:
            key = (str(row.get("mode")), str(row.get("name")), str(row.get("timerange")))
            current = selected.get(key)
            if current is None or (current.get("status") != "success" and row.get("status") == "success") or current.get("status") == row.get("status"):
                selected[key] = row
    rows = sorted(selected.values(), key=lambda row: (str(row.get("mode")), str(row.get("name")), str(row.get("timerange"))))
    write_results(rows, destination, settings)
    ranked = write_rankings(rows, destination, settings)
    print(json.dumps({"rows": len(ranked), "output": str(destination)}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="Discover strategy classes without importing them")
    inventory.add_argument("--output")
    inventory.set_defaults(func=command_inventory)
    run = commands.add_parser("run", help="Run isolated Docker backtests")
    run.add_argument(
        "--mode",
        choices=["spot", "futures", "all"],
        default="futures",
        help="Market to download/backtest: spot, futures, or both (all).",
    )
    run.add_argument("--timerange", action="append")
    run.add_argument("--strategy", action="append")
    run.add_argument("--path-prefix", action="append", help="Run strategy files below this relative directory prefix")
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--jobs", type=int, default=1)
    run.add_argument("--leverage", type=float, help="Controlled futures leverage (1-100); capped by the exchange")
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
