#!/usr/bin/env python3
"""Discover strategies and run isolated Freqtrade backtests outside the framework."""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import csv
import json
import math
import pathlib
import subprocess
import time
import zipfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
STRATEGY_USER_DATA = PROJECT_ROOT / "freqtrade-strategies" / "user_data"
STRATEGY_DIR = STRATEGY_USER_DATA / "strategies"
RUNS_DIR = ROOT / "runs"
SETTINGS_PATH = ROOT / "settings.json"


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
    for path in sorted(STRATEGY_DIR.rglob("*.py")):
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
            path_parts = {part.lower() for part in relative.parts}
            found.append(
                StrategySpec(
                    name=node.name,
                    file=relative.as_posix(),
                    timeframe=timeframe,
                    mode="futures" if can_short or "futures" in path_parts else "spot",
                    can_short=can_short,
                    lookahead_flag="lookahead_bias" in path_parts,
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
    executable = (ROOT / str(settings["freqtrade_bin"])).resolve()
    if not executable.is_file():
        raise FileNotFoundError(f"Freqtrade executable not found: {executable}")
    return [str(executable)]


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


def run_one(spec: StrategySpec, timerange: str, run_dir: pathlib.Path, settings: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    target = run_dir / spec.mode / spec.name / timerange
    target.mkdir(parents=True, exist_ok=True)
    command = freqtrade_command(settings) + [
        "backtesting",
        "--config", str(ROOT / "configs" / f"{spec.mode}.json"),
        "--userdir", str(ROOT / "user_data"),
        "--datadir", str(ROOT / "data" / ("okx" if spec.mode == "spot" else "binance")),
        "--strategy-path", str((STRATEGY_DIR / spec.file).parent),
        "--strategy", spec.name,
        "--timerange", timerange,
        "--cache", "none",
        "--export", "trades",
        "--backtest-directory", str(target),
    ]
    process = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (target / "backtest.log").write_text(process.stdout, encoding="utf-8")
    row: dict[str, Any] = {
        **asdict(spec),
        "timerange": timerange,
        "status": "success" if process.returncode == 0 else "failed",
        "error": "",
        "duration_seconds": round(time.monotonic() - started, 2),
        "run_directory": str(target.relative_to(PROJECT_ROOT)),
    }
    if process.returncode != 0:
        lines = [line.strip() for line in process.stdout.splitlines() if line.strip()]
        row["error"] = lines[-1][:500] if lines else f"exit code {process.returncode}"
        return row
    raw = find_result(target, spec.name)
    if raw is None:
        row["status"] = "failed"
        row["error"] = "Freqtrade completed but no result JSON was found"
        return row
    row.update(normalize_metrics(raw))
    return row


def write_results(rows: list[dict[str, Any]], run_dir: pathlib.Path, settings: dict[str, Any]) -> None:
    payload = {"generated_at": utc_now(), "settings": settings, "rows": rows}
    (run_dir / "results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    columns = sorted({key for row in rows for key in row})
    with (run_dir / "results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


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
    (run_dir / "ranked_results.json").write_text(json.dumps({"generated_at": utc_now(), "settings": settings, "rows": ordered}, ensure_ascii=False, indent=2), encoding="utf-8")
    columns = sorted({key for row in ordered for key in row})
    with (run_dir / "ranked_results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(ordered)
    lines = ["# Freqtrade Strategy Backtest Summary", "", f"Generated: {utc_now()}", ""]
    for mode in ("spot", "futures"):
        eligible = [row for row in ordered if row.get("eligible") and row.get("mode") == mode]
        lines.extend([f"## {mode.title()} ranking", "", "| Rank | Strategy | Score | Return | Sharpe | Drawdown | Trades |", "|---:|---|---:|---:|---:|---:|---:|"])
        for row in eligible[:10]:
            lines.append(
                f"| {row.get('rank', '')} | {row.get('name', '')} | {row.get('composite_score', 0):.2f} "
                f"| {(row.get('profit_total') or 0):.2%} | {(row.get('sharpe') or 0):.2f} "
                f"| {(row.get('max_drawdown_account') or 0):.2%} | {int(row.get('total_trades') or 0)} |"
            )
        if not eligible:
            lines.append("| - | No eligible strategy | - | - | - | - | - |")
        lines.append("")
    failed = [row for row in ordered if row.get("status") != "success"]
    disqualified = [row for row in ordered if row.get("status") == "success" and not row.get("eligible")]
    lines.extend([
        "## Coverage", "",
        f"- Total attempted: {len(ordered)}",
        f"- Successful: {sum(row.get('status') == 'success' for row in ordered)}",
        f"- Failed: {len(failed)}",
        f"- Successful but disqualified: {len(disqualified)}",
        "",
        "See `ranked_results.csv` for all metrics and `results.json` for the complete audit trail.",
    ])
    (run_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return ordered


def command_inventory(args: argparse.Namespace) -> int:
    specs = discover_strategies()
    destination = pathlib.Path(args.output) if args.output else ROOT / "inventory.json"
    write_inventory(specs, destination)
    counts = {mode: sum(spec.mode == mode for spec in specs) for mode in ("spot", "futures")}
    print(json.dumps({"count": len(specs), "modes": counts, "output": str(destination)}, ensure_ascii=False))
    return 0


def command_run(args: argparse.Namespace) -> int:
    settings = load_settings()
    timeranges = args.timerange or list(settings["timeranges"])
    specs = discover_strategies()
    if args.mode != "all":
        specs = [spec for spec in specs if spec.mode == args.mode]
    if args.strategy:
        wanted = set(args.strategy)
        specs = [spec for spec in specs if spec.name in wanted]
    if args.path_prefix:
        prefixes = tuple(args.path_prefix)
        specs = [spec for spec in specs if spec.file.startswith(prefixes)]
    if args.limit:
        specs = specs[: args.limit]
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    write_inventory(specs, run_dir / "inventory.json")
    work = [(spec, timerange) for timerange in timeranges for spec in specs]
    rows: list[dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as executor:
        futures = {executor.submit(run_one, spec, timerange, run_dir, settings): (spec, timerange) for spec, timerange in work}
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
    print(run_dir)
    return 0 if any(row.get("status") == "success" for row in rows) else 2


def command_summarize(args: argparse.Namespace) -> int:
    run_dir = pathlib.Path(args.run_dir).resolve()
    payload = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
    ranked = write_rankings(payload["rows"], run_dir, payload.get("settings") or load_settings())
    eligible = [row for row in ranked if row.get("eligible")]
    print(json.dumps({"rows": len(ranked), "eligible": len(eligible), "best": eligible[0].get("name") if eligible else None}, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inventory = commands.add_parser("inventory", help="Discover strategy classes without importing them")
    inventory.add_argument("--output")
    inventory.set_defaults(func=command_inventory)
    run = commands.add_parser("run", help="Run isolated Docker backtests")
    run.add_argument("--mode", choices=["spot", "futures", "all"], default="all")
    run.add_argument("--timerange", action="append")
    run.add_argument("--strategy", action="append")
    run.add_argument("--path-prefix", action="append", help="Run strategy files below this relative directory prefix")
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--jobs", type=int, default=1)
    run.add_argument("--run-id")
    run.set_defaults(func=command_run)
    summarize = commands.add_parser("summarize", help="Rebuild rankings for an existing run")
    summarize.add_argument("run_dir")
    summarize.set_defaults(func=command_summarize)
    return parser


if __name__ == "__main__":
    parser = build_parser()
    arguments = parser.parse_args()
    raise SystemExit(arguments.func(arguments))
