"""Port of sources/SM_0df36a2f06d0c4ef.pine
(batch_001/Ichimoku均线交叉策略Ichimoku-Moving-Average-Crossover-Strategy.md).

Pine v3, long and short ("Noro's Ichimoku Strategy v1.0"). Every Ichimoku line
here is a Donchian midpoint, and the two trade conditions are pure LEVEL tests
against the base line -- no cross is required -- gated by an average-body
filter and a candle-colour filter:

    donchian(len) => avg(lowest(len), highest(len))
    conversionLine = donchian(conversionPeriods)      // 9
    baseLine       = donchian(basePeriods)            // 26
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = donchian(laggingSpan2Periods)    // 52

    nbody = abs(close - open)
    abody = sma(nbody, 10)
    body  = nbody > abody / 3 or usebf == false

    bar = close > open ? 1 : close < open ? -1 : 0
    gb  = bar == 1  or usecf == false
    rb  = bar == -1 or usecf == false

    up = low  > baseLine and rb and body
    dn = high < baseLine and gb and body

    if up
        strategy.entry("Long", strategy.long, needlong == false ? 0 : na,
                       when = (time > timestamp(fromyear, frommonth, fromday, 00, 00)
                               and time < timestamp(toyear, tomonth, today, 23, 59)))
    if dn
        strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when = <same>)
    if time > timestamp(toyear, tomonth, today, 23, 59)
        strategy.close_all()

`strategy()` declares `default_qty_type = strategy.percent_of_equity`,
`default_qty_value = 100` and `pyramiding = 0`; everything else is Pine's
documented default (commission 0%, initial capital 1000000,
process_orders_on_close false). The third `strategy.entry` argument is the
QUANTITY, so `needlong == false ? 0 : na` is reproduced as qty=0 when the
Long switch is off (`needlong` default true leaves it na, i.e. the
100%-of-equity default) -- measured: the 13 `input()` calls in the source and
the 13 rows of the md's argument table agree in count, and the two date inputs
the md renders as `true` are 1 in the code.

The date window is a real `when=` gate, not dead code, so it is reproduced:
with the source's defaults (1900-01-01 00:00 to 2100-12-31 23:59) it is true on
every bar, and the `close_all` guard (`time > 2100-12-31 23:59`) is false on
every bar -- measured on BTC/USDT:USDT 1h 2024: 8785 of 8785 bars in the
window, 0 of 8785 after it.

MEASURED, 2024-01-01..2025-01-01 BTC/USDT:USDT 1h (`verify_chain.py --port
SM_0df36a2f06d0c4ef`): `mismatch_framework_veto`. The engine books 353 trades,
Freqtrade 352, with exactly one `SOURCE_STAKE_VETO` at the 2024-03-05 21:00
fill (required 1022640.82 against a 1022533.70 maximum). Comparing the two
trade lists position by position, the two agree on open date, close date,
direction and price for the FIRST 71 TRADES, and the first divergence is that
vetoed fill; of the 352 aligned pairs the verifier reports 281 as mismatched
(open_date 281, close_date 281, direction 281, max_price_gap 10661.70), which
is the whole remaining list shifted by the one missing trade, because the
framework's wallet and the engine's cash no longer agree. The cause is the
source's own sizing -- `default_qty_type = strategy.percent_of_equity` with
`default_qty_value = 100`, i.e. every entry commits the entire equity -- which
PINE_SEMANTICS.md 1.4/1.5/1.6 documents as a framework limit: the venue's
contract-step rounding moves the framework's wallet off the engine's cash by
about 1e-4 relative, and at 100% of equity that gap is the whole order.

FIDELITY:

* `lowest(len)` / `highest(len)` are Pine v3's ONE-ARGUMENT forms. FMZ's Pine
  reference gives `highest`'s default source as High and states that
  `ta.lowest` uses `low`, so the port computes `lowest(low, len)` /
  `highest(high, len)` -- a Donchian channel, which is also what the two-line
  `avg` makes of it. Same choice, stated the same way, as the sibling port
  SMIchimokuCloud_7dfe07; not verified against the platform here.
* `sma(nbody, 10)` is `pine_ta.pine_sma`, i.e. na until the window is full.
  While `abody` is na the comparison `nbody > abody / 3` is false (Pine treats
  na as false in a boolean context, and pandas' `>` yields False for NaN), so
  `body` is false on the first nine bars -- measured by construction on the
  port's own columns.
* `up`/`dn` compare against a base line that is na until 26 bars have elapsed,
  so neither can fire before bar 25.
* A bar can satisfy neither, either, or BOTH conditions. The source's two
  `if` blocks are independent (not if/else-if), so both entries are emitted, in
  source order, when both hold; the engine then applies `pyramiding = 0`, which
  blocks the second one because the first has already opened a position on the
  fill bar. The port keeps both calls in source order rather than merging them.
* The entry `when=` window uses Pine's `time`, the bar's OPENING time, in the
  exchange timezone. The port evaluates it on the bar timestamps as UTC, which
  is the exchange timezone for BTC/USDT (PINE_SEMANTICS.md section 3.4 records
  the general risk).
* The commented-out `if strategy.position_size < 0 / strategy.close_all()` and
  its mirror above the second entry are comments in the source, not live code,
  and are NOT restored: this source closes on nothing but the end-of-window
  `strategy.close_all`, so an opposite entry is what ends a position.
* `plot` and `fill` (conversion line, base line, lagging span, lead 1, lead 2
  and the cloud) are display-only and place no order; they are not reproduced.
  The lines they draw ARE computed, because the source computes them.
* `leadLine1` / `leadLine2` / `conversionLine` feed only those plots in the
  live script -- no condition reads them -- but they are computed here too.
* The md's prose is not restated by the code in two places, recorded rather
  than reconciled: it claims the strategy uses "量价确认 / volume confirmation",
  and the code reads no volume at any point; and it advises adding stops, while
  the source has no stop, no `strategy.exit` and no `strategy.close` beyond the
  end-of-window `close_all`, so `source_reproduce_stops` is False.
* The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own fill
  granularity for the 1h bars, not the strategy's period.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the last of those separately.
"""
from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(dataframe: pd.DataFrame, length: int) -> pd.Series:
    """`donchian(len) => avg(lowest(len), highest(len))` on low / high."""
    return ta.pine_avg(
        ta.pine_lowest(dataframe["low"], length),
        ta.pine_highest(dataframe["high"], length),
    )


def _window_mask(index, start: datetime, end: datetime) -> np.ndarray:
    """Pine `time > start and time < end` on the bar's OPENING time.

    `time` is the bar's opening time in the exchange timezone; the frame is
    indexed by UTC candle times, so the bounds are built in UTC
    (PINE_SEMANTICS.md section 3.4). Python datetimes are used because the
    sibling sources in this batch can declare a ToYear beyond pandas'
    nanosecond range.
    """
    times = pd.DatetimeIndex(index)
    if times.tz is None:
        times = times.tz_localize("UTC")
    return np.fromiter(
        (start < t.to_pydatetime() < end for t in times), dtype=bool, count=len(times)
    )


def _time_after(index, bound: datetime) -> np.ndarray:
    """Pine `time > <bound>` on the bar's OPENING time, in the exchange zone."""
    times = pd.DatetimeIndex(index)
    if times.tz is None:
        times = times.tz_localize("UTC")
    return np.fromiter(
        (t.to_pydatetime() > bound for t in times), dtype=bool, count=len(times)
    )


class SMIchimokuMovingAverageCrossover_0df36a(PinePortBase, IStrategy):
    source_id = "SM_0df36a2f06d0c4ef"
    source_file = "Ichimoku均线交叉策略Ichimoku-Moving-Average-Crossover-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "needlong": True,
        "needshort": True,
        "conversionPeriods": 9,
        "basePeriods": 26,
        "laggingSpan2Periods": 52,
        "usebf": True,
        "usecf": True,
        "fromyear": 1900,
        "toyear": 2100,
        "frommonth": 1,
        "tomonth": 12,
        "fromday": 1,
        "today": 31,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The only close in the source is the end-of-window strategy.close_all;
    # there is no stop, limit or trailing order anywhere.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`lowest(len)` / `highest(len)` are v3's one-argument forms. FMZ's Pine "
        "reference gives highest's default source as High and states that "
        "ta.lowest uses low, so the port computes lowest(low, len) / "
        "highest(high, len) -- a Donchian channel. Same reading as the sibling "
        "port SMIchimokuCloud_7dfe07; unverified against the platform.",
        "The entry QUANTITY is the source's third argument: `needlong == false ? "
        "0 : na`. Reproduced as qty=0.0 when the switch is off (the engine then "
        "refuses the order, which is what a zero-quantity Pine entry does) and "
        "as the default 100%-of-equity size when it is on -- i.e. the source's "
        "own ternary is kept rather than collapsed into a bare entry.",
        "The `when=` date window is reproduced with Pine's time semantics: the "
        "bar's OPENING time compared against the bounds, exclusive at both ends "
        "(`time > start` and `time < end`). With the source's defaults "
        "(1900-01-01 00:00 .. 2100-12-31 23:59) it is true on every bar, and the "
        "close_all guard `time > 2100-12-31 23:59` is false on every bar; both "
        "were measured on the port's own columns. The bounds are evaluated in "
        "UTC, the exchange timezone for BTC/USDT (PINE_SEMANTICS.md 3.4).",
        "The two entry `if` blocks are independent in the source (no else-if), "
        "so a bar meeting both `up` and `dn` emits both entries in source order. "
        "Both are kept; the second is then blocked by `pyramiding = 0`, exactly "
        "as Pine's default limits one entry per direction.",
        "The two commented-out `strategy.close_all()` blocks (position_size < 0 "
        "above the Long entry and > 0 above the Short entry) are comments in the "
        "source and are NOT restored. The only close is the end-of-window "
        "`strategy.close_all`.",
        "No stop, limit or trailing exit exists, so source_reproduce_stops is "
        "False; a position ends only by the opposite entry reversing it or by "
        "the end-of-window close_all.",
        "`body` is false while `abody` is na, because Pine treats na as false in "
        "a boolean context; `up` / `dn` are also false while baseLine is na. "
        "Both follow from the library's na propagation and were read off the "
        "port's own columns rather than assumed.",
        "Warm-up measured on BTC/USDT:USDT 1h 2024 (8785 bars): conversionLine "
        "first non-na at bar 8, abody at 9, baseLine at 25, leadLine2 at 51; the "
        "first `up` is at bar 25 and the first `dn` at bar 56. Nothing can fire "
        "before bar 25 because both signals read the base line.",
        "conversionLine, leadLine1 and leadLine2 feed only plot / fill in the "
        "live script -- no condition reads them -- but the source computes them, "
        "so they are computed here and kept as ledger columns.",
        "MD-vs-CODE, recorded not reconciled: the prose claims the strategy uses "
        "'量价确认' (volume confirmation) and fuses moving averages, price "
        "channels and volume; the code reads no volume at all.",
        "MD-vs-CODE, recorded not reconciled: the prose advises adding stops to "
        "control risk, and the code has no stop of any kind.",
        "MD-vs-CODE, recorded not reconciled: the md's argument table renders "
        "the numeric-1 defaults of From Month and From day as `true` (the FMZ "
        "exporter's rendering of 1); the code's `01` is used.",
        "The `strategy()` call declares percent_of_equity / 100 and pyramiding 0; "
        "commission, initial capital (Pine's documented 1000000) and "
        "process_orders_on_close are left at their documented defaults.",
        "The /*backtest header's basePeriod: 15m is the FMZ backtester's own "
        "filling granularity for the 1h bars, not the strategy's period.",
        "Leverage, margin, liquidation, funding and venue contract-step rounding "
        "are not modelled.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        conversion_periods = int(params["conversionPeriods"])
        base_periods = int(params["basePeriods"])
        lagging2_periods = int(params["laggingSpan2Periods"])

        # donchian(len) => avg(lowest(len), highest(len))
        conversion_line = _donchian(dataframe, conversion_periods)
        base_line = _donchian(dataframe, base_periods)
        lead_line1 = ta.pine_avg(conversion_line, base_line)
        lead_line2 = _donchian(dataframe, lagging2_periods)

        close = dataframe["close"]
        open_ = dataframe["open"]
        low = dataframe["low"]
        high = dataframe["high"]

        # nbody = abs(close - open); abody = sma(nbody, 10)
        nbody = (close - open_).abs()
        abody = ta.pine_sma(nbody, 10)
        # body = nbody > abody / 3 or usebf == false
        body = (nbody > abody / 3.0) | (not bool(params["usebf"]))
        body = body.fillna(False)

        # bar = close > open ? 1 : close < open ? -1 : 0
        bar = pd.Series(
            np.where(close > open_, 1, np.where(close < open_, -1, 0)),
            index=dataframe.index,
        )
        # gb = bar == 1 or usecf == false ; rb = bar == -1 or usecf == false
        gb = (bar == 1) | (not bool(params["usecf"]))
        rb = (bar == -1) | (not bool(params["usecf"]))

        # up = low > baseLine and rb and body ; dn = high < baseLine and gb and body
        up = (low > base_line) & rb & body
        down = (high < base_line) & gb & body

        # when = (time > timestamp(fromyear, frommonth, fromday, 00, 00)
        #         and time < timestamp(toyear, tomonth, today, 23, 59))
        in_window = _window_mask(
            dataframe.index,
            datetime(
                int(params["fromyear"]), int(params["frommonth"]),
                int(params["fromday"]), 0, 0, tzinfo=timezone.utc,
            ),
            datetime(
                int(params["toyear"]), int(params["tomonth"]),
                int(params["today"]), 23, 59, tzinfo=timezone.utc,
            ),
        )
        # if time > timestamp(toyear, tomonth, today, 23, 59) / strategy.close_all()
        after_window = _time_after(
            dataframe.index,
            datetime(
                int(params["toyear"]), int(params["tomonth"]),
                int(params["today"]), 23, 59, tzinfo=timezone.utc,
            ),
        )

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead_line1"] = lead_line1
        dataframe["pine_lead_line2"] = lead_line2
        dataframe["pine_nbody"] = nbody
        dataframe["pine_abody"] = abody
        dataframe["pine_body"] = body
        dataframe["pine_bar"] = bar
        dataframe["pine_gb"] = gb
        dataframe["pine_rb"] = rb
        dataframe["pine_up"] = up.fillna(False)
        dataframe["pine_down"] = down.fillna(False)
        dataframe["pine_in_window"] = in_window
        dataframe["pine_after_window"] = after_window
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "up": dataframe["pine_up"].to_numpy(dtype=bool),
            "down": dataframe["pine_down"].to_numpy(dtype=bool),
            "in_window": dataframe["pine_in_window"].to_numpy(dtype=bool),
            "after_window": dataframe["pine_after_window"].to_numpy(dtype=bool),
            "needlong": bool(params["needlong"]),
            "needshort": bool(params["needshort"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if up
        #     strategy.entry("Long", strategy.long, needlong == false ? 0 : na, when = ...)
        if ctx["up"][i]:
            broker.entry(
                "Long", "long",
                qty=None if ctx["needlong"] else 0.0,
                when=bool(ctx["in_window"][i]),
            )

        # if dn
        #     strategy.entry("Short", strategy.short, needshort == false ? 0 : na, when = ...)
        if ctx["down"][i]:
            broker.entry(
                "Short", "short",
                qty=None if ctx["needshort"] else 0.0,
                when=bool(ctx["in_window"][i]),
            )

        # if time > timestamp(toyear, tomonth, today, 23, 59)
        #     strategy.close_all()
        broker.close_all(when=bool(ctx["after_window"][i]))
