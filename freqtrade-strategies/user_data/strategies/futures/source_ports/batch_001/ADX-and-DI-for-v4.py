"""Port of sources/SM_2153584a60e384c6.pine (batch_001/ADX-and-DI-for-v4.md).

Pine v4. The file declares `study("ADX and DI for v4")`, NOT `strategy(...)`:
the two `strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/361554,
named in the md's Detail link). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended block,
and the trading behaviour it defines is entry-only:

    if DIPlus > DIMinus
        strategy.entry("entry long", strategy.long)
    else if DIPlus < DIMinus
        strategy.entry("entry short", strategy.short)

The indicator is BeikabuOyaji's ADX/DI, written with the recursive Wilder
smoothing spelled out by hand rather than `ta.rma`:

    TrueRange  = max(max(high-low, abs(high-nz(close[1]))), abs(low-nz(close[1])))
    DMPlus     = high-nz(high[1]) >  nz(low[1])-low ? max(high-nz(high[1]), 0) : 0
    DMMinus    = nz(low[1])-low   >  high-nz(high[1]) ? max(nz(low[1])-low, 0)   : 0

    SmoothedTrueRange := nz(SmoothedTrueRange[1]) - nz(SmoothedTrueRange[1])/len
                         + TrueRange                      # and likewise for both DMs

    DIPlus  = SmoothedDMPlus  / SmoothedTrueRange * 100
    DIMinus = SmoothedDMMinus / SmoothedTrueRange * 100
    DX      = abs(DIPlus-DIMinus) / (DIPlus+DIMinus) * 100
    ADX     = sma(DX, len)

The two conditions are strictly opposed, so at most one order is placed per bar
and the `else if` chain is kept as `elif` to mirror Pine's short-circuit. Both
entries are plain market orders with no stop, limit or quantity argument, so the
engine fills them at the NEXT bar's open with the script's default sizing.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal; since
DIPlus and DIMinus have a definite order on every bar, the position is in fact
flipped whenever the sign of DI+ - DI- changes. `pyramiding` keeps Pine's
default of 0, so a repeated signal while already positioned that way is
ignored.

FIDELITY:

* The smoothing is the source's OWN recursion, not `ta.rma` and not
  `pine_ta.pine_rma`: it starts from `nz(na) = 0` on the first bar and then
  `s = s - s/len + x`, i.e. a seed of the first bar's raw value rather than
  pine_rma's SMA of the first `len` observations. Using the library smoother
  would shift every DI/ADX value, so the port runs the recursion literally.
* `nz(close[1])`, `nz(high[1])`, `nz(low[1])` are 0 on the first bar, which is
  what makes TrueRange[0] = high[0], DMPlus[0] = high[0] and DMMinus[0] = 0
  (DIPlus[0] = 100, DIMinus[0] = 0). The port seeds the recursion with 0.0 for
  exactly this reason.
* Pine yields na for a zero denominator, so both DI divisions and the DX
  division are guarded: a zero denominator produces na rather than pandas' inf.
* `ADX = sma(DX, len)` is `pine_ta.pine_sma`: na until `len` bars have elapsed,
  na propagating through the window.
* `th = input(20)` is declared and never read (its only use, `hline(th, ...)`,
  is commented out in the source); it is recorded in `source_defaults` and is
  dead code, reproduced as such.
* The source declares `study(...)`, not `strategy(...)`, so it carries no
  strategy() properties; Pine's documented defaults are what the source_*
  attributes record (fixed size 1, 0% commission, pyramiding 0, initial
  capital 1000000). On TradingView strategy.entry inside a study does not
  compile; the host named by the source's /*backtest header and the md's Detail
  link (fmz.com/strategy/361554) is what ran the appended block, and that
  platform's Pine dialect -- not TradingView -- is the behaviour this port
  reproduces.
* The three `plot(...)` calls are display-only and place no order; they are
  dropped.
* The header's backtest window (2021-05-05 to 2022-05-04) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 1h` is the host's intrabar granularity for filling 1d bars, not
  the strategy's period.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _nz(value: float) -> float:
    """Pine `nz`: an na value becomes 0."""
    return 0.0 if value is None or np.isnan(value) else float(value)


def _wilder_recursive(values: np.ndarray, length: int) -> np.ndarray:
    """The source's hand-written smoothing, seeded from `nz(na) = 0`.

    `s := nz(s[1]) - nz(s[1])/len + x`, so the first bar is
    `0 - 0 + x[0]` -- a different warmup from `ta.rma`'s SMA seed.
    """
    out = np.full(len(values), np.nan)
    previous = 0.0
    for i, value in enumerate(values):
        current = previous - previous / length + value
        out[i] = current
        previous = current
    return out


def _pine_div(numerator, denominator):
    """Pine division: a zero denominator yields na, not inf."""
    return numerator / denominator.replace(0.0, np.nan)


class SMAdxAndDiForV4_215358(PinePortBase, IStrategy):
    source_id = "SM_2153584a60e384c6"
    source_file = "ADX-and-DI-for-v4.md"
    timeframe = "1d"
    can_short = True
    # Input defaults exactly as written. `th` is never read by the source.
    source_defaults: dict = {"len": 14, "th": 20}
    # study(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere in the
    # source -- not even a commented-out one.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The Wilder smoothing is the source's own recursion, not ta.rma and not "
        "pine_ta.pine_rma: it seeds from nz(na) = 0 on the first bar and then "
        "runs s := s - s/len + x. pine_rma instead seeds with the SMA of the "
        "first `len` observations, which would shift every DI and ADX value; "
        "the recursion is therefore written out literally in the port.",
        "nz(close[1]) / nz(high[1]) / nz(low[1]) are 0 on the first bar (Pine's "
        "nz replaces an na history reference with 0), so TrueRange[0] is high[0] "
        "and DMPlus[0] is high[0] while DMMinus[0] is 0 -- DIPlus starts at 100 "
        "and DIMinus at 0. The port seeds the recursion with 0.0 to reproduce "
        "exactly that; a port that dropped the first bar would start the "
        "recursion one observation later.",
        "Division: Pine yields na for a zero denominator. Both DI ratios and the "
        "DX ratio go through _pine_div, which turns a zero denominator into na "
        "rather than letting pandas return +-inf.",
        "ADX = sma(DX, len) is pine_ta.pine_sma (na until the window is full, na "
        "propagating inside it). The window never sees an na in the DX series "
        "here, because DIPlus/DIMinus are defined from the first bar.",
        "`th = input(20)` is dead code: the source's only use of it, "
        "hline(th, ...), is commented out. Recorded in source_defaults and "
        "reproduced as an unused value, not deleted.",
        "The source declares study(...), not strategy(...), so no strategy() "
        "properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD. On TradingView strategy.entry inside a "
        "study does not compile; the host named by the source's /*backtest "
        "header and the md's Detail link (fmz.com/strategy/361554) is what ran "
        "the appended block, and that platform's Pine dialect -- not "
        "TradingView -- is the original behaviour this port reproduces.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill (close the old side, open the new one). "
        "source_reproduce_stops is False accordingly.",
        "The two entry conditions are strictly opposed (DI+ > DI- versus "
        "DI+ < DI-), so a bar on which they are equal -- or on which either is "
        "na -- places no order. Kept as if/elif to mirror Pine's else-if.",
        "The three plot() calls are display-only and place no order; dropped.",
        "The backtest window in the header (2021-05-05 to 2022-05-04) is "
        "extraction metadata, not an input.time filter, so the port runs on "
        "whatever range the caller supplies. The header's basePeriod: 1h is the "
        "host's intrabar granularity for filling 1d bars, not the period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["len"])
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        close = dataframe["close"].to_numpy(dtype=float)

        # nz(close[1]) / nz(high[1]) / nz(low[1]): 0 on the first bar.
        previous_close = np.concatenate(([0.0], close[:-1]))
        previous_high = np.concatenate(([0.0], high[:-1]))
        previous_low = np.concatenate(([0.0], low[:-1]))

        # TrueRange = max(max(high-low, abs(high-nz(close[1]))), abs(low-nz(close[1])))
        true_range = np.maximum(
            np.maximum(high - low, np.abs(high - previous_close)),
            np.abs(low - previous_close),
        )
        high_diff = high - previous_high
        low_diff = previous_low - low
        # DirectionalMovementPlus / Minus, including their `max(..., 0)` clamps.
        dm_plus = np.where(high_diff > low_diff, np.maximum(high_diff, 0.0), 0.0)
        dm_minus = np.where(low_diff > high_diff, np.maximum(low_diff, 0.0), 0.0)

        smoothed_tr = _wilder_recursive(true_range, length)
        smoothed_plus = _wilder_recursive(dm_plus, length)
        smoothed_minus = _wilder_recursive(dm_minus, length)

        index = dataframe.index
        smoothed_tr_s = pd.Series(smoothed_tr, index=index)
        di_plus = _pine_div(100.0 * pd.Series(smoothed_plus, index=index), smoothed_tr_s)
        di_minus = _pine_div(100.0 * pd.Series(smoothed_minus, index=index), smoothed_tr_s)
        # DX = abs(DIPlus-DIMinus) / (DIPlus+DIMinus) * 100
        dx = _pine_div(100.0 * (di_plus - di_minus).abs(), di_plus + di_minus)
        adx = ta.pine_sma(dx, length)

        dataframe["pine_di_plus"] = di_plus
        dataframe["pine_di_minus"] = di_minus
        dataframe["pine_dx"] = dx
        dataframe["pine_adx"] = adx
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "di_plus": dataframe["pine_di_plus"].to_numpy(),
            "di_minus": dataframe["pine_di_minus"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if DIPlus > DIMinus
        #     strategy.entry("entry long", strategy.long)
        # else if DIPlus < DIMinus
        #     strategy.entry("entry short", strategy.short)
        di_plus = ctx["di_plus"][i]
        di_minus = ctx["di_minus"][i]
        if di_plus > di_minus:
            broker.entry("entry long", "long")
        elif di_plus < di_minus:
            broker.entry("entry short", "short")
