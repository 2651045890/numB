"""Port of sources/SM_1f06a8a54a62c990.pine (batch_001/ATR-动态止盈止损策略ATR-Dynamic-Profit-Target-and-Stop-Loss-Strategy.md).

Pine v2. A recursive ATR "volatility stop" line, with the entries driven by the
side of the line the close sits on:

    length = input(20)
    mult   = input(1)
    atr_   = atr(length)
    max1   = max(nz(max_[1]), close)
    min1   = min(nz(min_[1]), close)
    is_uptrend_prev = nz(is_uptrend[1], true)
    stop   = is_uptrend_prev ? max1 - mult * atr_ : min1 + mult * atr_
    vstop_prev = nz(vstop[1])
    vstop1 = is_uptrend_prev ? max(vstop_prev, stop) : min(vstop_prev, stop)
    is_uptrend = close - vstop1 >= 0
    is_trend_changed = is_uptrend != is_uptrend_prev
    max_   = is_trend_changed ? close : max1
    min_   = is_trend_changed ? close : min1
    vstop  = is_trend_changed ? (is_uptrend ? max_ - mult*atr_ : min_ + mult*atr_) : vstop1

    bullish = close > vstop
    bearish = close < vstop
    if bullish: strategy.entry("Buy",  strategy.long,  1)
    if bearish: strategy.entry("Sell", strategy.short, 1)

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0. The entries pass `qty=1` positionally, which is the
same quantity the default supplies.

There is no exit call: the position is only ever reversed by the opposite entry,
so `source_reproduce_stops` is False and a position open at the end of the
window stays open.

THE INDICATOR IS RECURSIVE AND IS COMPUTED BAR BY BAR, in this source's own
evaluation order. Every `[1]` reference is the PREVIOUS bar's final value, which
is how Pine reads a series: the names `max_`, `min_`, `is_uptrend` and `vstop`
are referenced before their assignment in the same block, and that is legal
only because each reference is to the prior bar's series. Re-deriving this with
vectorised pandas would silently pick a different evaluation order, so the loop
below mirrors the source statement for statement.

na HANDLING (a modelling choice, since Pine's `max`/`min` na rule cannot be
checked offline): `atr_` is na for the first `length` bars, and the source
guards every recursion seed with `nz(...)` but NOT the `stop` / `vstop1`
arithmetic. `pine_ta.pine_max` / `pine_min` are `np.maximum` / `np.minimum`,
which propagate na, so during the warm-up `vstop1` stays na, `is_uptrend` is na
(a comparison with na is falsy in Pine), and `bullish` / `bearish` are both
false -- the source emits no orders until the ATR exists. The alternative
reading, in which `max(na, x)` ignores the na, would make `vstop1 = 0` during
the warm-up and turn EVERY warm-up bar into a `close > 0` long entry; that
reading is rejected here because it is not what na propagation gives and
because it would make the source's own `nz` seeding pointless. The difference
is confined to the first `length` bars and is recorded rather than hidden.

The trend state is seeded exactly as the source seeds it: `nz(is_uptrend[1],
true)` is TRUE on the first bar (the na of a not-yet-existing series), and
`nz(max_[1])` / `nz(min_[1])` / `nz(vstop[1])` are 0. Note that `min1 =
min(nz(min_[1]), close)` therefore starts at 0 for positive prices; that is the
source's own arithmetic, and it is washed out at the first trend change
(`min_ = is_trend_changed ? close : min1`), so it is reproduced as written.

FIDELITY:

* THE MD'S ARGUMENT TABLE DISAGREES WITH THE SOURCE and the source is followed:
  the md lists `v_input_2 | true | mult`, i.e. a boolean default, while the
  source is `mult = input(1)` and `mult` is multiplied into the ATR distance
  (`mult * atr_`). The port takes `mult = 1` (numeric). The md's prose also
  describes a take-profit/stop-loss mechanism, while the code's only order
  calls are the two `strategy.entry` statements above; the line is a trend
  filter, not a resting stop order, and nothing in the source places a
  stop/limit/profit/loss order at all.
* `atr(length)` is Pine's Wilder ATR, modelled by `pine_ta.pine_atr`
  (`chandelier`-style `rma(tr, length)`). Per PINE_SEMANTICS.md section 3.7,
  `pine_atr` seeds `tr` on the first bar with `high - low` while Pine's default
  `ta.tr` returns na there, which shifts the rma seeding point by one bar; the
  ATR converges afterwards and this source's signals are ATR-threshold driven,
  so the effect is confined to the warm-up boundary.
* `is_uptrend != is_uptrend_prev` is a BOOLEAN comparison in this source (v2
  has no `math.*` namespace) and is reproduced as such. Section 1.16 (Pine v2
  treating bool as 1/0 in numeric contexts) does not apply here: neither
  operand is used numerically anywhere in the source -- the value only ever
  selects a ternary branch.
* `plot(vstop, color=...)` is display-only and is not reproduced.
* Leverage, margin, liquidation and funding are not modelled; the venue's
  contract-step rounding is not modelled either, so the framework and the
  engine can differ by a rounded quantity.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMATRDynamicProfitTargetStopLoss_1f06a8(PinePortBase, IStrategy):
    source_id = "SM_1f06a8a54a62c990"
    source_file = "ATR-动态止盈止损策略ATR-Dynamic-Profit-Target-and-Stop-Loss-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"length": 20, "mult": 1}
    # strategy(title, overlay=true): Pine defaults, nothing declared.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The indicator is recursive; it is evaluated bar by bar in the source's "
        "own statement order, with every [1] reference read as the previous "
        "bar's final value.",
        "The md's argument table lists mult as a boolean (`v_input_2 | true`), "
        "but the source is `mult = input(1)` and multiplies it into the ATR "
        "distance. The source is followed: mult = 1 (numeric).",
        "The md's prose describes dynamic take-profit/stop-loss orders; the "
        "source places no stop/limit/profit/loss order. Its only order calls "
        "are the two market entries, and the volatility line is only a trend "
        "filter. Recorded, not reconciled.",
        "na handling is a modelling choice: pine_max/pine_min propagate na, so "
        "during the ATR warm-up vstop1 is na, is_uptrend is na and no entry "
        "fires. The alternative reading (max ignoring na, vstop1 = 0) would "
        "enter a long on every warm-up bar. Confined to the first `length` bars.",
        "nz(is_uptrend[1], true) seeds the trend state TRUE on bar 0, and "
        "nz(max_[1]) / nz(min_[1]) / nz(vstop[1]) seed with 0; that makes "
        "min1 start at 0 for positive prices. The source's own arithmetic is "
        "reproduced as written and washes out at the first trend change.",
        "pine_atr seeds tr with high-low on its first bar while Pine's default "
        "ta.tr returns na there (PINE_SEMANTICS.md 3.7); the seeding point of "
        "the rma therefore differs by one bar. Not corrected in the port.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open "
        "at the end of the window stays open.",
        "plot(vstop) is display-only and is not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["length"])
        mult = float(params["mult"])
        close = dataframe["close"].to_numpy(dtype=float)
        atr_ = ta.pine_atr(dataframe, length).to_numpy(dtype=float)
        count = len(close)

        vstop = np.full(count, np.nan)
        trend = np.full(count, np.nan)  # Pine's `is_uptrend`; na until ATR exists
        changed = np.zeros(count, dtype=bool)
        bullish = np.zeros(count, dtype=bool)
        bearish = np.zeros(count, dtype=bool)

        # Previous bars' final values of the recursive series. na is carried as
        # NaN and `nz` collapses it to the source's replacement value.
        max_prev, min_prev, vstop_prev = np.nan, np.nan, np.nan
        is_uptrend_prev_state = None  # None is na; nz(..., true) makes it True

        for i in range(count):
            price = close[i]
            value = atr_[i]
            # max1 = max(nz(max_[1]), close); min1 = min(nz(min_[1]), close)
            max1 = ta.pine_max(ta.nz(max_prev), price)
            min1 = ta.pine_min(ta.nz(min_prev), price)
            # is_uptrend_prev = nz(is_uptrend[1], true)
            up_prev = True if is_uptrend_prev_state is None else bool(is_uptrend_prev_state)
            # stop = is_uptrend_prev ? max1 - mult*atr_ : min1 + mult*atr_
            stop = max1 - mult * value if up_prev else min1 + mult * value
            # vstop_prev = nz(vstop[1]); vstop1 = up_prev ? max(..) : min(..)
            vstop1 = (
                ta.pine_max(ta.nz(vstop_prev), stop) if up_prev
                else ta.pine_min(ta.nz(vstop_prev), stop)
            )
            # is_uptrend = close - vstop1 >= 0 (na while vstop1 is na)
            up = None if np.isnan(vstop1) else bool(price - vstop1 >= 0)
            # is_trend_changed = is_uptrend != is_uptrend_prev
            trend_changed = None if up is None else bool(up != up_prev)
            # max_ = is_trend_changed ? close : max1 (same for min_)
            max_ = price if trend_changed else max1
            min_ = price if trend_changed else min1
            # vstop = is_trend_changed ? (is_uptrend ? max_-mult*atr_ : min_+mult*atr_) : vstop1
            if trend_changed:
                level = max_ - mult * value if up else min_ + mult * value
            else:
                level = vstop1

            vstop[i] = level
            if up is not None:
                trend[i] = 1.0 if up else 0.0
            changed[i] = bool(trend_changed)
            # bearish = close < vstop ; bullish = close > vstop
            if not np.isnan(level):
                bullish[i] = bool(price > level)
                bearish[i] = bool(price < level)

            max_prev, min_prev, vstop_prev = max_, min_, level
            is_uptrend_prev_state = up

        dataframe["pine_vstop"] = vstop
        dataframe["pine_is_uptrend"] = trend
        dataframe["pine_is_trend_changed"] = changed
        dataframe["pine_bullish"] = bullish
        dataframe["pine_bearish"] = bearish
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "bullish": dataframe["pine_bullish"].to_numpy(),
            "bearish": dataframe["pine_bearish"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (bullish)
        #     strategy.entry("Buy", strategy.long, 1)
        if ctx["bullish"][i]:
            broker.entry("Buy", "long", 1)
        # if (bearish)
        #     strategy.entry("Sell", strategy.short, 1)
        if ctx["bearish"][i]:
            broker.entry("Sell", "short", 1)
