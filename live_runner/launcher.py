#!/usr/bin/env python3
"""Launch one or more Freqtrade live instances with a small, stable parameter set."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent
STRATEGY_ROOT = PROJECT_ROOT / "freqtrade-strategies" / "user_data" / "strategies"
RUNS_DIR = ROOT / "runs"
SETTINGS_PATH = PROJECT_ROOT / "strategy_runner" / "settings.json"
PROFILES_PATH = ROOT / "profiles.json"
sys.path.insert(0, str(PROJECT_ROOT / "strategy_runner"))
from leverage_adapter import create_leverage_adapter, validate_leverage  # noqa: E402


@dataclass(frozen=True)
class InstanceSpec:
    name: str
    strategy: str
    pairs: list[str]
    mode: str
    leverage: float


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_settings() -> dict[str, Any]:
    return load_json(SETTINGS_PATH)


def load_profiles() -> dict[str, Any]:
    return load_json(PROFILES_PATH)


def find_strategy_file(strategy_name: str) -> pathlib.Path:
    for path in sorted(STRATEGY_ROOT.rglob("*.py")):
        if path.stem == strategy_name:
            return path
    raise FileNotFoundError(f"strategy not found: {strategy_name}")


def config_path_for_mode(mode: str) -> pathlib.Path:
    return PROJECT_ROOT / "strategy_runner" / "configs" / f"{mode}.json"


def parse_list(values: list[str] | None) -> list[str]:
    items: list[str] = []
    for value in values or []:
        for part in value.split(","):
            part = part.strip()
            if part:
                items.append(part)
    return items


def split_pairs(pairs: list[str], chunk_size: int) -> list[list[str]]:
    chunk_size = max(1, chunk_size)
    return [pairs[i : i + chunk_size] for i in range(0, len(pairs), chunk_size)]


def build_instance_specs(
    profile: dict[str, Any], mode: str, strategies: list[str], pairs: list[str], leverage: float
) -> list[InstanceSpec]:
    pair_chunks = split_pairs(pairs, int(profile.get("pairs_per_instance", 1)))
    specs: list[InstanceSpec] = []
    for strategy in strategies:
        for index, chunk in enumerate(pair_chunks, start=1):
            specs.append(
                InstanceSpec(
                    name=f"{strategy}-{index}", strategy=strategy, pairs=chunk, mode=mode, leverage=leverage
                )
            )
    return specs


def make_config(mode: str, strategy: str, pairs: list[str], profile: dict[str, Any], live: bool) -> dict[str, Any]:
    config = load_json(config_path_for_mode(mode))
    config["strategy"] = strategy
    config["dry_run"] = not live
    if "wallet" in profile:
        config["dry_run_wallet"] = profile["wallet"]
    if "max_open_trades" in profile:
        config["max_open_trades"] = profile["max_open_trades"]
    if "tradable_balance_ratio" in profile:
        config["tradable_balance_ratio"] = profile["tradable_balance_ratio"]
    exchange = config.setdefault("exchange", {})
    exchange["pair_whitelist"] = pairs
    return config


def freqtrade_binary(settings: dict[str, Any]) -> str:
    return str((PROJECT_ROOT / settings["freqtrade_bin"]).resolve())


def write_plan(run_dir: pathlib.Path, profile_name: str, specs: list[InstanceSpec], live: bool) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "profile": profile_name,
        "live": live,
        "instances": [
            {
                "name": spec.name,
                "strategy": spec.strategy,
                "mode": spec.mode,
                "pairs": spec.pairs,
                "leverage": spec.leverage,
            }
            for spec in specs
        ],
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "plan.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def launch_instance(settings: dict[str, Any], run_dir: pathlib.Path, spec: InstanceSpec, profile: dict[str, Any], live: bool) -> subprocess.Popen[str]:
    instance_dir = run_dir / spec.name
    instance_dir.mkdir(parents=True, exist_ok=True)
    config = make_config(spec.mode, spec.strategy, spec.pairs, profile, live)
    config_path = instance_dir / "config.json"
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    adapter = create_leverage_adapter(
        spec.strategy,
        find_strategy_file(spec.strategy),
        instance_dir / "leverage_adapter",
        spec.leverage,
    )
    log_path = instance_dir / "stdout.log"
    command = [
        freqtrade_binary(settings),
        "trade",
        "--config", str(config_path),
        "--userdir", str(PROJECT_ROOT / "strategy_runner" / "user_data"),
        "--strategy-path", str(adapter.strategy_path),
        "--strategy", adapter.strategy_name,
    ]
    with log_path.open("a", encoding="utf-8") as log_file:
        return subprocess.Popen(command, stdout=log_file, stderr=subprocess.STDOUT, text=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", default="safe_dryrun", help="Profile name from live_runner/profiles.json")
    parser.add_argument("--mode", choices=["futures"], default="futures", help="Only futures mode is supported")
    parser.add_argument("--strategy", action="append", required=True, help="Strategy class name; repeat or comma-separate")
    parser.add_argument("--pairs", action="append", required=True, help="Trading pair; repeat or comma-separate")
    parser.add_argument("--live", action="store_true", help="Run real trading instead of dry-run")
    parser.add_argument("--leverage", type=float, help="Controlled futures leverage (1-100); capped by OKX")
    parser.add_argument("--plan-only", action="store_true", help="Write configs but do not start bots")
    parser.add_argument("--run-id", help="Output directory name")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profiles = load_profiles()
    if args.profile not in profiles:
        raise SystemExit(f"unknown profile: {args.profile}")
    profile = dict(profiles[args.profile])
    mode = "futures"
    leverage = validate_leverage(args.leverage if args.leverage is not None else profile.get("leverage", 1.0))
    strategies = parse_list(args.strategy)
    pairs = parse_list(args.pairs)
    if not strategies:
        raise SystemExit("provide at least one strategy")
    if not pairs:
        raise SystemExit("provide at least one pair")
    invalid_pairs = [pair for pair in pairs if not pair.endswith("/USDT:USDT")]
    if invalid_pairs:
        raise SystemExit(
            "futures pairs must use Freqtrade contract notation such as BTC/USDT:USDT; "
            f"invalid: {', '.join(invalid_pairs)}"
        )
    specs = build_instance_specs(profile, mode, strategies, pairs, leverage)
    settings = load_settings()
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / run_id
    live = bool(args.live)
    write_plan(run_dir, args.profile, specs, live)
    if args.plan_only:
        print(str(run_dir))
        return 0
    processes: list[tuple[InstanceSpec, subprocess.Popen[str]]] = []
    for index, spec in enumerate(specs, start=1):
        proc = launch_instance(settings, run_dir, spec, profile, live)
        processes.append((spec, proc))
        print(f"[{index}/{len(specs)}] started {spec.name} -> {spec.pairs}")
        delay = float(profile.get("launch_delay_seconds", 5))
        if index < len(specs) and delay > 0:
            time.sleep(delay)
    exit_code = 0
    for spec, proc in processes:
        code = proc.wait()
        if code != 0 and exit_code == 0:
            exit_code = code
            print(f"{spec.name} exited with {code}", file=sys.stderr)
    print(str(run_dir))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
