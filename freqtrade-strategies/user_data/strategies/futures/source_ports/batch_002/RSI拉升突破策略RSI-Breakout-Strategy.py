"""Port of sources/SM_02fdde5cc49135a9.pine (batch_002/RSI拉升突破策略RSI-Breakout-Strategy.md).

Pine v4 (`//@version=4`), on the `/*backtest` header's 1h period. The source
marks the start of the trading day with a session filter, measures the day's
range from that marker, and takes a breakout of it while RSI agrees with the
breakout's direction:

    T1    = time(timeframe.period, "0915-0916")   // day marker
    Z1    = valuewhen(T1, bar_index, 0)           // that marker's bar_index
    L     = bar_index - Z1 + 1                    // bars since the marker
    tim   = time(timeframe.period, "1015-1510")   // entry window
    exitt = time(timeframe.period, "1511-1530")   // forced-flat window
    upper = highest(L); lower = lowest(L)         // the day's range so far
    rsi   = hand-written Wilder RSI(close, 14)
    vwma20 = vwma(close, 20)

    if (upper == high) and rsi > 50 and tim and close > open
        strategy.entry("Buy", strategy.long, comment="Buy")
    strategy.close("Buy", when = close < vwma(close, 20) or exitt)
    if (lower == low) and rsi < 50 and tim and close < open
        strategy.entry("Sell", strategy.short, comment="Sell")
    strategy.close("Sell", when = close > vwma(close, 20) or exitt)

`strategy()` declares only `title`, `shorttitle` and `overlay`, so every
property is Pine's documented default: `strategy.fixed` / 1 contract, initial
capital 1000000, commission 0%, `pyramiding 0`, `process_orders_on_close=false`.
The two `strategy.entry` calls therefore size 1 contract each, and a second
entry in a direction that is already open is refused by `pyramiding 0` -- so a
breakout bar that repeats while the position is already on that side adds
nothing.

The order of the four calls is the source's and is preserved: entry, then the
Long close, then the Short entry, then the Short close. That order is what
`pine_script` reproduces; the engine fills same-bar pending orders in creation
order (PINE_SEMANTICS.md 1.13).

FIDELITY:

* SESSION MEMBERSHIP IS THE BAR'S OPENING TIME. `time(timeframe.period,
  session)` is na when the bar is not in the session, and TradingView defines
  that on the bar's opening time: the function "returns a UNIX timestamp for
  the opening time of the current bar, or na if the bar is not in the specified
  session", and the Sessions page counts "all bars that start within the
  session" -- its Notice asks for session bounds aligned with bar bounds for
  exactly that reason. The port therefore tests
  `start <= minute_of_day < end` on the bar's OPEN, not an intersection of the
  session with the bar's own extent. This is also the reading the corpus's
  other session guard implements (batch_001/HMA...: `(_minutes >= start) &
  (_minutes < end)`).
* ON THE DECLARED 1h PERIOD NONE OF THE THREE SESSIONS EVER FIRES. Every 1h bar
  opens at the top of an hour, and none of those :00 instants lies inside a
  window that begins at :15 or :11 -- so "0915-0916" (the day marker),
  "1015-1510" (`tim`) and "1511-1530" (`exitt`) each match no bar at all,
  whatever a bar's own extent may overlap. `T1` is therefore na on every bar,
  `Z1` never becomes a number, `L` stays na, `highest(na)` / `lowest(na)` are
  na, so `upper == high` and `lower == low` are false everywhere and the source
  places NO order on this period. The three session strings are written for
  bars whose open falls exactly on them -- an "0915-0916" window is a 09:15 day
  marker, the NSE open the md describes -- which no 1h bar is. Reproduced
  as-is: `pine_marker` is a constant-false column and both conditions are
  constant false.
* THE DECLARED PLATFORM WOULD DISAGREE, AND IS RECORDED NOT ADOPTED. The
  `/*backtest` header is FMZ's, and FMZ's Pine reference states of `time()`'s
  `session` parameter that "FMZ does not support this". If the session
  arguments were dropped, every bar would be in session: `L` constantly 1, so
  the day range collapses to a single bar (`upper == high`, `lower == low`),
  `tim` always true and `exitt` always true, and the strategy degenerates to
  "RSI agrees with the candle" plus a same-bar forced close. That is a platform
  implementation gap rather than the semantics of the source's own language,
  and this corpus models the Pine chart model, not the FMZ runtime
  (sm_event.py). Adopting it here would also silently rewrite all 82
  session-using sources of the corpus, so it is a corpus-level decision left
  open; recorded as a blocker rather than decided inside this port.
* `time()` uses the exchange timezone in Pine; this port reads the candle times
  as they arrive (local OKX/Binance data is UTC). PINE_SEMANTICS.md 3.4.
* The day is anchored to the 09:15 MARKER, not to midnight: `L` counts bars
  since the last marker, so `upper` / `lower` would be the range of the bars
  from that marker up to the current bar. The md's "当日最高价/最低价" is that
  marker-anchored range, not the calendar day's -- but a marker only exists on
  a period where a bar opens inside 09:15-09:16, and the declared 1h period has
  none, so neither extreme ever becomes a number here.
* `highest(L)` / `lowest(L)` take a SERIES length (`L` changes every bar), which
  is why they are computed here as running extremes since the marker rather
  than with `pine_ta.pine_highest` / `pine_lowest` (fixed-window helpers).
  With no marker on this period `Z1` stays na, so `L` is na on every bar and
  both extremes are na.
* `upper == high` / `lower == low` are exact float comparisons against the
  running maximum/minimum, as in the source; they are not "close enough" tests.
* The RSI is the source's own hand-written v4 formula, including its `down == 0
  ? 100 : up == 0 ? 0 : ...` guards, reproduced literally instead of calling
  `pine_ta.pine_rsi`. The two agree on the values here (the guards reproduce the
  same boundaries), but the source's arithmetic is what is on the record.
  `len = 14` is a literal in the source and stays a literal.
* `vwma(close, 20)` needs the volume series, which is handed to
  `pine_ta.pine_vwma` through the source series' `attrs`; the 20-bar window is
  the source's literal.
* `time()` on the FIRST bars: there is no bar on this period at which the
  marker makes `L` a number, so the RSI and VWMA warmups (14 and 20 bars) never
  become a signal source either. na propagates and every comparison against na
  is false, so the warmup is inert rather than signal-generating.
* `strategy.close` is a MARKET close in Pine and is projected as an exit
  signal, not as a resting level, so `source_reproduce_stops` is False: the
  source has no `strategy.exit` and no stop/limit leg at all, and the "止损线"
  the md describes is implemented as a close condition, not as a broker stop.
* `tim` and `exitt` are written as adjacent windows ("1015-1510" then
  "1511-1530"), so on a period whose bars open inside them an entry and its
  close could land on one bar and fill at the same next-open price -- the
  zero-length round trip of PINE_SEMANTICS.md 1.13. On the declared 1h period
  `exitt` matches no bar at all, so that overlap does not arise here: the only
  close condition that is ever true is the VWMA one, and no entry is ever
  placed for it to close. The two windows are disjoint in the source, so
  `tim` and `exitt` cannot both be true on any bar of any period.
* can_short is True -- the source has a real `strategy.entry("Sell",
  strategy.short)`. The md's "限定交易时间" claim that trading stops at 15:10 is
  the `tim` filter; the source's forced flat is the separate `exitt` session.
* The `comment="Buy"` / `comment="Sell"` arguments are display-only.
* The `/*backtest` header's `basePeriod: 15m` is the FMZ backtester's own
  granularity for filling 1h bars, not the strategy's period; the FMZ runtime
  question above is the only place it matters.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _session_bounds(spec: str) -> tuple[int, int]:
    """`"0915-0916"` -> (555, 556) minutes after midnight."""
    start, _, end = spec.partition("-")
    return int(start[:2]) * 60 + int(start[2:]), int(end[:2]) * 60 + int(end[2:])


def _in_session(index: pd.DatetimeIndex, spec: str) -> np.ndarray:
    """Whether each bar's OPEN time falls inside the session.

    This is `time(timeframe.period, session)`: the function "returns a UNIX
    timestamp for the opening time of the current bar, or na if the bar is not
    in the specified session", and the Sessions page counts "all bars that start
    within the session". Membership is a property of the bar's open, not of the
    bar's [open, open + timeframe) extent -- so a session that no bar opens
    inside is false on every bar, which is what the Sessions page's Notice to
    align session bounds with bar bounds exists to warn about.
    """
    start, end = _session_bounds(spec)
    minute_of_day = index.hour.to_numpy() * 60 + index.minute.to_numpy()
    return (minute_of_day >= start) & (minute_of_day < end)


def _range_since_marker(marker: np.ndarray, high: np.ndarray,
                        low: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """`highest(L)` / `lowest(L)` with `L = bar_index - Z1 + 1`.

    The window is [Z1, i], so it restarts at every marker and grows by one bar
    afterwards: a running maximum/minimum since the marker is the same value
    without an O(L) rescan per bar. `length` is `L` itself, i.e. na until the
    first marker has been seen (then `Z1` is na and `lowest(na)` is na).
    """
    count = len(high)
    length = np.full(count, np.nan)
    upper = np.full(count, np.nan)
    lower = np.full(count, np.nan)
    start = -1
    run_high = np.nan
    run_low = np.nan
    for i in range(count):
        if marker[i]:
            start = i
            run_high = high[i]
            run_low = low[i]
        elif start < 0:
            continue
        else:
            run_high = max(run_high, high[i])
            run_low = min(run_low, low[i])
        length[i] = i - start + 1
        upper[i] = run_high
        lower[i] = run_low
    return upper, lower, length


class SMRsiBreakout_02fdde(PinePortBase, IStrategy):
    source_id = "SM_02fdde5cc49135a9"
    source_file = "RSI拉升突破策略RSI-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    # No input() call in the source: every length and both sessions are
    # literals, so there is nothing to override.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Session membership is the bar's OPEN time inside the session: "
        "`time(timeframe.period, session)` \"returns a UNIX timestamp for the "
        "opening time of the current bar, or na if the bar is not in the "
        "specified session\", and the Sessions page counts \"all bars that "
        "start within the session\". The predicate is "
        "`start <= minute_of_day < end`; it is NOT an intersection of the "
        "session with the bar's [open, open+timeframe) extent (an earlier "
        "version of this port invented that rule and then cited it as "
        "TradingView's -- it is not, and it is what put the day marker on the "
        "09:00 bar). PINE_SEMANTICS.md 3.4 covers the timezone half: `time()` "
        "uses the exchange timezone, this port reads the candle times as "
        "delivered (UTC for local OKX/Binance data).",
        "Consequence on the declared 1h period: no bar opens inside any of "
        "\"0915-0916\", \"1015-1510\" or \"1511-1530\" (every 1h bar opens on "
        "the hour), so the marker never fires, `L` is na on every bar, "
        "`highest(na)` / `lowest(na)` are na and both entry conditions are "
        "false everywhere -- the source places NO order on this period and the "
        "port reproduces that. The windows are written for bars that open "
        "exactly on them (an \"0915-0916\" marker is the 09:15 NSE open the md "
        "describes). validate_pine therefore reports the port as ran but never "
        "signalled on synthetic data.",
        "The declared platform would disagree, and that is recorded, not "
        "adopted: the `/*backtest` header is FMZ's and FMZ's Pine reference "
        "documents `time()`'s `session` parameter as unsupported there, which "
        "would make all three sessions inert (`L` constantly 1, `tim` and "
        "`exitt` constantly true, the day range collapsed to one bar). That is "
        "a platform implementation gap rather than the semantics of the "
        "source's own language, and the corpus models the Pine chart model, not "
        "the FMZ runtime (sm_event.py); adopting it would silently rewrite all "
        "82 session-using sources. Recorded as a blocker; corpus-level decision.",
        "The day is anchored to the 09:15 marker, not to midnight: `L` counts "
        "bars since the last marker, so the range would be the bars from that "
        "marker to the current bar -- but no bar on this period opens inside "
        "09:15-09:16, so neither extreme is ever a number here.",
        "`highest(L)` / `lowest(L)` take a series length; computed as running "
        "extremes since the marker (the same window [Z1, i]) instead of the "
        "fixed-window pine_ta helpers. na on every bar of this period because "
        "no marker ever fires.",
        "`upper == high` / `lower == low` are exact comparisons, as in the "
        "source.",
        "The RSI is the source's own v4 formula with its `down == 0 ? 100 : "
        "up == 0 ? 0` guards, written out rather than delegated to "
        "pine_ta.pine_rsi (the values agree; the source's arithmetic is the "
        "recorded one). `len = 14` is a source literal.",
        "`vwma(close, 20)`: the volume series is passed through the source "
        "series' attrs, which is how pine_ta.pine_vwma resolves it.",
        "No `strategy.exit` and no stop/limit leg exist -- both exits are "
        "market `strategy.close` calls, projected as exit signals -- so "
        "source_reproduce_stops is False. The md's \"止损线\" (VWMA) is a close "
        "condition in the code, not a broker stop.",
        "`tim` and `exitt` are adjacent, disjoint windows (`1015-1510`, "
        "`1511-1530`), so no bar can be in both: the zero-length round trip of "
        "PINE_SEMANTICS.md 1.13 cannot arise from these sessions. (An earlier "
        "version of this port claimed a 15:00 overlap and attributed it to the "
        "shared projection layer; that overlap existed only in the discarded "
        "intersection model, which mapped \"1511-1530\" onto the 15:00 bar.) "
        "On this period `exitt` matches no bar at all, so the only close "
        "condition ever true is the VWMA one, and no entry is ever placed.",
        "md/source: the md calls this a strategy for Indian index futures "
        "(Nifty/Bank Nifty) and describes buying the day's high break, while "
        "the header backtests Futures_Binance BTC_USDT and the code's \"day\" "
        "is marker-anchored, not a calendar day. Also: the md's step 1 says "
        "trading is limited to 10:15-15:10, which is the `tim` filter; the "
        "forced flat is the separate `exitt` session. Code followed, both "
        "records kept.",
        "`comment=\"Buy\"` / `comment=\"Sell\"` are display-only; plot() calls "
        "(including the VWMA plot) place no condition.",
        "No stop/limit order exists, so nothing rests; the engine's "
        "`pine_stop_level` / `pine_limit_level` stay empty for this port.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        index = dataframe.index
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        close = dataframe["close"]
        open_ = dataframe["open"]

        # T1 = time(timeframe.period, "0915-0916"); Y = bar_index;
        # Z1 = valuewhen(T1, bar_index, 0); L = Y - Z1 + 1
        marker = _in_session(index, "0915-0916")
        bar_index = pd.Series(
            np.arange(len(dataframe), dtype=float), index=index, name="pine_bar_index"
        )
        upper, lower, length = _range_since_marker(marker, high, low)

        # tim = time(timeframe.period, "1015-1510")
        # exitt = time(timeframe.period, "1511-1530")
        window = _in_session(index, "1015-1510")
        forced_flat = _in_session(index, "1511-1530")

        # len = 14 / src = close / up = rma(max(change(src), 0), len)
        # down = rma(-min(change(src), 0), len)
        # rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
        rsi_len = 14
        change = ta.pine_change(close, 1)
        up = ta.pine_rma(change.clip(lower=0.0), rsi_len)
        down = ta.pine_rma((-change).clip(lower=0.0), rsi_len)
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = 100.0 - (100.0 / (1.0 + up / down))
        rsi = pd.Series(
            np.where(down == 0, 100.0, np.where(up == 0, 0.0, ratio)),
            index=index, dtype=float,
        )
        # na must stay na: the ternary chain above evaluates on numbers, so the
        # warmup tail (where up/down are undefined) is restored explicitly.
        rsi = rsi.where(up.notna() & down.notna())

        # plot(vwma(close, 20)) -- the plot is display-only, but the SAME
        # expression is the close condition, so it is computed once here.
        close_with_volume = close.copy()
        close_with_volume.attrs["volume"] = dataframe["volume"]
        vwma20 = ta.pine_vwma(close_with_volume, 20)

        dataframe["pine_marker"] = marker
        dataframe["pine_bar_index"] = bar_index
        dataframe["pine_length"] = length
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_rsi"] = rsi
        dataframe["pine_vwma20"] = vwma20
        dataframe["pine_buy_condition"] = (
            (upper == high) & (rsi > 50) & window & (close > open_)
        )
        dataframe["pine_sell_condition"] = (
            (lower == low) & (rsi < 50) & window & (close < open_)
        )
        dataframe["pine_close_buy"] = (close < vwma20) | forced_flat
        dataframe["pine_close_sell"] = (close > vwma20) | forced_flat
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_condition": dataframe["pine_buy_condition"].to_numpy(),
            "sell_condition": dataframe["pine_sell_condition"].to_numpy(),
            "close_buy": dataframe["pine_close_buy"].fillna(False).to_numpy(),
            "close_sell": dataframe["pine_close_sell"].fillna(False).to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ((upper==high) and rsi>50 and tim and close>open)
        #     strategy.entry("Buy", strategy.long, comment="Buy")
        if ctx["buy_condition"][i]:
            broker.entry("Buy", "long")
        # strategy.close("Buy", when = close < vwma(close,20) or exitt)
        broker.close("Buy", when=bool(ctx["close_buy"][i]))
        # if ((lower==low) and rsi<50 and tim and close<open)
        #     strategy.entry("Sell", strategy.short, comment="Sell")
        if ctx["sell_condition"][i]:
            broker.entry("Sell", "short")
        # strategy.close("Sell", when = close > vwma(close,20) or exitt)
        broker.close("Sell", when=bool(ctx["close_sell"][i]))
