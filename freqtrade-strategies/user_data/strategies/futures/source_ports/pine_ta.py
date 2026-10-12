"""Pine Script `ta.*` / bare-builtin semantics for source ports.

Every function here models a documented Pine behaviour. Where TradingView's
exact internal seeding is not publicly specified (notably `ta.ema`), the
modelled choice is named in the docstring and listed in
strategy_migration/PINE_SEMANTICS.md as an unresolved parity risk rather than
being presented as certified equivalence.

All functions take and return pandas Series aligned to the input index. `na`
is represented by NaN. Pine's functions are na-aware: an na observation does
not consume a smoothing step and does not count toward a window.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = [
    "na", "nz", "pine_sma", "pine_ema", "pine_rma", "pine_wma", "pine_vwma",
    "pine_stdev", "pine_variance", "pine_highest", "pine_lowest", "pine_sum",
    "pine_change", "pine_roc", "pine_crossover", "pine_crossunder", "pine_cross",
    "pine_barssince", "pine_valuewhen", "pine_tr", "pine_atr", "pine_rsi",
    "pine_macd", "pine_linreg", "pine_cum", "pine_avg", "pine_median",
    "pine_mode", "pine_percentile", "pine_pivothigh", "pine_pivotlow",
    "pine_source", "pine_round", "pine_sign", "pine_abs", "pine_max", "pine_min",
]


def _as_series(value, index=None, name=None) -> pd.Series:
    if isinstance(value, pd.Series):
        return value.astype(float)
    if index is None:
        raise ValueError("a scalar source requires an explicit index")
    return pd.Series(float(value), index=index, dtype=float, name=name)


def _length(length) -> int:
    """Pine requires a positive integer length; reject silent coalescing."""
    if isinstance(length, bool) or int(length) != length or int(length) < 1:
        raise ValueError(f"Pine length must be a positive integer, got {length!r}")
    return int(length)


def na(value):
    return pd.isna(value)


def nz(value, replacement=0.0):
    """Pine `nz`: replace na with replacement (2-arg form) or 0."""
    if isinstance(value, pd.Series):
        return value.fillna(replacement)
    return replacement if pd.isna(value) else value


def pine_sma(source, length) -> pd.Series:
    """Simple mean of the last `length` non-na observations.

    Pine's ta.sma uses a rolling window over *bars*, and returns na until
    `length` bars have elapsed. na values inside the window propagate na.
    """
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).mean()


def pine_ema(source, length) -> pd.Series:
    """Exponential moving average, alpha = 2/(length+1).

    MODELLED CHOICE (parity risk): the running value is seeded with the first
    non-na observation and an na observation does not advance the recursion.
    TradingView does not publish its exact seeding rule; ports that need the
    alternative SMA-seeded variant must pass `seed='sma'`.
    """
    source = _as_series(source)
    length = _length(length)
    return _ema_impl(source, length, seed="first")


def _ema_impl(source: pd.Series, length: int, seed: str, offset: int = 0) -> pd.Series:
    if seed not in ("first", "sma"):
        raise ValueError("seed must be 'first' or 'sma'")
    alpha = 2.0 / (length + 1)
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    state = np.nan
    seen = 0
    window: list[float] = []
    for i, value in enumerate(values):
        if np.isnan(value):
            out[i] = state
            continue
        if np.isnan(state):
            if seed == "sma":
                seen += 1
                window.append(value)
                if seen < length:
                    out[i] = np.nan
                    continue
                state = float(np.mean(window))
                out[i] = state
                continue
            state = value
        else:
            state = alpha * value + (1.0 - alpha) * state
        out[i] = state
    return pd.Series(out, index=source.index, dtype=float)


def pine_rma(source, length) -> pd.Series:
    """Wilder smoothing (Pine ta.rma).

    Seeds with the SMA of the first `length` non-na observations, then
    `state = (state * (length - 1) + x) / length`. na observations are skipped
    without advancing the recursion.
    """
    source = _as_series(source)
    length = _length(length)
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    state = np.nan
    window: list[float] = []
    for i, value in enumerate(values):
        if np.isnan(value):
            out[i] = state
            continue
        if np.isnan(state):
            window.append(value)
            if len(window) < length:
                out[i] = np.nan
                continue
            state = float(np.mean(window))
        else:
            state = (state * (length - 1) + value) / length
        out[i] = state
    return pd.Series(out, index=source.index, dtype=float)


def pine_wma(source, length) -> pd.Series:
    """Weighted MA, weights 1..length with the newest observation heaviest."""
    source = _as_series(source)
    length = _length(length)
    weights = np.arange(1, length + 1, dtype=float)
    denominator = weights.sum()

    def _w(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        return float(np.dot(window, weights) / denominator)

    return source.rolling(length, min_periods=length).apply(_w, raw=True)


def pine_vwma(source, length) -> pd.Series:
    """Volume-weighted MA: sma(source * volume, length) / sma(volume, length)."""
    source = _as_series(source)
    volume = _as_series(source.attrs["volume"]) if "volume" in source.attrs else None
    if volume is None:
        raise ValueError("pine_vwma requires source.attrs['volume']")
    length = _length(length)
    numerator = (source * volume).rolling(length, min_periods=length).sum()
    denominator = volume.rolling(length, min_periods=length).sum()
    return numerator / denominator


def pine_stdev(source, length) -> pd.Series:
    """Population standard deviation (ddof=0), as Pine ta.stdev computes it."""
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).std(ddof=0)


def pine_variance(source, length) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).var(ddof=0)


def pine_highest(source, length) -> pd.Series:
    """Rolling maximum. Pine returns na until `length` bars have elapsed."""
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).max()


def pine_lowest(source, length) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).min()


def pine_sum(source, length) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).sum()


def pine_change(source, length=1) -> pd.Series:
    source = _as_series(source)
    return source - source.shift(_length(length))


def pine_roc(source, length=1) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    previous = source.shift(length)
    return 100.0 * (source - previous) / previous


def pine_crossover(a, b) -> pd.Series:
    """True on the bar where a crosses above b.

    Pine: `a > b and a[1] <= b[1]`. An na on either side yields na -> False,
    because Pine treats na comparisons as false in a boolean context.
    """
    a = _as_series(a)
    b = _as_series(b) if not np.isscalar(b) else pd.Series(float(b), index=a.index)
    return ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False)


def pine_crossunder(a, b) -> pd.Series:
    a = _as_series(a)
    b = _as_series(b) if not np.isscalar(b) else pd.Series(float(b), index=a.index)
    return ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False)


def pine_cross(a, b) -> pd.Series:
    return pine_crossover(a, b) | pine_crossunder(a, b)


def pine_barssince(condition) -> pd.Series:
    """Bars since the condition was last true; na until the first true."""
    condition = _as_series(condition).fillna(0).astype(bool)
    out = np.full(len(condition), np.nan)
    count = np.nan
    for i, flag in enumerate(condition.to_numpy()):
        if flag:
            count = 0.0
        elif not np.isnan(count):
            count += 1.0
        out[i] = count
    return pd.Series(out, index=condition.index, dtype=float)


def pine_valuewhen(condition, source, occurrence=0) -> pd.Series:
    """Value of `source` on the occurrence-th most recent true `condition`.

    occurrence=0 is the most recent. Carries forward until a new occurrence.
    """
    condition_series = _as_series(condition)
    condition = condition_series.fillna(0).astype(bool).to_numpy()
    source = _as_series(source, index=condition_series.index).to_numpy(dtype=float)
    occurrence = int(occurrence)
    if occurrence < 0:
        raise ValueError("occurrence must be >= 0")
    out = np.full(len(source), np.nan)
    history: list[float] = []
    state = np.nan
    for i in range(len(source)):
        if condition[i]:
            history.append(source[i])
        if len(history) > occurrence:
            state = history[-1 - occurrence]
        out[i] = state
    return pd.Series(out, index=condition_series.index, dtype=float)


def pine_tr(dataframe, handle_na=False) -> pd.Series:
    """True range. handle_na=True makes the first bar high-low (Pine ta.tr(true))."""
    previous_close = dataframe["close"].shift(1)
    high, low = dataframe["high"], dataframe["low"]
    value = pd.concat(
        [(high - low).abs(), (high - previous_close).abs(), (low - previous_close).abs()],
        axis=1,
    ).max(axis=1)
    if handle_na:
        value = value.where(previous_close.notna(), high - low)
    return value


def pine_atr(dataframe, length) -> pd.Series:
    return pine_rma(pine_tr(dataframe, handle_na=True), length)


def pine_rsi(source, length) -> pd.Series:
    """Pine ta.rsi: 100 - 100 / (1 + rma(gain)/rma(loss))."""
    source = _as_series(source)
    length = _length(length)
    delta = source.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    average_gain = pine_rma(gain, length)
    average_loss = pine_rma(loss, length)
    with np.errstate(divide="ignore", invalid="ignore"):
        relative = average_gain / average_loss
        out = 100.0 - 100.0 / (1.0 + relative)
    # Pine returns 100 when there were no losses in the window.
    out = out.where(average_loss != 0.0, 100.0)
    return out.where(average_gain.notna() & average_loss.notna())


def pine_macd(source, fast, slow, signal) -> pd.Series:
    """Pine ta.macd returns [macdLine, signalLine, histLine] as a DataFrame."""
    source = _as_series(source)
    fast, slow, signal = _length(fast), _length(slow), _length(signal)
    macd_line = pine_ema(source, fast) - pine_ema(source, slow)
    signal_line = pine_ema(macd_line, signal)
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "hist": macd_line - signal_line}
    )


def pine_linreg(source, length, offset=0) -> pd.Series:
    """Least-squares linear regression value, `offset` bars back from the end."""
    source = _as_series(source)
    length = _length(length)
    offset = int(offset)
    x = np.arange(length, dtype=float)
    x_mean = x.mean()
    denominator = ((x - x_mean) ** 2).sum()

    def _reg(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        slope = np.dot(x - x_mean, window - window.mean()) / denominator
        intercept = window.mean() - slope * x_mean
        return intercept + slope * (length - 1 - offset)

    return source.rolling(length, min_periods=length).apply(_reg, raw=True)


def pine_cum(source) -> pd.Series:
    source = _as_series(source)
    return source.fillna(0.0).cumsum()


def pine_avg(a, b):
    return (a + b) / 2.0


def pine_median(source, length) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    return source.rolling(length, min_periods=length).median()


def pine_mode(source, length) -> pd.Series:
    source = _as_series(source)
    length = _length(length)

    def _mode(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        values, counts = np.unique(window, return_counts=True)
        return float(values[int(np.argmax(counts))])

    return source.rolling(length, min_periods=length).apply(_mode, raw=True)


def pine_percentile(source, length, percent) -> pd.Series:
    source = _as_series(source)
    length = _length(length)
    percent = float(percent)

    def _percentile(window: np.ndarray) -> float:
        if np.isnan(window).any():
            return np.nan
        return float(np.percentile(window, percent))

    return source.rolling(length, min_periods=length).apply(_percentile, raw=True)


def pine_pivothigh(source, left, right) -> pd.Series:
    """Pine ta.pivothigh: value of the pivot high, reported `right` bars later."""
    source = _as_series(source)
    left, right = _length(left), _length(right)
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(left, len(values) - right):
        if np.isnan(values[i]):
            continue
        window = values[i - left : i + right + 1]
        if np.isnan(window).any():
            continue
        if values[i] == window.max() and (window == values[i]).sum() == 1:
            out[i + right] = values[i]
    return pd.Series(out, index=source.index, dtype=float)


def pine_pivotlow(source, left, right) -> pd.Series:
    source = _as_series(source)
    left, right = _length(left), _length(right)
    values = source.to_numpy(dtype=float)
    out = np.full(len(values), np.nan)
    for i in range(left, len(values) - right):
        if np.isnan(values[i]):
            continue
        window = values[i - left : i + right + 1]
        if np.isnan(window).any():
            continue
        if values[i] == window.min() and (window == values[i]).sum() == 1:
            out[i + right] = values[i]
    return pd.Series(out, index=source.index, dtype=float)


def pine_source(dataframe, name) -> pd.Series:
    """Resolve a Pine `input.source` name against an OHLCV frame."""
    mapping = {
        "open": dataframe["open"],
        "high": dataframe["high"],
        "low": dataframe["low"],
        "close": dataframe["close"],
        "volume": dataframe["volume"],
        "hl2": (dataframe["high"] + dataframe["low"]) / 2.0,
        "hlc3": (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3.0,
        "ohlc4": (
            dataframe["open"] + dataframe["high"] + dataframe["low"] + dataframe["close"]
        )
        / 4.0,
        "hlcc4": (dataframe["high"] + dataframe["low"] + 2 * dataframe["close"]) / 4.0,
    }
    if name not in mapping:
        raise ValueError(f"unsupported Pine source {name!r}")
    return mapping[name]


def pine_round(value, precision=0):
    """Pine math.round: half away from zero, not banker's rounding."""
    precision = int(precision)
    if isinstance(value, pd.Series):
        scaled = value * (10**precision)
        return np.sign(scaled) * np.floor(np.abs(scaled) + 0.5) / (10**precision)
    scaled = float(value) * (10**precision)
    return float(np.sign(scaled) * np.floor(abs(scaled) + 0.5) / (10**precision))


def pine_sign(value):
    return np.sign(value)


def pine_abs(value):
    return abs(value)


def pine_max(a, b):
    return np.maximum(a, b)


def pine_min(a, b):
    return np.minimum(a, b)
