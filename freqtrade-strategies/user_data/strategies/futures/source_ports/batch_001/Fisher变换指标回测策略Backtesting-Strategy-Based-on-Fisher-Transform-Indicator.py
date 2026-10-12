"""Port of sources/SM_38e1dbcf7e3ee10d.pine (batch_001/Fisher变换指标回测策略Backtesting-Strategy-Based-on-Fisher-Transform-Indicator.md).

Pine v2, Ehlers' Fisher Transform as published by HPotter. The source is an
always-in-the-market sign follower on a recursive Fisher series:

    xHL2   = hl2
    xMaxH  = highest(xHL2, Length)
    xMinL  = lowest(xHL2, Length)
    nValue1 = 0.33 * 2 * ((xHL2 - xMinL)/(xMaxH - xMinL) - 0.5) + 0.67 * nz(nValue1[1])
    nValue2 = iff(nValue1 >  .99,  .999,
              iff(nValue1 < -.99, -.999, nValue1))
    nFish   = 0.5 * log((1 + nValue2)/(1 - nValue2)) + 0.5 * nz(nFish[1])
    pos     = iff(nFish > 0, 1, iff(nFish < 0, -1, nz(pos[1], 0)))
    possig  = iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))

    if possig == 1
        strategy.entry("Long", strategy.long)
    if possig == -1
        strategy.entry("Short", strategy.short)

`strategy()` declares only `title` / `shorttitle`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither
`strategy.entry` passes `qty`, so the default quantity supplies it.

Both `if` blocks are evaluated independently on every bar (the source does not
use `else if`). `pos` is single-valued, so the two can never both be true, but
the ORDER (Long then Short) is kept in the port as written.

FIDELITY:

* `nValue1`, `nFish` and `pos` are recursive -- each bar reads its own previous
  value through `nz(...[1], 0/na)`. They are carried by an explicit bar loop,
  not by a vectorised substitute, because the `nz` default differs per series
  and applying the wrong one silently changes the whole history.
* `nz()` in Pine is `na(x) ? replacement : x`; here `nz(nValue1[1])` and
  `nz(nFish[1])` default to 0 while `nz(pos[1], 0)` is written out with its
  explicit 0. All three are reproduced with their own default.
* A degenerate window (`xMaxH == xMinL`) makes the source divide by zero. Pine
  returns `na` for float division by zero, so the port yields `na` there rather
  than the inf/nan pandas would produce, and the `na` then propagates through
  `nValue2` and `nFish` exactly as it does in Pine.
* `highest`/`lowest` return na until the window is full, so the first non-na
  `nFish` is on bar `Length - 1` and `pos` is 0 before that (the `nz(pos[1], 0)`
  branch). No entry can fire before then.
* `nFish == 0` exactly has no sign test of its own -- it falls through to
  `nz(pos[1], 0)` and HOLDS the previous sign. Reproduced as a hold, not as a
  flat/neutral state.
* `reverse` is a `bool` input used in a logical context (`reverse and pos == 1`),
  never in a numeric one, so the PINE_SEMANTICS.md 1.16 trap does not apply here
  and the literal translation is correct.
* `plot` calls and the `barcolor` line (already commented out in the source) are
  display-only and place no condition. The `Trigger` plot (`nz(nFish[1])`) is
  reproduced as a column and never read.
* Entries carry no `qty`, no `stop` and no `limit`, and the source has no
  `strategy.close` / `strategy.exit`, so `source_reproduce_stops` is False and
  the only exits are the reverse entries.
* `1 + nValue2` / `1 - nValue2` cannot reach zero: `nValue2` is clamped into
  [-0.999, 0.999] before the log.
* `reverse` defaults to False, so `possig == pos` in the shipped configuration;
  the reversal branch is still implemented because the input exists.
* The md's argument table and prose add nothing the code does not say; no
  md/source disagreement was found for this source.
* Leverage, margin, liquidation, funding, and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFisherTransformEhlers_38e1db(PinePortBase, IStrategy):
    source_id = "SM_38e1dbcf7e3ee10d"
    source_file = "Fisher变换指标回测策略Backtesting-Strategy-Based-on-Fisher-Transform-Indicator.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"Length": 10, "reverse": False}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "nValue1 / nFish / pos are recursive (each bar reads its own `[1]` "
        "through `nz`). They are carried by an explicit bar loop so that every "
        "`nz` default (0 for nValue1 and nFish, 0 for pos) is applied to the "
        "right series; a vectorised rewrite would silently drop the recursion.",
        "A degenerate window (xMaxH == xMinL) makes the source divide by zero. "
        "Pine returns na for float division by zero, so the port yields na "
        "there and lets it propagate through nValue2 / nFish as Pine does, "
        "instead of producing inf/nan.",
        "nFish == 0 exactly falls through both sign tests to `nz(pos[1], 0)`, "
        "i.e. it HOLDS the previous sign. Reproduced as a hold, not as flat.",
        "`reverse` is a bool input used only in a logical context "
        "(`reverse and pos == 1`), not in a numeric one, so PINE_SEMANTICS.md "
        "1.16 does not apply and the literal translation is correct.",
        "highest/lowest return na until the window is full, so pos is 0 until "
        "bar Length-1 and no entry can fire before then.",
        "The source has no strategy.close / strategy.exit and neither entry "
        "carries a stop or limit, so source_reproduce_stops is False and the "
        "only exit is the reverse entry.",
        "`plot`/`barcolor` are display-only; the `Trigger` plot (nz(nFish[1])) "
        "is computed as a column and never read by the script.",
        "reverse defaults to False, so possig == pos in the shipped "
        "configuration; the reversal branch is still implemented because the "
        "input exists.",
        "The md and the source agree line for line; no md/source disagreement.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["Length"])
        reverse = bool(params["reverse"])

        hl2 = ta.pine_source(dataframe, "hl2")
        # xMaxH / xMinL are rolling extremes of hl2 over the same window.
        x_max = ta.pine_highest(hl2, length).to_numpy(dtype=float)
        x_min = ta.pine_lowest(hl2, length).to_numpy(dtype=float)
        mid = hl2.to_numpy(dtype=float)

        count = len(mid)
        value1 = np.full(count, np.nan)
        value2 = np.full(count, np.nan)
        fish = np.full(count, np.nan)
        pos = np.full(count, np.nan)
        possig = np.full(count, np.nan)

        previous_value1 = np.nan
        previous_fish = np.nan
        previous_pos = np.nan
        for i in range(count):
            span = x_max[i] - x_min[i]
            if np.isnan(span) or span == 0.0:
                # Pine: na window, or float division by zero -> na.
                current = np.nan
            else:
                current = (
                    0.33 * 2.0 * ((mid[i] - x_min[i]) / span - 0.5)
                    + 0.67 * (0.0 if np.isnan(previous_value1) else previous_value1)
                )
            value1[i] = current

            # nValue2 = iff(nValue1 > .99, .999, iff(nValue1 < -.99, -.999, nValue1))
            if not np.isnan(current) and current > 0.99:
                clipped = 0.999
            elif not np.isnan(current) and current < -0.99:
                clipped = -0.999
            else:
                clipped = current
            value2[i] = clipped

            # nFish = 0.5*log((1+nValue2)/(1-nValue2)) + 0.5*nz(nFish[1])
            if np.isnan(clipped):
                n_fish = np.nan
            else:
                n_fish = (
                    0.5 * np.log((1.0 + clipped) / (1.0 - clipped))
                    + 0.5 * (0.0 if np.isnan(previous_fish) else previous_fish)
                )
            fish[i] = n_fish

            # pos = iff(nFish > 0, 1, iff(nFish < 0, -1, nz(pos[1], 0)))
            if not np.isnan(n_fish) and n_fish > 0:
                sign = 1.0
            elif not np.isnan(n_fish) and n_fish < 0:
                sign = -1.0
            else:
                sign = 0.0 if np.isnan(previous_pos) else previous_pos
            pos[i] = sign

            # possig = iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))
            if reverse and sign == 1:
                signal = -1.0
            elif reverse and sign == -1:
                signal = 1.0
            else:
                signal = sign
            possig[i] = signal

            previous_value1 = current
            previous_fish = n_fish
            previous_pos = sign

        dataframe["pine_fisher_value1"] = value1
        dataframe["pine_fisher_value2"] = value2
        dataframe["pine_fisher"] = fish
        # plot(nz(nFish[1]), color=red, title="Trigger") -- display-only.
        dataframe["pine_fisher_trigger"] = pd.Series(fish, index=dataframe.index).shift(1).fillna(0.0)
        dataframe["pine_fisher_pos"] = pos
        dataframe["pine_fisher_possig"] = possig
        return dataframe

    def pine_context(self, dataframe, params):
        return {"possig": dataframe["pine_fisher_possig"].to_numpy(dtype=float)}

    def pine_script(self, broker, i, ctx):
        # if (possig == 1) strategy.entry("Long", strategy.long)
        # if (possig == -1) strategy.entry("Short", strategy.short)
        # Two independent `if`s in the source; possig is single-valued so at
        # most one fires, but the written order is kept.
        if ctx["possig"][i] == 1:
            broker.entry("Long", "long")
        if ctx["possig"][i] == -1:
            broker.entry("Short", "short")
