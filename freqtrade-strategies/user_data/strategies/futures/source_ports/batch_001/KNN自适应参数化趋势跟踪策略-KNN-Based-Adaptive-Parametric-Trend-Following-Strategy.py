"""Port of sources/SM_d7c50b8bbc3f20d7.pine
(batch_001/KNN自适应参数化趋势跟踪策略-KNN-Based-Adaptive-Parametric-Trend-Following-Strategy.md).

Pine v6, on the `/*backtest` header's 1h period. A KNN "trend" vote against a
50-period SMA:

    k = input.int(5) ; window_size = input.int(20) ; ma_length = input.int(50)
    ma = ta.sma(close, ma_length)

    var float[] features = na
    var float[] distances = na
    var int[]   nearest_neighbors = na

    if bar_index >= window_size - 1
        features := array.new_float(0)
        for i = 0 to window_size - 1
            array.push(features, close[i])
        distances := array.new_float(0)
        for i = 0 to window_size - 1
            var float distance = 0.0
            for j = 0 to window_size - 1
                distance += math.pow(close[j] - array.get(features, j), 2)
            distance := math.sqrt(distance)
            array.push(distances, distance)
        if array.size(distances) > 0 and array.size(distances) >= k
            nearest_neighbors := array.new_int(0)
            for i = 0 to k - 1
                var int min_index = -1
                var float min_distance = na
                for j = 0 to array.size(distances) - 1
                    if na(min_distance) or array.get(distances, j) < min_distance
                        min_index := j
                        min_distance := array.get(distances, j)
                if min_index != -1
                    array.push(nearest_neighbors, min_index)
                    array.remove(distances, min_index)
        var float average_change = 0.0
        if array.size(nearest_neighbors) > 0
            for i = 0 to array.size(nearest_neighbors) - 1
                var int index = array.get(nearest_neighbors, i)
                if index + 1 < bar_index
                    average_change += (close[index] - close[index + 1])
            average_change := average_change / array.size(nearest_neighbors)
        if average_change > 0 and close > ma
            strategy.entry("Long", strategy.long)
        else if average_change < 0 and close < ma
            strategy.entry("Short", strategy.short)

`strategy()` declares `commission_value=0.03` with
`commission_type=strategy.commission.percent`, `currency='USD'` and
`default_qty_type=strategy.cash`. `default_qty_value` is NOT declared, so
Pine's documented default of 1 applies: every entry the source places without a
`qty=` is worth ONE US DOLLAR of the quote currency. `initial_capital` is not
declared, so Pine's documented default 1000000 stands, and `pyramiding` is not
declared, so 0.

WHY THE PORT CARRIES A BAR LOOP, AND WHAT IT FINDS. Pine's `var` initializes a
variable ONCE and then carries its value across bars *and* across loop
iterations; a `var` inside a `for` body is therefore not a per-iteration local.
Four of this source's variables are declared that way, and the port reproduces
each one with exactly that lifetime (module-level scalars threaded through the
bar loop) rather than the tidier reading in which they reset:

* `features` is rebuilt on every bar from the CURRENT bar's own history, so
  `array.get(features, j)` IS `close[j]`. The inner sum
  `math.pow(close[j] - array.get(features, j), 2)` is therefore identically
  zero, and `distance` -- which is `var` and so never resets to 0.0 after its
  first initialization -- stays 0.0 forever. Every element of `distances` is
  `sqrt(0) == 0`.
* `min_index` (var, starts -1) and `min_distance` (var, starts na) therefore
  pick index 0 on the first neighbour scan and are never re-armed by a strictly
  smaller distance (all distances compare equal), so `nearest_neighbors` is
  `[0, 0, 0, 0, 0]` on every bar -- five copies of the same index.
* `index` (var) is initialized once from `array.get(nearest_neighbors, 0)` and
  then never re-assigned, so all `k` additions use index 0 and each adds
  `close - close[1]`.
* `average_change` (var) is the only one of the four that reaches a signal. It
  is NOT reset per bar, so what the source actually accumulates is
  `average_change[i] = average_change[i-1] / k + (close - close[1])`, i.e. a
  leaky recursive mean of the one-bar change rather than the one-bar change
  itself. Before the first evaluated bar it is the value Pine gives a fresh
  `var float` -- 0.0 -- and the division by `array.size(nearest_neighbors)` is
  by `k`, not by the number of additions.

The port reproduces that recursion literally. It is not "simplified" to
`close - close[1]`, and it is not "fixed" to a real KNN: the distance arrays
really are degenerate in the source, and PINE_SEMANTICS.md's rule about not
correcting the source applies.

FIDELITY:

* `var` lifetime (once-initialized, cross-bar and cross-iteration) is the
  modelling choice that drives every result above. It is Pine's documented
  semantics for `var`; the alternative reading (a `var` inside a `for` body
  behaving as a per-iteration local) would make `distances` a list of zeros
  anyway but would remove the cross-bar recursion in `average_change`. Recorded
  as the load-bearing assumption rather than resolved.
* `default_qty_value` is undeclared, so Pine's documented default 1 applies to
  `strategy.cash`: one US dollar of notional per entry. That is far below the
  venue's minimum order size, so the framework vetoes every entry and the two
  sides of the chain diverge completely -- measured on 2024: the engine fills
  649 trades and the framework opens 0, with 650 SOURCE_STAKE_VETO lines
  (`required=1.00000000`, `min_stake=4.759923`). The source's own sizing is the
  cause, not the port: closing the gap would mean overriding a declared source
  property, which the iron rules forbid.
* `ta.sma(close, 50)` is na until bar 49, and `na > x` / `na < x` compare
  false, so no signal is possible before then; `pine_ta.pine_sma` gives exactly
  that warmup.
* `na(min_distance) or array.get(distances, j) < min_distance` is transcribed
  as written, including the `na` test on the FIRST scan only.
* The `var float[] features = na` / `distances = na` / `nearest_neighbors = na`
  initializers are never read: every path assigns them with `:=` before use,
  and the signal block sits inside the `bar_index >= window_size - 1` gate.
* `array.remove` is Pine's positional removal; the port's `del distances[j]`
  is the same operation, and it is what makes the min-scan shift indices after
  each selection.
* `currency='USD'` and contract-step rounding are not modelled
  (PINE_SEMANTICS.md 2.4, 2.6).
* There is no stop, limit, trail or `strategy.exit` in the source, so
  `source_reproduce_stops` is False; a position is only ever changed by the
  opposite entry reversing it, and a same-direction repeat is refused by
  `pyramiding 0`.
* The md's "自适应参数化" (adaptive parametrization) and its KNN-distance prose
  describe an intent the code does not realize -- the distances are all zero,
  as shown above. Recorded, not corrected.
* Leverage, margin, liquidation and funding are not modelled.
"""
from __future__ import annotations

import math

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKnnAdaptiveParametric_d7c50b(PinePortBase, IStrategy):
    source_id = "SM_d7c50b8bbc3f20d7"
    source_file = (
        "KNN自适应参数化趋势跟踪策略"
        "-KNN-Based-Adaptive-Parametric-Trend-Following-Strategy.md"
    )
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"k": 5, "window_size": 20, "ma_length": 50}
    source_qty_type = "cash"
    # default_qty_value is not declared by the source -> Pine's documented
    # default of 1, i.e. one unit of the quote currency per entry.
    source_qty_value = 1.0
    source_commission_percent = 0.03
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source's KNN is degenerate: `features` is rebuilt every bar from "
        "the current bar's own history, so `close[j] - features[j]` is 0 and "
        "every element of `distances` is sqrt(0). nearest_neighbors is "
        "[0,0,0,0,0] on every bar. Reproduced literally rather than corrected.",
        "`var` lifetime is the load-bearing modelling choice: a var is "
        "initialized ONCE and persists across bars and across loop iterations, "
        "so `var float average_change` accumulates as "
        "average_change[i] = average_change[i-1]/k + (close - close[1]) "
        "instead of resetting to the one-bar change each bar. Pine's "
        "documented `var` semantics; the alternative per-iteration reading is "
        "recorded as the residual equivalence risk.",
        "`var int index = array.get(nearest_neighbors, i)` is likewise "
        "initialized once (to 0) and never re-assigned, so all k additions in "
        "the average are the same term.",
        "`var float distance = 0.0` is never reset, and its increments are all "
        "zero, so it stays 0.0 and each pushed distance is sqrt(0).",
        "default_qty_value is undeclared -> Pine's documented default 1 with "
        "qty_type=cash: one US dollar of notional per entry, far below the "
        "venue's minimum order size. That is the source's own declaration, not "
        "a port choice.",
        "commission_value=0.03 with commission_type=percent -> 0.03%.",
        "initial_capital is undeclared -> Pine's documented default 1000000.",
        "ta.sma(close, 50) is na for the first 49 bars and na comparisons are "
        "false, so no signal is possible before then.",
        "No stop/limit/trail/strategy.exit exists, so source_reproduce_stops "
        "is False; pyramiding 0 refuses a same-direction repeat and the "
        "opposite entry reverses.",
        "The md's adaptive-parameterisation and KNN-distance prose describes "
        "an intent the code does not realise; recorded, not corrected.",
        "currency='USD' is not modelled, and neither are leverage, margin, "
        "liquidation, funding or contract-step rounding.",
    ]

    def pine_indicators(self, dataframe, params):
        k = int(params["k"])
        window = int(params["window_size"])
        ma_length = int(params["ma_length"])

        close_series = dataframe["close"]
        close = close_series.to_numpy(dtype=float)
        bars = len(close)
        # ma = ta.sma(close, ma_length)
        ma = ta.pine_sma(close_series, ma_length).to_numpy(dtype=float)

        average_change = np.full(bars, np.nan)

        # ---- Pine `var` scalars: initialized once, then carried -------------
        # Each is None until the bar on which its declaration is first reached.
        distance = None          # var float distance = 0.0
        min_index = None         # var int   min_index = -1
        min_distance = None      # var float min_distance = na
        neighbor_index = None    # var int   index = array.get(nearest_neighbors, i)
        running_change = None    # var float average_change = 0.0

        for i in range(bars):
            if i < window - 1:  # if bar_index >= window_size - 1
                continue
            if distance is None:
                distance = 0.0
            # features := array.new_float(0); push close[i] for i = 0..window-1
            features = [close[i - j] for j in range(window)]

            # distances := array.new_float(0)
            distances: list[float] = []
            for _ in range(window):
                for j in range(window):
                    distance += (close[i - j] - features[j]) ** 2
                distance = math.sqrt(distance)
                distances.append(distance)

            # Nearest neighbours, with min_index / min_distance keeping their
            # `var` values across iterations and bars.
            nearest: list[int] = []
            if len(distances) > 0 and len(distances) >= k:
                nearest = []
                if min_index is None:
                    min_index = -1
                if min_distance is None:
                    min_distance = float("nan")
                for _ in range(k):
                    for j in range(len(distances)):
                        if math.isnan(min_distance) or distances[j] < min_distance:
                            min_index = j
                            min_distance = distances[j]
                    if min_index != -1:
                        nearest.append(min_index)
                        del distances[min_index]

            if running_change is None:
                running_change = 0.0
            if len(nearest) > 0:
                for t in range(len(nearest)):
                    if neighbor_index is None:
                        neighbor_index = nearest[t]
                    if neighbor_index + 1 < i:
                        running_change += (
                            close[i - neighbor_index] - close[i - neighbor_index - 1]
                        )
                running_change = running_change / len(nearest)
            average_change[i] = running_change

        # if average_change > 0 and close > ma / else if average_change < 0 and
        # close < ma -- na compares false on both sides.
        long_signal = (average_change > 0) & (close > ma)
        short_signal = (average_change < 0) & (close < ma)

        dataframe["pine_ma"] = ma
        dataframe["pine_average_change"] = average_change
        dataframe["pine_long_signal"] = long_signal
        dataframe["pine_short_signal"] = short_signal
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_signal": dataframe["pine_long_signal"].to_numpy(),
            "short_signal": dataframe["pine_short_signal"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if average_change > 0 and close > ma
        #     strategy.entry("Long", strategy.long)
        # else if average_change < 0 and close < ma
        #     strategy.entry("Short", strategy.short)
        if ctx["long_signal"][i]:
            broker.entry("Long", "long")
        elif ctx["short_signal"][i]:
            broker.entry("Short", "short")
