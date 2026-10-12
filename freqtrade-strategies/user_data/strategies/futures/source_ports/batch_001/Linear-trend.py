"""Port of sources/SM_37d3208454848ad6.pine (batch_001/Linear-trend.md).

Pine v4. A least-squares regression line with a dispersion channel around it,
plus a three-state trend ratchet that selects which channel edge is the
reversal line:

    c  = input(close)                 // source input, default close
    len = input(200, minval=1)
    off = 0
    dev = input(4, "Deviation")
    lreg   = linreg(c, len, off)
    lreg_x = linreg(c, len, off + 1)
    b = bar_index
    s = lreg - lreg_x
    intr = lreg - b*s
    dS = 0.0
    for i = 0 to len-1
        dS := dS + pow(c[i] - (s*(b-i) + intr), 2)
    de   = sqrt(dS/len)
    up   = (-de*dev) + lreg
    down = ( de*dev) + lreg
    up_t   := c[1] >  up_t[1]   ? max(up,   up_t[1])   : up
    down_t := c[1] <  down_t[1] ? min(down, down_t[1]) : down
    trend  := c > down_t[1] ? 1 : c < up_t[1] ? -1 : nz(trend[1], 1)
    r_line = trend == 1 ? up_t : down_t
    buy  = crossover(c, r_line)
    sell = crossunder(c, r_line)
    if buy
        strategy.entry("long", strategy.long)
    else if sell
        strategy.entry("short", strategy.short)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it. The `if buy ... else if sell`
form means a bar satisfying both would take the long branch only; in practice
they are mutually exclusive.

FIDELITY:

* `de` is NOT a standard deviation. The source divides the residual sum of
  squares by `len` (not `len-1`, and with no mean subtraction -- the regression
  already removes the mean), so it is the RMS residual. Reproduced from the
  source formula, not from `stdev`.
* The regression is computed with `pine_ta.pine_linreg`, which is Pine v4's
  `linreg(source, length, offset)` -- the least-squares value `offset` bars back
  from the end of the window.
* `intr = lreg - b*s` uses the GLOBAL `bar_index`, but the loop's fitted value
  `s*(b-i) + intr` collapses algebraically to `lreg - s*i`, so `bar_index` never
  has to be materialised: the residual is a function of the window only. The
  port keeps that identity (and the original formula is quoted above).
* The loop's `pow(c[i] - ..., 2)` propagates na: any missing bar inside the
  window makes `dS` na, hence `de`, `up` and `down`. The port keeps an explicit
  `complete` mask so na propagates exactly; `nan_to_num` is used only on the
  additive accumulator that the mask already neutralises.
* `up_t` / `down_t` / `trend` are recursive and seeded from na on bar 0, NOT
  from their `= 0.0` / `= 0` initialisers: Pine's `[1]` on the first bar reads
  na, so the first evaluation takes the `else` branch. The port therefore starts
  with `previous_* = nan`, which makes `nz(trend[1], 1)` resolve to 1 on bar 0
  exactly as Pine does.
* Pine's `max(na, x)` and `min(na, x)` return na, and a comparison against na is
  false. The port guards each ratchet branch on both operands being finite, so a
  na `up`/`down` falls through to the `else` branch (assigning that na) instead
  of being silently dropped.
* `bar_index` is supplied by the engine's own bar counter, which is the same
  integer Pine exposes.
* The md's argument table lists exactly the three inputs the source declares
  (`c`, `len`, `Deviation`); `off` is a literal, not an input, so it is absent
  from `source_defaults`. No md/source disagreement was found.
* `alertcondition` and `plotshape` are display-only and place no condition.
* No `strategy.close` / `strategy.exit` / `stop` / `limit` exists, so
  `source_reproduce_stops` is False and the only exits are the reverse entries.
  Both directions are entered, so `can_short` is True.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMLinearTrend_37d320(PinePortBase, IStrategy):
    source_id = "SM_37d3208454848ad6"
    source_file = "Linear-trend.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {"c": "close", "len": 200, "dev": 4}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`de = sqrt(dS/len)` is the RMS residual, not a standard deviation: the "
        "source divides by `len` (not len-1) with no mean subtraction, because "
        "the regression has already removed the mean. Implemented from the "
        "source formula, not from pine_stdev.",
        "The loop residual `c[i] - (s*(b-i) + intr)` collapses algebraically to "
        "`c[i] - (lreg - s*i)` because `intr = lreg - b*s`, so the global "
        "`bar_index` cancels out. The port uses the collapsed form; the original "
        "formula is quoted in the module docstring.",
        "na inside the 200-bar window makes dS (and therefore de / up / down) "
        "na. An explicit `complete` mask reproduces that propagation.",
        "up_t / down_t / trend are recursive and read `[1]` as na on bar 0 -- the "
        "`= 0.0` / `= 0` initialisers are NOT what `[1]` returns -- so the first "
        "bar takes the else branch and nz(trend[1], 1) yields 1. The port seeds "
        "its previous-values with nan to match.",
        "Pine's max(na, x) / min(na, x) are na and comparisons against na are "
        "false; each ratchet branch is guarded on both operands being finite so "
        "a na up/down assigns na through the else branch instead of being "
        "dropped.",
        "off = 0 is a literal in the source, not an input(), so it is not in "
        "source_defaults; the md's argument table lists only c, len, Deviation.",
        "alertcondition / plotshape are display-only and place no condition.",
        "No strategy.close / strategy.exit / stop / limit exists, so "
        "source_reproduce_stops is False; both directions are entered, so "
        "can_short is True.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["len"])
        deviation = float(params["dev"])
        source = ta.pine_source(dataframe, params["c"])
        source_values = source.to_numpy(dtype=float)
        count = len(source_values)

        lreg = ta.pine_linreg(source, length, 0).to_numpy(dtype=float)
        lreg_x = ta.pine_linreg(source, length, 1).to_numpy(dtype=float)
        slope = lreg - lreg_x

        # dS = for i = 0 to len-1: dS + pow(c[i] - (s*(b-i) + intr), 2)
        total = np.zeros(count)
        complete = np.ones(count, dtype=bool)
        for lag in range(length):
            shifted = np.full(count, np.nan)
            if lag < count:
                # c[i] with i == lag is only defined once the frame is that long.
                shifted[lag:] = source_values[: count - lag]
            residual = shifted - (lreg - slope * lag)
            complete &= ~np.isnan(residual)
            total += np.nan_to_num(residual ** 2, nan=0.0, posinf=0.0, neginf=0.0)
        de = np.where(complete, np.sqrt(total / length), np.nan)

        up = (-de * deviation) + lreg
        down = (de * deviation) + lreg

        up_t = np.full(count, np.nan)
        down_t = np.full(count, np.nan)
        trend = np.full(count, np.nan)
        previous_up_t = np.nan
        previous_down_t = np.nan
        previous_trend = np.nan
        for i in range(count):
            close_previous = source_values[i - 1] if i >= 1 else np.nan

            # up_t := c[1] > up_t[1] ? max(up, up_t[1]) : up
            if (
                np.isfinite(close_previous)
                and np.isfinite(previous_up_t)
                and np.isfinite(up[i])
                and close_previous > previous_up_t
            ):
                up_t[i] = max(up[i], previous_up_t)
            else:
                up_t[i] = up[i]

            # down_t := c[1] < down_t[1] ? min(down, down_t[1]) : down
            if (
                np.isfinite(close_previous)
                and np.isfinite(previous_down_t)
                and np.isfinite(down[i])
                and close_previous < previous_down_t
            ):
                down_t[i] = min(down[i], previous_down_t)
            else:
                down_t[i] = down[i]

            # trend := c > down_t[1] ? 1 : c < up_t[1] ? -1 : nz(trend[1], 1)
            if (
                np.isfinite(source_values[i])
                and np.isfinite(previous_down_t)
                and source_values[i] > previous_down_t
            ):
                state = 1.0
            elif (
                np.isfinite(source_values[i])
                and np.isfinite(previous_up_t)
                and source_values[i] < previous_up_t
            ):
                state = -1.0
            else:
                state = 1.0 if np.isnan(previous_trend) else previous_trend
            trend[i] = state

            previous_up_t = up_t[i]
            previous_down_t = down_t[i]
            previous_trend = state

        r_line = np.where(trend == 1, up_t, down_t)
        dataframe["pine_lreg"] = lreg
        dataframe["pine_lreg_prev"] = lreg_x
        dataframe["pine_linreg_de"] = de
        dataframe["pine_linreg_up"] = up
        dataframe["pine_linreg_down"] = down
        dataframe["pine_linreg_up_t"] = up_t
        dataframe["pine_linreg_down_t"] = down_t
        dataframe["pine_linreg_trend"] = trend
        dataframe["pine_linreg_line"] = r_line
        line = dataframe["pine_linreg_line"]
        dataframe["pine_linreg_buy"] = ta.pine_crossover(source, line)
        dataframe["pine_linreg_sell"] = ta.pine_crossunder(source, line)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy": dataframe["pine_linreg_buy"].to_numpy(dtype=bool),
            "sell": dataframe["pine_linreg_sell"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if buy -> strategy.entry("long", strategy.long)
        # else if sell -> strategy.entry("short", strategy.short)
        if ctx["buy"][i]:
            broker.entry("long", "long")
        elif ctx["sell"][i]:
            broker.entry("short", "short")
