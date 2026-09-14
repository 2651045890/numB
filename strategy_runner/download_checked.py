"""Run the installed Freqtrade downloader with local coverage checks and Chinese progress."""
from __future__ import annotations

import sys
import time
import os
import threading
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone


def covered(data, timeframe, candle_type, timerange, prepend, now=None):
    """Check the requested side of the range; file existence alone is insufficient."""
    from freqtrade.exchange import timeframe_to_seconds

    if data.empty or timerange is None:
        return False
    dates = data["date"]
    if dates.isna().any() or not dates.is_monotonic_increasing or dates.duplicated().any():
        return False
    if prepend:
        return timerange.starttype == "date" and dates.iloc[0].timestamp() <= timerange.startts
    # Funding intervals can vary; do not infer complete funding coverage from candle spacing.
    if str(candle_type) == "funding_rate":
        return False
    step = timeframe_to_seconds(timeframe)
    if (dates.diff().dropna().dt.total_seconds() > step).any():
        return False
    end = timerange.stopts if timerange.stoptype == "date" else (now or datetime.now(timezone.utc)).timestamp()
    last_required = (int(end) // step - 1) * step
    return dates.iloc[-1].timestamp() >= last_required


def incremental_results(pairs, process, exchange, workers):
    """Each worker owns an exchange and event loop; never share CCXT across threads."""
    from freqtrade.resolvers import ExchangeResolver
    local = threading.local()
    resources = []
    lock = threading.Lock()

    def run(pair):
        if not hasattr(local, "exchange"):
            local.exchange = ExchangeResolver.load_exchange(
                deepcopy(exchange._config), validate=False, load_leverage_tiers=False,
            )
            with lock:
                resources.append(local.exchange)
            local.exchange.reload_markets()
        return process(pair, local.exchange)

    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(run, pair): pair for pair in pairs}
            for future in as_completed(futures):
                pair = futures[future]
                try:
                    yield pair, future.result()
                except Exception as exc:
                    print(f"[数据错误] {pair} 增量更新失败：{exc}", flush=True)
                    yield pair, (True, False)
    finally:
        for resource in resources:
            resource.close()


def local_check_results(pairs, check, workers):
    """Run file-only coverage checks concurrently without creating exchange clients."""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(check, pair): pair for pair in pairs}
        for future in as_completed(futures):
            pair = futures[future]
            try:
                yield pair, future.result()
            except Exception as exc:
                raise RuntimeError(f"本地数据检查失败：{pair}：{exc}") from exc


def install_checks():
    from freqtrade.data.history import history_utils as history
    original_refresh = history.refresh_backtest_ohlcv_data
    original_download = history._download_pair_history
    state = {"failed": False, "phase": "检查"}
    outcomes = threading.local()
    existing = set()
    missing = set()
    coverage_lock = threading.Lock()

    def download(pair, **kwargs):
        key = (pair, kwargs["timeframe"], str(kwargs["candle_type"]))
        handler = kwargs["data_handler"]
        if state["phase"] == "检查":
            try:
                data = handler.ohlcv_load(
                    pair, timeframe=kwargs["timeframe"], candle_type=kwargs["candle_type"],
                    fill_missing=False, drop_incomplete=False, warn_no_data=False,
                )
                with coverage_lock:
                    (missing if data.empty else existing).add(key)
            except Exception as exc:
                # Do not silently replace unreadable user files.
                raise RuntimeError(f"本地数据检查失败：{key}：{exc}") from exc
            return True
        targets = missing if state["phase"] == "首次下载" else existing
        if key not in targets:
            return True
        if state["phase"] == "增量更新":
            data = handler.ohlcv_load(
                pair, timeframe=kwargs["timeframe"], candle_type=kwargs["candle_type"],
                fill_missing=False, drop_incomplete=False, warn_no_data=False,
            )
            if covered(data, kwargs["timeframe"], kwargs["candle_type"], kwargs.get("timerange"), False):
                print(f"[数据审核] {pair} {kwargs['timeframe']} {kwargs['candle_type']} 已覆盖，跳过下载", flush=True)
                return True
        outcomes.current["downloaded"] = True
        timerange = kwargs.get("timerange")
        # Match the framework's append boundary (excluding an incomplete final candle).
        data = handler.ohlcv_load(
            pair, timeframe=kwargs["timeframe"], candle_type=kwargs["candle_type"],
            fill_missing=False, drop_incomplete=True, warn_no_data=False,
        )
        start = data.iloc[-1]["date"].isoformat() if not data.empty else (
            timerange.startdt.isoformat() if timerange and timerange.starttype == "date" else "默认历史起点"
        )
        end = timerange.stopdt.isoformat() if timerange and timerange.stoptype == "date" else "最新可用数据"
        label = f"{pair} | 周期 {kwargs['timeframe']} | 类型 {kwargs['candle_type']}"
        print(f"[开始下载] {label} | 时间范围 {start} → {end}（UTC）", flush=True)
        started = time.monotonic()
        result = False
        try:
            result = original_download(pair, **kwargs)
            return result
        finally:
            if not result:
                outcomes.current["failed"] = True
            status = "处理完成" if result else "失败"
            print(f"[下载{status}] {label} | 耗时 {time.monotonic() - started:.1f} 秒", flush=True)

    def refresh(exchange, *, pairs, **kwargs):
        pairs = list(dict.fromkeys(pairs))
        total = len(pairs)
        existing.clear()
        missing.clear()
        state["phase"] = "检查"
        # Run the framework's task enumeration locally before any candle requests.
        kwargs.update(no_parallel_download=True, prepend=False)
        if kwargs.get("erase"):
            raise ValueError("分阶段下载不支持 --erase，请保留现有数据")
        check_workers = max(1, min(32, int(os.environ.get(
            "DATA_CHECK_WORKERS", str(min(32, (os.cpu_count() or 1) + 4)),
        ))))
        print(
            f"[数据进度] 整体检查：共 {total} 个币，已检查 0 个，剩余 {total} 个；"
            f"启用 {check_workers} 个本地并发任务，检查完成后才开始下载",
            flush=True,
        )

        def check(pair):
            unavailable = original_refresh(exchange, pairs=[pair], **kwargs)
            if unavailable:
                raise RuntimeError(f"币种不可用：{unavailable}")
            return True

        for index, (pair, _) in enumerate(local_check_results(pairs, check, check_workers), 1):
            print(f"[数据进度] 整体检查：共 {total} 个币，已检查 {index} 个，剩余 {total - index} 个", flush=True)
        missing_pairs = {key[0] for key in missing}
        existing_pairs = {key[0] for key in existing}
        print(
            f"[数据进度] 整体检查完毕：共 {total} 个币，已检查 {total} 个，"
            f"已有全部所需数据 {total - len(missing_pairs)} 个，"
            f"需要首次下载 {len(missing_pairs)} 个（缺少 {len(missing)} 份周期/类型数据）；开始首次下载",
            flush=True,
        )
        for phase, selected in (("首次下载", missing_pairs), ("增量更新", existing_pairs)):
            state["phase"] = phase
            targets = [pair for pair in pairs if pair in selected]
            completed = skipped = failed = 0
            count = len(targets)
            print(f"[数据进度] {phase}：共 {count} 个币，已完成 0 个，剩余 {count} 个", flush=True)
            def process(pair, client):
                outcomes.current = {"failed": False, "downloaded": False}
                entries = sorted(key for key in existing | missing if key[0] == pair)
                details = "，".join(f"{tf}/{kind}" for _, tf, kind in entries)
                selected_data = missing if phase == "首次下载" else existing
                current = "，".join(f"{tf}/{kind}" for key_pair, tf, kind in entries if (key_pair, tf, kind) in selected_data)
                print(f"[数据任务] {phase}：{pair} | 所需数据：{details} | 本阶段处理：{current}", flush=True)
                options = dict(kwargs)
                options["progress_tracker"] = None
                unavailable = original_refresh(client, pairs=[pair], **options)
                return bool(unavailable or outcomes.current["failed"]), outcomes.current["downloaded"]

            if phase == "首次下载":
                # Full-history pagination is request-heavy. Independent CCXT clients do not
                # share a rate limiter, so keep bootstrap downloads serial by default.
                workers = max(1, min(8, int(os.environ.get("DATA_INITIAL_WORKERS", "1"))))
            else:
                legacy_workers = os.environ.get("DATA_INCREMENTAL_WORKERS", "3")
                workers = max(1, min(8, int(os.environ.get("DATA_DOWNLOAD_WORKERS", legacy_workers))))
            if targets and workers > 1:
                print(f"[数据进度] {phase}：启用 {workers} 个并发下载任务（联网上限 {workers}）", flush=True)
                results = incremental_results(targets, process, exchange, workers)
            else:
                print(f"[数据进度] {phase}：串行下载", flush=True)
                results = ((pair, process(pair, exchange)) for pair in targets)
            for index, (pair, (has_failed, did_download)) in enumerate(results, 1):
                if has_failed:
                    failed += 1
                else:
                    completed += 1
                    skipped += int(not did_download)
                print(
                    f"[数据进度] {phase}：共 {count} 个币，已完成 {completed} 个"
                    f"（已有覆盖跳过 {skipped} 个），失败 {failed} 个，剩余待处理 {count - index} 个，刚处理 {pair}",
                    flush=True,
                )
            if failed:
                raise RuntimeError(f"{phase}有 {failed} 个币失败，请检查日志后重试")
        return []

    history._download_pair_history = download
    history.refresh_backtest_ohlcv_data = refresh


if __name__ == "__main__":
    install_checks()
    from freqtrade.main import main
    main(sys.argv[1:])
