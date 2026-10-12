"""Port of sources/SM_25b12921b7598c9a.pine (batch_001/Andrew-Abraham趋势追踪策略Andrew-Abraham-Trend-Tracking-Strategy.md).

Pine v2 (`//@version=2`), HPotter's transcription of the "Trend Trader" that
Andrew Abraham published in the "Trading the Trend" article of TASC, September
1998. It is a chandelier-style trailing channel and an unconditional reversal:

    Length     = input(21, minval=1)
    Multiplier = input(3, minval=1)
    reverse    = input(false, title="Trade reverse")

    avgTR    = wma(atr(1), Length)
    highestC = highest(Length)              // highest high
    lowestC  = lowest(Length)               // lowest low
    hiLimit  = highestC[1] - (avgTR[1] * Multiplier)
    loLimit  = lowestC[1]  + (avgTR[1] * Multiplier)

    ret = iff(close > hiLimit and close > loLimit, hiLimit,
          iff(close < loLimit and close < hiLimit, loLimit, nz(ret[1], 0)))
    pos = iff(close > ret, 1,
          iff(close < ret, -1, nz(pos[1], 0)))
    possig = iff(reverse and pos == 1,  -1,
             iff(reverse and pos == -1,  1, pos))

    if (possig == 1)
        strategy.entry("Long", strategy.long)
    if (possig == -1)
        strategy.entry("Short", strategy.short)

`ret` and `pos` are both self-referential series: each bar's value falls back to
its own previous value (through `nz(..., 0)`, so the very first bar's fallback
is 0). Both are therefore computed in a single forward pass, exactly as written,
and not seeded with an SMA or a rolling extreme.

The entries are unconditional in the sense that the source re-issues them on
every bar the state persists, not only on the flip bar. Pine's `pyramiding`
default of 0 is what turns that into "enter on the flip only", and `pine_engine`
reproduces it by blocking same-direction stacking; the projected `enter_long` /
`enter_short` columns inherit the same block, so the framework sees exactly the
entries the engine fills. There is no exit call at all, so a position is only
ever closed by the opposite entry reversing it and `source_reproduce_stops` is
False.

`strategy(title="Trend Trader Strategy", overlay=true)` declares only `title`
and `overlay`, so Pine's documented defaults apply: `default_qty_type =
strategy.fixed`, `default_qty_value = 1`, `commission_value = 0`,
`pyramiding = 0`, initial capital 1000000 and `process_orders_on_close = false`.
The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own granularity
for filling those daily bars, not the strategy's period.

FIDELITY:

* `atr(1)` is Wilder's `rma(tr, 1)`, and an RMA over a single sample IS that
  sample, so `atr(1)` is the true range itself. The port keeps the call shape
  (`pine_atr(dataframe, 1)`) rather than substituting `pine_tr`, so the identity
  stays visible. `pine_ta.pine_atr` uses `ta.tr` with `handle_na=True`, which
  gives the first bar `high - low`; this is the ONE place PINE_SEMANTICS §3.7
  records a public-layer difference (bare `ta.tr` is na on the first bar), and it
  only moves the seeding bar of the following WMA, not any formula here.
* `highest(Length)` / `lowest(Length)` are the one-argument forms, which Pine
  documents as the highest `high` / lowest `low` over `Length` bars. Read that
  way because the source pairs them into a channel around the extremes
  (`hiLimit` from `highestC`, `loLimit` from `lowestC`); the port does not
  reinterpret them as close-based.
* `wma(atr(1), Length)` weights the newest observation heaviest (weights
  1..Length), which is what `pine_ta.pine_wma` computes, and it is na until the
  whole `Length`-bar window is filled, so `hiLimit` / `loLimit` are na for the
  first `Length` bars (plus one bar for the `[1]` lag).
* `iff` returns its second argument unless the condition is true, so a bar whose
  `hiLimit` / `loLimit` are na (the warm-up bars) falls through to
  `nz(ret[1], 0)`. On bar 0 that is 0, so `close > ret` on bar 0 puts `pos` at 1
  and the source genuinely issues its first `Long` entry there. Transcribed as
  written rather than suppressed.
* `reverse = input(false, ...)` is a boolean input used in a boolean context
  (`reverse and pos == 1`), NOT in an arithmetic one, so PINE_SEMANTICS §1.16's
  bool-as-number trap does not apply here. It is carried as a Python bool and
  the two branches are selected with the same `and` semantics Pine uses.
* The `//backtest` header's window (2023-01-01..2024-01-07) is the FMZ
  backtester's own; the chain verifier's window is its own choice and is not
  driven by this header.
* `barcolor` and `plot` are display-only and are not reproduced, as are the
  title and the `overlay`.
* Contract-step rounding, leverage, margin, liquidation and funding are not
  modelled (PINE_SEMANTICS §1.6, §二-4).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAndrewAbrahamTrendTrader_25b129(PinePortBase, IStrategy):
    source_id = "SM_25b12921b7598c9a"
    source_file = "Andrew-Abraham趋势追踪策略Andrew-Abraham-Trend-Tracking-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"Length": 21, "Multiplier": 3, "reverse": False}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "atr(1) is rma(tr, 1), and an RMA over one sample IS the sample, so it "
        "equals the true range; the port keeps pine_atr(dataframe, 1) rather "
        "than substituting pine_tr so the identity stays visible.",
        "pine_ta.pine_atr's ta.tr uses handle_na=True, giving the first bar "
        "high - low. This is the one public-layer boundary recorded in "
        "PINE_SEMANTICS §3.7 (bare ta.tr is na on bar 0); it moves only the "
        "seeding bar of the following WMA.",
        "highest(Length) / lowest(Length) are Pine's one-argument forms, i.e. "
        "the highest high / lowest low over Length bars. Read that way because "
        "the source builds a channel around the extremes; not reinterpreted as "
        "close-based.",
        "ret and pos are self-referential: each bar falls back to its own "
        "previous value through nz(..., 0), whose bar-0 fallback is 0. Both are "
        "computed in one forward pass exactly as written, not seeded with an "
        "SMA or a rolling extreme.",
        "On bar 0 hiLimit / loLimit are na, so ret = nz(ret[1], 0) = 0 and "
        "close > ret puts pos at 1: the source really does issue its first Long "
        "on bar 0. Transcribed rather than suppressed.",
        "reverse = input(false, ...) is a boolean input used in a boolean "
        "context (reverse and pos == 1), not an arithmetic one, so "
        "PINE_SEMANTICS §1.16's bool-as-number trap does not apply.",
        "The source re-issues the entry on every bar its state persists, not "
        "only on the flip bar; Pine's pyramiding default of 0 turns that into "
        "enter-on-flip, and pine_engine reproduces it by blocking "
        "same-direction stacking (the projected signal columns inherit the same "
        "block).",
        "There is no exit call in the source: a position is closed only by the "
        "opposite entry reversing it, so source_reproduce_stops is False and a "
        "position open at the end of the window stays open.",
        "strategy() declares only title/overlay, so Pine's defaults apply: "
        "qty_type fixed, qty_value 1, commission 0, pyramiding 0, initial "
        "capital 1000000, process_orders_on_close false.",
        "barcolor / plot / title / overlay are display-only and are not "
        "reproduced.",
        "Contract-step rounding, leverage, margin, liquidation and funding are "
        "not modelled (PINE_SEMANTICS §1.6, §二-4).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["Length"])
        multiplier = float(params["Multiplier"])
        reverse = bool(params["reverse"])
        close = dataframe["close"]

        # avgTR    = wma(atr(1), Length)
        avg_tr = ta.pine_wma(ta.pine_atr(dataframe, 1), length)
        # highestC = highest(Length)   /   lowestC = lowest(Length)
        highest_c = ta.pine_highest(dataframe["high"], length)
        lowest_c = ta.pine_lowest(dataframe["low"], length)
        # hiLimit = highestC[1] - (avgTR[1] * Multiplier)
        hi_limit = highest_c.shift(1) - avg_tr.shift(1) * multiplier
        # loLimit = lowestC[1] + (avgTR[1] * Multiplier)
        lo_limit = lowest_c.shift(1) + avg_tr.shift(1) * multiplier

        close_values = close.to_numpy(dtype=float)
        hi_values = hi_limit.to_numpy(dtype=float)
        lo_values = lo_limit.to_numpy(dtype=float)
        count = len(close_values)
        ret_values = np.full(count, np.nan)
        pos_values = np.full(count, np.nan)
        ret_lag = np.nan
        pos_lag = np.nan
        for i in range(count):
            price = close_values[i]
            hi = hi_values[i]
            lo = lo_values[i]
            # ret = iff(close > hiLimit and close > loLimit, hiLimit,
            #       iff(close < loLimit and close < hiLimit, loLimit,
            #           nz(ret[1], 0)))
            # An na bound makes both comparisons false, so the warm-up bars
            # fall straight through to the nz() fallback -- as in Pine, where
            # a series comparison against na yields false and iff takes its
            # second argument unless the condition is true.
            if price > hi and price > lo:
                ret = hi
            elif price < lo and price < hi:
                ret = lo
            else:
                ret = 0.0 if np.isnan(ret_lag) else ret_lag
            # pos = iff(close > ret, 1, iff(close < ret, -1, nz(pos[1], 0)))
            if price > ret:
                pos = 1.0
            elif price < ret:
                pos = -1.0
            else:
                pos = 0.0 if np.isnan(pos_lag) else pos_lag
            ret_values[i] = ret
            pos_values[i] = pos
            ret_lag = ret
            pos_lag = pos

        ret = pd.Series(ret_values, index=close.index, dtype=float)
        pos = pd.Series(pos_values, index=close.index, dtype=float)
        # possig = iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))
        # A pure per-bar function of pos, so it is applied elementwise: with
        # reverse false (the source default) it is the identity.
        if reverse:
            possig = np.where(pos == 1.0, -1.0, np.where(pos == -1.0, 1.0, pos))
        else:
            possig = pos.to_numpy(dtype=float)

        dataframe["pine_avg_tr"] = avg_tr
        dataframe["pine_ret"] = ret
        dataframe["pine_pos"] = pos
        dataframe["pine_possig"] = possig
        dataframe["pine_long_condition"] = possig == 1.0
        dataframe["pine_short_condition"] = possig == -1.0
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if (possig == 1)
        #     strategy.entry("Long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # if (possig == -1)
        #     strategy.entry("Short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
