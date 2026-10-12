"""Port of sources/SM_b54c457253fccf33.pine (batch_001/Fisher变换指标回测策略Fisher-Transform-Backtest-Strategy.md).

Pine v2, Ehlers' Fisher Transform as republished by HPotter. The order logic is
an always-in-the-market sign follower on a recursive Fisher series:

    Length  = input(10, minval=1)
    reverse = input(false, title="Trade reverse")
    hline(0, color=blue)

    xHL2    = hl2
    xMaxH   = highest(xHL2, Length)
    xMinL   = lowest(xHL2, Length)
    nValue1 = 0.33 * 2 * ((xHL2 - xMinL) / (xMaxH - xMinL) - 0.5) + 0.67 * nz(nValue1[1])
    nValue2 = iff(nValue1 >  .99,  .999,
              iff(nValue1 < -.99, -.999, nValue1))
    nFish   = 0.5 * log((1 + nValue2) / (1 - nValue2)) + 0.5 * nz(nFish[1])
    pos     = iff(nFish > 0, 1,
              iff(nFish < 0, -1, nz(pos[1], 0)))
    possig  = iff(reverse and pos == 1, -1,
              iff(reverse and pos == -1, 1, pos))

    if (possig == 1)
        strategy.entry("Long", strategy.long)
    if (possig == -1)
        strategy.entry("Short", strategy.short)

`strategy()` declares only `title` / `shorttitle`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, `pyramiding 0`, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it. The two `if` blocks are
independent (the source does not use `else if`) and are kept in their written
order; `pos` is single-valued so they can never both fire.

The `/*backtest` header declares `period: 1h` on Futures_Binance BTC_USDT, so
`timeframe` is "1h"; its `basePeriod: 15m` is the backtester's own fill
granularity for those bars, not the strategy's period.

There is no `strategy.close` / `strategy.exit` and no stop or limit anywhere in
the source, so `source_reproduce_stops` is False: a position is only closed by
the opposite entry reversing it, and a position open at the end of the window
stays open.

FIDELITY:

* `nValue1`, `nFish` and `pos` are RECURSIVE -- each bar reads its own previous
  value through `nz(...[1])`. They are carried by an explicit bar loop rather
  than a vectorised substitute, because the three `nz` defaults differ per
  series and applying the wrong one silently changes the whole history.
* `nz(x)` in Pine is `na(x) ? replacement : x` with replacement defaulting to 0.
  `nz(nValue1[1])` and `nz(nFish[1])` therefore default to 0 while `nz(pos[1], 0)`
  spells its 0 out; all three are reproduced with their own default.
* A degenerate window (`xMaxH == xMinL`) makes the source divide by zero. The
  port yields na there (Pine's float-division-by-zero result) instead of letting
  an inf/nan escape, and the na propagates through `nValue2` / `nFish` exactly as
  in Pine.
* `highest` / `lowest` return na until their window is full and na inside the
  window propagates, which is the shared layer's documented reading of Pine's
  windowed builtins (PINE_SEMANTICS.md 3.2). The first non-na `nFish` is
  therefore on bar `Length - 1`, and `pos` is the `nz(pos[1], 0)` branch (0)
  before that -- no entry can fire earlier.
* `nFish == 0` exactly has no sign test of its own: it falls through to
  `nz(pos[1], 0)` and HOLDS the previous sign. Reproduced as a hold, not as a
  flat/neutral state.
* `reverse` is a `bool` input used only in a logical context (`reverse and
  pos == 1`), never in a numeric one, so the PINE_SEMANTICS.md 1.16 trap
  (`bool` compared as a number) does not apply and the literal translation is
  correct.
* `hline(0)`, the two `plot` calls and `barcolor` are display-only and place no
  condition. `plot(nz(nFish[1]), title="Trigger")` is carried as a column and is
  never read by the order logic.
* `reverse` defaults to False, so `possig == pos` in the shipped configuration;
  the reversal branch is still implemented because the input exists.
* The md reproduces the source verbatim (same text, same arguments table:
  `v_input_1 = 10` Length, `v_input_2 = false` Trade reverse); no md/source
  disagreement was found for this source.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately rather
  than treating it as a signal difference.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFisherTransformBacktest_b54c45(PinePortBase, IStrategy):
    source_id = "SM_b54c457253fccf33"
    source_file = "Fisher变换指标回测策略Fisher-Transform-Backtest-Strategy.md"
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
        "nValue1 / nFish / pos are recursive: every bar reads its own `[1]` "
        "through `nz`. They are carried by an explicit bar loop so each `nz` "
        "default (0 for nValue1, 0 for nFish, 0 for pos) is applied to the "
        "series that wrote it; a vectorised rewrite would drop the recursion.",
        "A degenerate window (xMaxH == xMinL) makes the source divide by zero; "
        "the port yields na there (Pine's float-division-by-zero result) and "
        "lets it propagate through nValue2 / nFish, rather than emitting inf.",
        "nFish == 0 exactly falls through both sign tests to `nz(pos[1], 0)`, "
        "i.e. it HOLDS the previous sign. Reproduced as a hold, not as flat.",
        "highest / lowest return na until the window is full (and na inside the "
        "window propagates), so pos is 0 until bar Length-1 and no entry can "
        "fire before then (PINE_SEMANTICS.md 3.2 records this as the layer's "
        "reading of Pine's windowed builtins, not as certified equivalence).",
        "`reverse` is a bool input used only in a logical context "
        "(`reverse and pos == 1`), never numerically, so the "
        "PINE_SEMANTICS.md 1.16 trap does not apply and the literal "
        "translation is correct.",
        "The source has no strategy.close / strategy.exit and neither entry "
        "carries a stop or limit, so source_reproduce_stops is False and the "
        "only exit is the opposite entry reversing the position.",
        "hline / plot / barcolor are display-only; the `Trigger` plot "
        "(nz(nFish[1])) is computed as a column and never read by the script.",
        "reverse defaults to False, so possig == pos in the shipped "
        "configuration; the reversal branch is implemented because the input "
        "exists.",
        "The md reproduces this source verbatim (same code, same arguments "
        "table); no md/source disagreement.",
        "ta.ema is not used here, but the layer's na handling (na does not "
        "advance a smoothing step) is the same choice recorded in "
        "PINE_SEMANTICS.md 3.1 for the seeds it does affect.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["Length"])
        reverse = bool(params["reverse"])

        hl2 = ta.pine_source(dataframe, "hl2")
        # xMaxH / xMinL: rolling extremes of hl2 over the same Length window.
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
                # na window, or Pine's float division by zero -> na.
                current = np.nan
            else:
                # nValue1 = 0.33*2*((xHL2 - xMinL)/(xMaxH - xMinL) - 0.5)
                #           + 0.67*nz(nValue1[1])
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

            # possig = iff(reverse and pos == 1, -1,
            #          iff(reverse and pos == -1, 1, pos))
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
        dataframe["pine_fisher_trigger"] = (
            pd.Series(fish, index=dataframe.index).shift(1).fillna(0.0)
        )
        dataframe["pine_fisher_pos"] = pos
        dataframe["pine_fisher_possig"] = possig
        return dataframe

    def pine_context(self, dataframe, params):
        return {"possig": dataframe["pine_fisher_possig"].to_numpy(dtype=float)}

    def pine_script(self, broker, i, ctx):
        # if (possig == 1)
        #     strategy.entry("Long", strategy.long)
        # if (possig == -1)
        #     strategy.entry("Short", strategy.short)
        # Two independent `if`s, kept in the source's written order.
        if ctx["possig"][i] == 1:
            broker.entry("Long", "long")
        if ctx["possig"][i] == -1:
            broker.entry("Short", "short")
