"""Port of sources/SM_3556bf5382f000ca.pine (batch_001/52周高低盒子交易策略52-Week-High-Low-Box-Trading-Strategy.md).

Pine v4, "Darvas Box Strategy". The box is built from DAILY data requested onto
whatever chart the script runs on (here the `/*backtest` header's `period: 1h`)
and trades breakouts of the box with the daily close:

    boxp = input(5, "BOX LENGTH")

    D_High  = security(syminfo.tickerid, 'D', high)
    D_Low   = security(syminfo.tickerid, 'D', low)
    D_Close = security(syminfo.tickerid, 'D', close)
    D_Open  = security(syminfo.tickerid, 'D', open)

    LL = lowest(D_Low, boxp)
    k1 = highest(D_High, boxp)
    k2 = highest(D_High, boxp-1)
    k3 = highest(D_High, boxp-2)

    NH        = valuewhen(D_High > k1[1], D_High, 0)
    box1      = k3 < k2
    TopBox    = valuewhen(barssince(D_High > k1[1]) == boxp-2 and box1, NH, 0)
    BottomBox = valuewhen(barssince(D_High > k1[1]) == boxp-2 and box1, LL, 0)

    if crossover(D_Close, TopBox)
        strategy.entry("Long", strategy.long, comment="Long")
    if crossunder(D_Close, BottomBox)
        strategy.entry("Short", strategy.short, comment="Short")

`strategy()` declares only `title` and `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. Neither entry
passes `qty`, so the default quantity supplies it. The two `if` blocks are
independent (not `else if`) and are kept in their written order.

THE `security()` REQUESTS ARE THE PART THE SHARED ENGINE DOES NOT MODEL.
PINE_SEMANTICS.md section 二.1: the engine does not resample, so a port that
depends on multi-timeframe data must "supply an aligned series itself or be
recorded as an explicitly PARTIAL port". This port supplies it (which is why the
source is tier 4):

  * The daily OHLC is aggregated from THIS frame's 1h bars, grouped by the UTC
    calendar day (`index.floor("1D")`).
  * The alignment is the DEVELOPING daily value -- what `security()` without
    `lookahead` returns, i.e. the HTF value as it stands at each chart bar's
    close, using no data from any later bar: `D_High` is the day's running
    maximum, `D_Low` the running minimum, `D_Open` the day's opening bar, and
    `D_Close` the most recent chart close (which is what the developing daily
    close is). Nothing looks ahead, so the port passes the prefix-causality
    check.

The alternative alignment -- making the PREVIOUS COMPLETED day's OHLC visible for
the whole of the next day -- was tried first and REJECTED, not merely disfavoured:
it makes the source structurally untradeable. Under it `D_High` is a step
function that changes only at the first chart bar of a day, so `k1[1]` equals
`D_High` for every bar of the day, the only possible `D_High > k1[1]` bars are
day-boundary bars, and `barssince(...) == boxp-2` therefore lands three bars into
a day -- where `k2 = highest(D_High, boxp-1)` and `k3 = highest(D_High, boxp-2)`
are maxima over windows that lie inside that same, constant day, making
`box1 = k3 < k2` identically false. Zero boxes, zero trades, on any data. A
published strategy with a backtest curve cannot be that, so the developing
alignment (which is also the documented `lookahead_off` reading) is the one kept.
Both the choice and the rejected alternative are recorded in the report's
blockers: only the original platform can settle it.

FIDELITY:

* The source's `D_Open` is assigned and never used afterwards -- dead code. It is
  computed here too (as a column) and likewise never read.
* `highest`, `lowest`, `valuewhen`, `barssince` and `crossover` run on the 1h bar
  sequence with the daily series as input, exactly as Pine evaluates them on the
  chart's own bars. The port does not re-expand or smooth the daily series.
* `k1[1]` is the previous 1h BAR's `k1`, not the previous day's: history
  references are over the chart's bars, because that is the series the script is
  evaluated on.
* `valuewhen` is Pine's "last occurrence, carried forward" -- `pine_ta.pine_valuewhen`
  with occurrence 0. `barssince` before its first true is na, and `na == 3` is
  false, so the TopBox/BottomBox condition stays false until a first breakout.
* The three lookback lengths are `boxp`, `boxp-1` and `boxp-2`; a rolling window
  of length < 1 is na in Pine, so a `boxp` override below 3 yields na windows
  rather than an exception.
* MD/SOURCE DISAGREEMENT 1: the md is otherwise identical to the source, but its
  prose says the stop loss is set near the previous range's upper/lower limit.
  The CODE places no stop of any kind -- only the two entries. Code followed.
* MD/SOURCE DISAGREEMENT 2: the md describes the box as the last "5 days"
  (最近5天). That is only true if the chart were daily; the header declares
  `period: 1h`, so `highest(D_High, 5)` is a 5-CHART-BAR window over the daily
  series, i.e. five hours of running daily values, not five days. Code followed.
* No `strategy.close` / `strategy.exit` / `stop` / `limit` exists, so
  `source_reproduce_stops` is False and the only exits are the reverse entries.
  Both directions are entered, so `can_short` is True.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _daily_developing(dataframe, column, how):
    """The developing daily value of `column`, aligned onto this frame's bars.

    `security(syminfo.tickerid, 'D', ...)` without `lookahead` returns the
    higher-timeframe value as of each chart bar's close, computed from no later
    data: the running maximum / minimum so far inside the current UTC day, the
    day's opening bar, or the current bar's own close (the developing daily
    close). `how` selects which.
    """
    if not isinstance(dataframe.index, pd.DatetimeIndex):
        raise ValueError(
            "the security('D') alignment needs a DatetimeIndex; a range index "
            "would silently align every bar to 1970 (PINE_SEMANTICS.md 1.2)"
        )
    series = dataframe[column]
    day = dataframe.index.floor("1D")
    if how == "high":
        return series.groupby(day).cummax()
    if how == "low":
        return series.groupby(day).cummin()
    if how == "open":
        return series.groupby(day).transform("first")
    if how == "close":
        # The developing daily close IS this bar's close.
        return series
    raise ValueError(f"unsupported daily aggregation {how!r}")


def _rolling_extreme(series, length, kind):
    """`highest` / `lowest` with Pine's `length < 1 -> na` edge."""
    if length < 1:
        return pd.Series(np.nan, index=series.index, dtype=float)
    if kind == "high":
        return ta.pine_highest(series, length)
    return ta.pine_lowest(series, length)


class SM52WeekHighLowBox_3556bf(PinePortBase, IStrategy):
    source_id = "SM_3556bf5382f000ca"
    source_file = "52周高低盒子交易策略52-Week-High-Low-Box-Trading-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"boxp": 5}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "request.security() is NOT modelled by the shared engine "
        "(PINE_SEMANTICS.md section 二.1). This port supplies the aligned series "
        "itself: the daily OHLC is aggregated from this frame's 1h bars by UTC "
        "calendar day, using the DEVELOPING daily value that security() without "
        "`lookahead` returns. The source is therefore an explicitly constructed "
        "(not silently 'fixed') mtf port. Tier 4.",
        "MODELLING CHOICE / equivalence risk: the alignment is 'the HTF value as "
        "of each chart bar's close, from no later data' -- D_High/D_Low are the "
        "day's running extremes, D_Open the day's first bar, D_Close this bar's "
        "close. The daily boundary is taken as UTC from the frame's own index "
        "(Pine uses the exchange timezone, PINE_SEMANTICS.md 3.4).",
        "REJECTED ALTERNATIVE, recorded not hidden: aligning the PREVIOUS "
        "COMPLETED day's OHLC onto the following day (the 'available only after "
        "the daily bar closes' reading of lookahead_off) makes the source "
        "structurally untradeable -- k1[1] == D_High for every intraday bar, so "
        "the only breakouts are at day boundaries, barssince()==boxp-2 therefore "
        "lands inside a constant day, and box1 = k3 < k2 is identically false. "
        "Zero boxes on any data. Only the original platform can settle which "
        "alignment FMZ used; the developing one is kept because it is both the "
        "documented lookahead_off reading and the only one under which the "
        "published strategy trades at all. See the report's blockers.",
        "A gap or a missing 1h bar changes the aggregated daily high/low/open "
        "relative to the venue's own daily candles, and a partial first or last "
        "day of the window is aggregated from fewer bars than the venue had. "
        "Neither is corrected; both are recorded.",
        "D_Open is assigned by the source and never used -- dead code, computed "
        "here as a column and likewise never read.",
        "k1[1] is the previous 1h BAR's k1 (the series the script is evaluated "
        "on), not the previous day's; highest/lowest/valuewhen/barssince/"
        "crossover all run on the 1h bar sequence over the daily series, exactly "
        "as Pine evaluates them on the chart's bars.",
        "A rolling window of length < 1 is na in Pine, so a boxp override below "
        "3 yields na windows instead of an exception.",
        "MD/SOURCE DISAGREEMENT 1: the md's prose says the stop loss is set near "
        "the previous range's upper/lower limit, but the code places no stop at "
        "all -- only the two strategy.entry calls. Code followed, disagreement "
        "recorded.",
        "MD/SOURCE DISAGREEMENT 2: the md calls this a 'last 5 days' box, which "
        "would require a daily chart; the header declares period: 1h, so "
        "highest(D_High, 5) is a 5-chart-bar window. Code followed.",
        "No strategy.close / strategy.exit / stop / limit exists, so "
        "source_reproduce_stops is False; both directions are entered, so "
        "can_short is True.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe, params):
        length = int(params["boxp"])

        d_high = _daily_developing(dataframe, "high", "high")
        d_low = _daily_developing(dataframe, "low", "low")
        d_close = _daily_developing(dataframe, "close", "close")
        d_open = _daily_developing(dataframe, "open", "open")

        lowest_low = _rolling_extreme(d_low, length, "low")
        k1 = _rolling_extreme(d_high, length, "high")
        k2 = _rolling_extreme(d_high, length - 1, "high")
        k3 = _rolling_extreme(d_high, length - 2, "high")

        breakout = (d_high > k1.shift(1)).fillna(False)
        nh = ta.pine_valuewhen(breakout, d_high, 0)
        box1 = (k3 < k2).fillna(False)
        box_ready = (ta.pine_barssince(breakout) == length - 2) & box1
        top_box = ta.pine_valuewhen(box_ready, nh, 0)
        bottom_box = ta.pine_valuewhen(box_ready, lowest_low, 0)

        dataframe["pine_daily_high"] = d_high
        dataframe["pine_daily_low"] = d_low
        dataframe["pine_daily_close"] = d_close
        # Assigned by the source and never read afterwards -- reproduced, unused.
        dataframe["pine_daily_open"] = d_open
        dataframe["pine_box_lowest"] = lowest_low
        dataframe["pine_box_k1"] = k1
        dataframe["pine_box_k2"] = k2
        dataframe["pine_box_k3"] = k3
        dataframe["pine_box_nh"] = nh
        dataframe["pine_box_ready"] = box_ready
        dataframe["pine_top_box"] = top_box
        dataframe["pine_bottom_box"] = bottom_box
        dataframe["pine_long_signal"] = ta.pine_crossover(d_close, top_box)
        dataframe["pine_short_signal"] = ta.pine_crossunder(d_close, bottom_box)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_signal": dataframe["pine_long_signal"].to_numpy(dtype=bool),
            "short_signal": dataframe["pine_short_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if crossover(D_Close, TopBox)
        #     strategy.entry("Long", strategy.long, comment="Long")
        if ctx["long_signal"][i]:
            broker.entry("Long", "long")
        # if crossunder(D_Close, BottomBox)
        #     strategy.entry("Short", strategy.short, comment="Short")
        if ctx["short_signal"][i]:
            broker.entry("Short", "short")
