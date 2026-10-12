"""Port of sources/SM_3e110f1d73262011.pine (batch_001/Directional-Movement-Oscillator-DMI.md).

Pine v4. A DI oscillator and its SMA:

    len = 10, avlength = 8
    up         = change(high)                       # high - high[1]
    down       = -change(low)                       # -(low - low[1])
    truerange  = rma(tr, len)
    plus       = fixnan(100 * rma(up > down and up > 0 ? up : 0, len) / truerange)
    minus      = fixnan(100 * rma(down > up and down > 0 ? down : 0, len) / truerange)
    diosc      = plus - minus
    signal     = sma(diosc, avlength)

and the order block appended at the end of the file:

    if diosc
       strategy.entry("buy", strategy.long)
    else if p2
        strategy.entry("sell", strategy.short)

No exit call exists anywhere (see FIDELITY on the two plots used as conditions).

The file declares `study(...)`, not `strategy(...)` (PINE_SEMANTICS.md 1.17),
so no strategy() properties exist: Pine's documented defaults are recorded in
the source_* attributes -- fixed 1-unit sizing, 0% commission, pyramiding 0,
initial capital 1000000 USD.

FIDELITY:

* `if diosc` is a TRUTHINESS test on a float, not a comparison: Pine (and
  Python) call any non-zero, non-na value true -- `-1` included. It is
  reproduced verbatim as "not na and != 0", never rewritten as `diosc > 0`,
  which would silently drop every bar where the oscillator is negative
  (PINE_SEMANTICS.md 1.17).
* `p2` is the id returned by `p2 = plot(signal, ...)`. Pine v4 gives a plot id,
  not a bool, so `else if p2` has no documented meaning and would not compile on
  TradingView; it is a converter artefact. It is modelled here as the truthiness
  of the series that plot draws -- `signal` -- because that is the only reading
  under which the identifier names something with a value. This is an
  unresolved equivalence risk, not a verified reproduction (see also the
  funnel note below, which bounds the damage).
* That funnel: `if diosc` is tested FIRST, and `diosc` is a DI difference that
  is non-zero on essentially every bar, so the `else if` is reached only on bars
  where diosc is exactly 0 or na. Under either reading of `p2` the short branch
  is therefore a rare event and the port's trades are dominated by the long
  branch; the two readings differ only on those rare bars.
* `fixnan(x)` is Pine v4's "replace na with the most recent non-na value", i.e.
  a forward fill that leaves the leading na run in place. pine_ta has no
  fixnan, so it is implemented here as `.ffill()`.
* `tr` is the v4 builtin: na on the first bar (no previous close), while
  pine_ta.pine_tr returns `high - low` there (PINE_SEMANTICS.md 3.7). Bar 0 is
  masked to na so `rma(tr, len)` seeds one bar later, as Pine's does -- the
  seeding point is what shifts the whole truerange series.
* `up > down and up > 0 ? up : 0`: Pine treats an na comparison as false and an
  na condition as the FALSE branch, so the first bar contributes 0, not na. The
  columns fed to `rma` are therefore never na and the rma seeds on its first
  `len` bars; the port builds the mask with na-as-false.
* `x / 0 -> na` in Pine, so the division by truerange is taken with a zero
  denominator replaced by na rather than by numpy's inf.
* `plot`, `fill` and the `transp` arguments are display-only and place no order.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series):
    """Pine v4 `fixnan`: na takes the most recent non-na value.

    The leading na run has nothing to take, so it stays na, exactly as Pine's
    fixnan leaves it.
    """
    return series.ffill()


def _pine_divide(numerator, denominator):
    """Pine's `/`: a zero denominator yields na, not numpy's infinity."""
    return numerator / denominator.replace(0.0, np.nan)


class SMDirectionalMovementOscillatorDmi_3e110f(PinePortBase, IStrategy):
    source_id = "SM_3e110f1d73262011"
    source_file = "Directional-Movement-Oscillator-DMI.md"
    timeframe = "4h"
    can_short = True
    source_defaults = {
        "len": 10,        # input(10, title="DI Length")
        "avlength": 8,    # input(8, title="DI Smoothing Length")
    }
    # study(...) carries no strategy() properties, so Pine's documented
    # defaults apply: fixed 1 unit, 0% commission, pyramiding 0, capital 1000000.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares `study(...)`, not `strategy(...)`: the original "
        "behaviour is the indicator plus the order block the converter appended "
        "at the end of the file (PINE_SEMANTICS.md 1.17). There is no exit call "
        "of any kind, so a position is only left by the opposite entry reversing "
        "it; source_reproduce_stops is False and a position open at the end of "
        "the window stays open.",
        "`if diosc` is a truthiness test on a float: non-zero and non-na is true, "
        "negative values included. It is kept as-is and NOT rewritten as "
        "`diosc > 0` -- that rewrite would silently delete every short-period "
        "bar the source trades (PINE_SEMANTICS.md 1.17).",
        "`else if p2` reads the id returned by `p2 = plot(signal, ...)`. A Pine v4 "
        "plot id is not a boolean and has no documented truthiness, so this is a "
        "converter artefact that would not compile on TradingView. It is modelled "
        "as the truthiness of the plotted series `signal` (non-zero, non-na). "
        "UNRESOLVED equivalence risk -- but see the next note for its extent.",
        "The `else if` is only reached when diosc is exactly 0 or na, because "
        "`if diosc` is tested first and a DI difference is non-zero on almost "
        "every bar. Both candidate readings of p2 (the plotted series, or an "
        "always-truthy handle) therefore place the short branch on the same tiny "
        "set of bars, differing only there.",
        "`fixnan` is not exposed by pine_ta; it is implemented in this file as a "
        "forward fill that leaves the leading na run in place, which is what Pine "
        "v4's fixnan does.",
        "`tr` is the v4 builtin and is na on the first bar (no previous close); "
        "pine_ta.pine_tr returns high - low there (PINE_SEMANTICS.md 3.7), so bar "
        "0 is masked to na and `rma(tr, len)` seeds one bar later, as Pine's does.",
        "The columns fed to `rma` are never na: `na` in a Pine comparison is "
        "false and na in a ternary condition takes the FALSE branch, so the first "
        "bar contributes 0.",
        "Pine's division by zero yields na, so a zero truerange is replaced by na "
        "rather than numpy's infinity (unreachable on real bars; kept exact).",
        "plot / fill / transp are display-only and place no order.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["len"])
        smooth = int(params["avlength"])
        high, low = dataframe["high"], dataframe["low"]

        # up = change(high); down = -change(low)
        up = ta.pine_change(high)
        down = -ta.pine_change(low)

        # truerange = rma(tr, len) -- `tr` is na on the first bar (Pine), so the
        # rma's seeding point is bar `len`, one later than pine_ta's default.
        true_range = ta.pine_tr(dataframe, handle_na=False)
        true_range.iloc[0] = np.nan
        truerange = ta.pine_rma(true_range, length)

        # up > down and up > 0 ? up : 0  (na comparison -> false -> 0)
        up_mask = ((up > down) & (up > 0)).fillna(False)
        down_mask = ((down > up) & (down > 0)).fillna(False)
        plus_series = ta.pine_rma(up.where(up_mask, 0.0), length)
        minus_series = ta.pine_rma(down.where(down_mask, 0.0), length)

        plus = _fixnan(_pine_divide(100.0 * plus_series, truerange))
        minus = _fixnan(_pine_divide(100.0 * minus_series, truerange))
        diosc = plus - minus
        signal = ta.pine_sma(diosc, smooth)

        dataframe["pine_diosc"] = diosc
        dataframe["pine_signal"] = signal
        # `if diosc` / `else if p2`: truthiness of the float and of the plotted
        # series -- non-zero AND non-na, negative values included.
        dataframe["pine_long_condition"] = diosc.notna() & (diosc != 0.0)
        dataframe["pine_short_condition"] = signal.notna() & (signal != 0.0)
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if diosc
        #    strategy.entry("buy", strategy.long)
        # else if p2
        #     strategy.entry("sell", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("buy", "long")
        elif ctx["short_condition"][i]:
            broker.entry("sell", "short")
