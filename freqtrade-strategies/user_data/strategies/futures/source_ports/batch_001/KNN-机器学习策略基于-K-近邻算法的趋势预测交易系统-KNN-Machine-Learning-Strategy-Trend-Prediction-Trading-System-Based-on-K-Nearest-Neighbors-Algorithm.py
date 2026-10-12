"""Port of sources/SM_f400ed9ce8083e5a.pine (batch_001/KNN-机器学习策略基于-K-近邻算法的趋势预测交易系统-KNN-Machine-Learning-Strategy-Trend-Prediction-Trading-System-Based-on-K-Nearest-Neighbors-Algorithm.md).

Pine v5, `strategy('money printer part 1', overlay=true)`. A K-nearest-
neighbour smoother of a price series, then a 5-period WMA of it, traded on its
own two-bar turn:

    windowSize = math.max(numberOfClosestValues, 30)

    value_in  = switch PriceValue      // default "hl2"
        "hl2" => ta.sma(hl2, maLen)
        ... other arms ...
    target_in = switch TargetValue     // default "Price Action"
        "Price Action" => ta.rma(close, maLen_)
        ... other arms ...

    meanOfKClosest(value_, target_) =>
        closestDistances = array.new_float(numberOfClosestValues, 1e10)
        closestValues    = array.new_float(numberOfClosestValues, 0.0)
        for i = 1 to windowSize
            value    = value_[i]
            distance = math.abs(target_ - value)
            maxDistIndex = 0
            maxDistValue = closestDistances.get(0)
            for j = 1 to numberOfClosestValues - 1
                if closestDistances.get(j) > maxDistValue
                    maxDistIndex := j
                    maxDistValue := closestDistances.get(j)
            if distance < maxDistValue
                closestDistances.set(maxDistIndex, distance)
                closestValues.set(maxDistIndex, value)
        closestValues.sum() / numberOfClosestValues

    knnMA = meanOfKClosest(value_in, target_in)

    knnMA_ = ta.wma(knnMA, 5)
    LongCondtion  = knnMA_[1] < knnMA_ and knnMA_[1] <= knnMA_[2]
    ShortCondtion = knnMA_[1] > knnMA_ and knnMA_[1] >= knnMA_[2]

    strategy.entry("Long",  strategy.long,  when = LongCondtion)
    strategy.close("Long",  when = ShortCondtion)
    strategy.entry("Short", strategy.short, when = ShortCondtion)
    strategy.close("short", when = LongCondtion)

`meanOfKClosest` keeps the `numberOfClosestValues` nearest samples of
`value_` to today's `target_` over the trailing `windowSize` bars and averages
them. Before the window has filled it replaces nothing, and Pine then sums an
all-zero array: the early `knnMA` values are 0.0, NOT na. That is reproduced --
it feeds the WMA warm-up and therefore the first tradeable signals.

The `knn()` classifier (`knn_prediction`, `c`, `o`, `price`) and `MAknn_`, the
background colouring and the nine `alertcondition` calls do not reach any
order; `knn_prediction` is still computed so the port carries the source's
indicator surface, and the rest are display-only.

`strategy()` declares only `title` / `overlay`, so Pine's documented defaults
apply and are what this port carries: `default_qty_type=fixed`, one unit per
order, `commission_value=0`, `pyramiding=0`, `process_orders_on_close=false`,
initial capital 1000000.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity, not the strategy's period.

Neither `strategy.close` carries a price leg, so `source_reproduce_stops` is
False and the only exits are next-open market closes.

FIDELITY:

* The last close names entry id "short" (lower case) while the entry it means
  is spelled "Short". The shared engine matches order ids by exact string, so
  `close("short")` is a no-op there; the port writes the source's own literal
  rather than silently "fixing" the case. In practice the two spellings agree:
  `LongCondtion` and `ShortCondtion` are mutually exclusive, so on the bar
  `close("short")` is placed the preceding `entry("Long")` has already
  reversed any short by the time the close is filled. Whether TradingView
  matches ids case-insensitively is unverified and is NOT assumed.
* `windowSize` is `math.max(numberOfClosestValues, 30)`, so with the declared
  default of 3 the window is 30 bars; a larger k widens it to k. The port
  reproduces the `max` rather than hard-coding 30.
* The `switch` arms reachable only by overriding the string inputs: `sma`,
  `wma`, `ema` and (for the target) `Volatility` -> `ta.atr(14)` are
  implemented; `VWAP` (`ta.vwap`) and `hma` (`ta.hma`) are NOT implemented and
  raise instead of being approximated. Neither is reachable with the source's
  declared defaults ("hl2" / "Price Action"), which is what a backtest runs.
  TradingView never published its exact internal rounding for `ta.hma`'s
  `length / 2` argument, and `ta.vwap` is session-anchored, which the offline
  engine does not model at all (PINE_SEMANTICS.md section 2.1).
* The colour inputs (`Upknn_col`, `Dnknn_col`, `Neuknn_col`, `Maknn_col`,
  `Up_col`, `Dn_col`) and the `bgcolor` bool are declared inputs but only
  drive `plot` / `bgcolor`; they carry no order logic and are recorded here
  rather than duplicated in `source_defaults`.
* `math.sqrt(math.pow(price[j] - price, 2))` is `|price[j] - price|`; the port
  uses the absolute value directly.
* `input.string` / `input.int` bounds (minval / maxval) are validation only and
  place no order.
* The tooltip strings `t1`..`t5` are documentation.
* Leverage, margin, liquidation, funding and venue contract-step rounding are
  not modelled.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _mean_of_k_closest(values, target, k, window, series_index):
    """Pine `meanOfKClosest`: average of the k nearest past `values` to today.

    Walks back `window` bars from each bar, keeping the k samples closest to
    that bar's `target`. na samples (either the value or the target) fail the
    `distance < maxDistValue` test in Pine and are skipped here for the same
    reason. The k-array starts at 1e10 distances and 0.0 values, so before the
    window fills the sum is 0 and Pine divides it by k -- early output is 0.0,
    not na, and that is what the port returns.
    """
    n = len(values)
    values = np.asarray(values, dtype=float)
    target = np.asarray(target, dtype=float)
    out = np.zeros(n, dtype=float)
    for t in range(n):
        closest_distances = np.full(k, 1e10)
        closest_values = np.zeros(k)
        target_t = target[t]
        if not np.isfinite(target_t):
            continue
        for i in range(1, window + 1):
            index = t - i
            if index < 0:
                break
            value = values[index]
            if not np.isfinite(value):
                continue
            distance = abs(target_t - value)
            max_dist_index = 0
            max_dist_value = closest_distances[0]
            for j in range(1, k):
                if closest_distances[j] > max_dist_value:
                    max_dist_index = j
                    max_dist_value = closest_distances[j]
            if distance < max_dist_value:
                closest_distances[max_dist_index] = distance
                closest_values[max_dist_index] = value
        out[t] = closest_values.sum() / k
    return pd.Series(out, index=series_index)


def _knn_prediction(price, c, o, series_index, lookback=10):
    """Pine `knn(price)`: 1 when the record-setting neighbours say Pos wins.

    For j = 1..lookback the running minimum of |price[j] - price| is tracked;
    every time it is beaten, the neighbour at that offset is classified from
    `c` vs `o` and the matching counter is incremented. Output is
    `Pos_count > Neg_count ? 1 : -1`, so a tie (including no update at all,
    which is what the first bars produce) returns -1. na distances fail the
    strict `<` in Pine and are skipped identically here.
    """
    n = len(price)
    price = np.asarray(price, dtype=float)
    c = np.asarray(c, dtype=float)
    o = np.asarray(o, dtype=float)
    out = np.full(n, -1.0)
    for t in range(n):
        pos_count = 0
        neg_count = 0
        min_distance = 10e10
        price_t = price[t]
        if not np.isfinite(price_t):
            out[t] = -1.0
            continue
        for j in range(1, lookback + 1):
            index = t - j
            if index < 0:
                break
            neighbour = price[index]
            if not np.isfinite(neighbour):
                continue
            distance = abs(neighbour - price_t)
            if distance < min_distance:
                min_distance = distance
                neighbour_c = c[index]
                neighbour_o = o[index]
                if np.isfinite(neighbour_c) and np.isfinite(neighbour_o):
                    if neighbour_c < neighbour_o:
                        pos_count += 1
                    if neighbour_c > neighbour_o:
                        neg_count += 1
        out[t] = 1.0 if pos_count > neg_count else -1.0
    return pd.Series(out, index=series_index)


def _price_value_series(dataframe, name, length):
    """The source's `PriceValue` switch arms, default "hl2"."""
    close = dataframe["close"]
    if name == "hl2":
        return ta.pine_sma((dataframe["high"] + dataframe["low"]) / 2.0, length)
    if name == "sma":
        return ta.pine_sma(close, length)
    if name == "wma":
        return ta.pine_wma(close, length)
    if name == "ema":
        return ta.pine_ema(close, length)
    raise NotImplementedError(
        f"PriceValue={name!r} is not implemented; the source's declared default "
        "is 'hl2'. ta.vwap is session-anchored and ta.hma's internal rounding "
        "is unspecified -- neither is approximated here."
    )


def _target_value_series(dataframe, name, length):
    """The source's `TargetValue` switch arms, default "Price Action"."""
    close = dataframe["close"]
    if name == "Price Action":
        return ta.pine_rma(close, length)
    if name == "Volatility":
        # `ta.atr(14)` -- the 14 is a literal in the source, not `maLen_`.
        return ta.pine_atr(dataframe, 14)
    if name == "sma":
        return ta.pine_sma(close, length)
    if name == "wma":
        return ta.pine_wma(close, length)
    if name == "ema":
        return ta.pine_ema(close, length)
    raise NotImplementedError(
        f"TargetValue={name!r} is not implemented; the source's declared "
        "default is 'Price Action'. See the PriceValue note."
    )


class SMKnnTrendPrediction_f400ed(PinePortBase, IStrategy):
    source_id = "SM_f400ed9ce8083e5a"
    source_file = (
        "KNN-机器学习策略基于-K-近邻算法的趋势预测交易系统-"
        "KNN-Machine-Learning-Strategy-Trend-Prediction-Trading-System-"
        "Based-on-K-Nearest-Neighbors-Algorithm.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "PriceValue": "hl2",
        "maLen": 5,
        "TargetValue": "Price Action",
        "maLen_": 5,
        "numberOfClosestValues": 3,
        "smoothingPeriod": 50,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The last strategy.close names entry id \"short\" while the entry it "
        "means is spelled \"Short\". The shared engine matches ids exactly, so "
        "the port's close(\"short\") is a no-op there; the source's literal is "
        "kept rather than silently recased. The two spellings coincide in "
        "effect here because the long and short conditions are mutually "
        "exclusive and the preceding reverse entry has already closed the "
        "short by the time the close fills. Whether TradingView matches ids "
        "case-insensitively is UNVERIFIED and is not assumed.",
        "windowSize = math.max(numberOfClosestValues, 30), reproduced rather "
        "than hard-coded to 30.",
        "Early knnMA values are 0.0, not na: meanOfKClosest sums an all-zero "
        "k-array before the window fills. Reproduced, since it seeds the WMA "
        "warm-up and therefore the early signals.",
        "PriceValue / TargetValue switch arms 'VWAP' (ta.vwap) and 'hma' "
        "(ta.hma) are NOT implemented and raise instead of being approximated. "
        "`sma` / `wma` / `ema` and the target's 'Volatility' -> ta.atr(14) are "
        "implemented. Only the declared defaults ('hl2' / 'Price Action') are "
        "reachable in a default backtest.",
        "ta.vwap is session-anchored (PINE_SEMANTICS.md section 2.1: "
        "request.security / multi-period data are not modelled); ta.hma's "
        "half-length rounding is not published.",
        "The colour inputs (Upknn_col, Dnknn_col, Neuknn_col, Maknn_col, "
        "Up_col, Dn_col) and the `bgcolor` bool are declared inputs that only "
        "drive plot / bgcolor and place no order; they are recorded here "
        "rather than duplicated in source_defaults.",
        "knn_prediction is computed for surface completeness but reaches no "
        "order; MAknn_, price, c and o are inputs to it only.",
        "math.sqrt(math.pow(x, 2)) is |x|; the port uses the absolute value.",
        "input minval / maxval bounds and the tooltip strings are validation "
        "and documentation.",
        "No stop / limit / trailing exit exists, so source_reproduce_stops is "
        "False and an open position at the window end stays open.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        k = int(params["numberOfClosestValues"])
        smoothing = int(params["smoothingPeriod"])
        window = max(k, 30)

        value_in = _price_value_series(dataframe, str(params["PriceValue"]), int(params["maLen"]))
        target_in = _target_value_series(
            dataframe, str(params["TargetValue"]), int(params["maLen_"])
        )

        knn_ma = _mean_of_k_closest(
            value_in.to_numpy(dtype=float), target_in.to_numpy(dtype=float),
            k, window, dataframe.index,
        )

        close = dataframe["close"]
        price = (knn_ma + close) / 2.0
        c = ta.pine_rma(knn_ma.shift(1), smoothing)
        o = ta.pine_rma(knn_ma, smoothing)
        knn_prediction = ta.pine_wma(_knn_prediction(price, c, o, dataframe.index), 3)

        knn_ma_smoothed = ta.pine_wma(knn_ma, 5)

        dataframe["pine_knn_ma"] = knn_ma
        dataframe["pine_knn_ma_smoothed"] = knn_ma_smoothed
        dataframe["pine_knn_prediction"] = knn_prediction
        dataframe["pine_long_condition"] = (
            (knn_ma_smoothed.shift(1) < knn_ma_smoothed)
            & (knn_ma_smoothed.shift(1) <= knn_ma_smoothed.shift(2))
        )
        dataframe["pine_short_condition"] = (
            (knn_ma_smoothed.shift(1) > knn_ma_smoothed)
            & (knn_ma_smoothed.shift(1) >= knn_ma_smoothed.shift(2))
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, when = LongCondtion)
        broker.entry("Long", "long", when=bool(ctx["long_condition"][i]))
        # strategy.close("Long", when = ShortCondtion)
        broker.close("Long", when=bool(ctx["short_condition"][i]))
        # strategy.entry("Short", strategy.short, when = ShortCondtion)
        broker.entry("Short", "short", when=bool(ctx["short_condition"][i]))
        # strategy.close("short", when = LongCondtion)
        broker.close("short", when=bool(ctx["long_condition"][i]))
