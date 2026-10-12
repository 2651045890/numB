"""Port of sources/SM_48ce0df7ec53a7e7.pine
(batch_001/10EMA双重交叉趋势追踪策略10EMA-Double-Cross-Trend-Tracking-Strategy.md).

Pine v5, on the `/*backtest` header's 1d period. A 10/50 EMA cross arms a
price level, and a later "confirmation" candle fires a resting stop-limit entry
guarded by a trailing scalp exit:

    t1 = time(timeframe.period, "0930-1500")
    sema = ta.ema(close, 10) ; lema = ta.ema(close, 50) ; hema = ta.ema(close, 200)
    bullcrosscount = ta.barssince(ta.crossover(sema, lema))
    bearcrosscount = ta.barssince(ta.crossunder(sema, lema))
    ideallong  = bullcrosscount <= 5
    idealshort = bearcrosscount <= 5
    emabull = sema > lema and bearish and close > sema and close > hema
              and ideallong and t1 and barstate.isconfirmed
    emabear = sema < lema and bullish and close < sema and close < hema
              and idealshort and t1 and barstate.isconfirmed
    xemabull = ta.barssince(emabull) ; xemabear = ta.barssince(emabear)
    dbullema = emabull and emabull[1] and xemabull <= 1
    dbearema = emabear and emabear[1] and xemabear <= 1
    bullentry = dbullema ? ta.valuewhen(emabull[1], high + 0.05, 0)
                         : ta.valuewhen(emabull,     high + 0.05, 0)
    bullentryh   = dbullema ? bullentry[1] : bullentry
    bullentrylow = ta.valuewhen(emabull, low - 0.05, 0)
    bullstop   = (bullentryh - bullentrylow) <= 1.00 ? bullentryh - 1.00
               : (bullentryh - bullentrylow) <= 10.40 ? bullentrylow : na
    bulltarget = (bullentryh - bullstop) * 1.62 + bullentryh
    ... the bear side mirrors it, with bearentryhigh = valuewhen(emabear, high+0.05)
    bullclose = (xemabull <= 7) and bullish and bullcrosscount >= 1 and barstate.isconfirmed
    bearclose = (xemabear <= 7) and bearish and bearcrosscount >= 1 and barstate.isconfirmed
    idealbuy  = close >= bullentryh and bullclose and (ta.barssince(bullclose) <= 7)
    idealsell = close <= bearentryh and bearclose and (ta.barssince(bearclose) <= 7)

    if idealbuy
        strategy.close("sell", comment=na)
        strategy.entry("buy", strategy.long, limit=bullentryh, stop=bullstop)
    strategy.exit("exit","buy", trail_points=low, trail_offset=5, qty_percent=100,
                  limit=bulltarget, stop=bullstop)
    if idealsell
        strategy.close("buy", comment=na)
        strategy.entry("sell", strategy.short, limit=bearentryh, stop=bearstop)
    strategy.exit("exit","sell", trail_points=low, trail_offset=5, qty_percent=100,
                  limit=beartarget, stop=bearstop)

`strategy()` declares only `title`, `overlay` and `format`, so every property is
Pine's documented default: `strategy.fixed` / 1 contract, initial capital
1000000, commission 0%, `pyramiding 0`, `process_orders_on_close=false`. The
`basePeriod: 1h` in the header is the FMZ backtester's own fill granularity, not
the strategy's period.

FIDELITY -- WHAT THE SOURCE DOES, AND WHAT THE ENGINE CANNOT CARRY.

* Both `strategy.entry` calls are STOP-LIMIT orders: Pine places a stop and, on
  the trigger, a limit. The engine's `_price_order_fill` reads only the stop leg
  of such an order (`if order.stop is not None: ... return`), so the port's
  entries fill at the stop (or the bar's open when the bar gaps through it) and
  the `limit=` leg is inert (PINE_SEMANTICS.md 2.11). For THIS source the two
  legs point the same way -- a long's limit sits above its stop, a short's below
  -- so the two models agree except on a bar that opens beyond the limit, where
  Pine books the limit and the engine books the open.
* `strategy.exit("exit", ...)` is called TWICE per bar with the SAME id, for
  `from_entry="buy"` and then `from_entry="sell"`. The engine keeps one order
  per id (`PineBroker._place` drops the same-id predecessor), so the sell leg
  placed second REPLACES the buy leg every bar, on every bar. `_try_fill_pending`
  then skips an exit whose `from_entry` is not open and publishes no level for
  it, so the LONG position never has a resting stop or take-profit in the
  ledger, while the SHORT position does. The long side is therefore closed only
  by the market `strategy.close("buy")`, and its stop/target/trail are not
  reproduced at all. This is a load-bearing consequence of the shared id, not a
  port choice; if TradingView keeps the two legs apart (id+from_entry), the
  long side would trade differently. Recorded as a blocker rather than resolved.
* `trail_points = low` is a PRICE, not a point distance: the trail arms only once
  the bar extreme is `low` away from the entry, which for BTC means never.
  Reproduced by passing `low` through, so the engine's ratchet never arms and
  the trail is inert -- as in the source.
* `trail_offset = 5` and the engine's ratchet live on the ORDER, and a same-id
  re-place restarts the ratchet (PINE_SEMANTICS.md 3.6). A source that re-places
  its trail every bar -- this one does -- therefore never ratchets across bars.
  Whether the original platform carries the ratchet across a replacement is
  unverified; recorded, not guessed.
* `qty_percent=100` cannot be passed to the engine's `exit()` (no such
  parameter). The engine's exits always close the whole position, which is what
  `qty_percent=100` asks for, so nothing is lost here.
* `t1 = time(timeframe.period, "0930-1500")` tests the bar's OPENING time.
  Pine's `time()` "returns a UNIX timestamp for the opening time of the current
  bar, or na if the bar is not in the specified session", and the Sessions page
  counts "all bars that start within the session"; so `_in_session` tests
  `start <= minute_of_day < end` on the bar's OPEN, never an intersection of the
  session with the bar's own extent. This is the model the corpus's other
  session guards use (batch_002/RSI-breakout after its own correction, and
  batch_001/HMA: `(_minutes >= start) & (_minutes < end)`).
* ON THIS SOURCE'S DECLARED 1d PERIOD THE SESSION NEVER MATCHES, SO THE SOURCE
  PLACES NO TRADE ON A SYMBOL WITHOUT A REAL TRADING SESSION. A daily candle on
  a 7x24 pair -- BTC/USDT:USDT here -- opens at 00:00, whose minute-of-day 0 is
  not in [570, 900). `t1` is therefore na on EVERY daily bar, `emabull` /
  `emabear` never become true, `idealbuy` / `idealsell` never fire, and the port
  places ZERO orders. The source's window is a MARKET-HOURS window -- its own
  comment reads "last hour of market is not ideal for trading" -- written for
  an instrument that has a real session; it is not a 24/7 filter, and 0 trades
  is the faithful result on a 24/7 symbol.
* THE EARLIER REVISION OF THIS PORT INVENTED AN INTERSECTION RULE, AND IT
  MANUFACTURED SIGNALS. It modelled `time(timeframe.period, session)` as the
  session meeting the bar's [open, open + timeframe) extent, under which the
  09:30-15:00 window on a 1440-minute bar was "always contained": `t1` read TRUE
  on every bar, the session filter was a no-op, and the port booked trades the
  source does not place (engine 3 / framework 3 closed on BTC/USDT:USDT 1d,
  20240101-20250101). That rule had been adopted from the batch_002 port before
  that port was itself corrected. It is removed here, and `_TIMEFRAME_MINUTES`
  -- which existed only to feed it -- went with it. The trade counts are NOT
  fudged to keep the port trading.
* `barstate.isconfirmed` is always true on historical bars, so the conjunct is
  a no-op in both Pine and the port.
* `bullcandle` / `bearcandle` (`ta.valuewhen(bullish/bearish, close, 0)`) and
  `offsetema` are computed by the source and never read. They are kept as
  columns / a recorded default so the formula set is on the record.
* `and` on series in Pine is short-circuit-free and na-propagating; every
  comparison here is `na -> false`, and the port's Series comparisons give
  exactly that (`ta.barssince` is na until its first true, so `ideallong` /
  `idealshort` are false until the first cross).
* `ta.ema` seeding is TradingView-internal and unpublished; `pine_ta.pine_ema`
  seeds from the first non-na observation (PINE_SEMANTICS.md 3.1). All three
  EMAs and both crosses carry that choice.
* The md's prose says the auxiliary filter is "the 10EMA on the HOURLY chart in
  an uptrend". The code has no `request.security` at all: `hema` is
  `ta.ema(src, 200)` on the chart's own timeframe and the filter is
  `close > hema`, a level comparison, not a rising slope. The input's title
  ("hourly 10 ema") and the md's description are both leftovers from the hourly
  original. Source wins; recorded, not corrected.
* The md's `Strategy Arguments` table renders the Offset default as `false`; the
  source declares `input.int(defval=0)`. The source wins.
* `plotshape` calls are display-only and are not reproduced. The commented-out
  line/label blocks are NOT restored.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

SESSION = "0930-1500"


def _session_bounds(spec: str) -> tuple[int, int]:
    """`"0930-1500"` -> (570, 900) minutes after midnight."""
    start, _, end = spec.partition("-")
    return int(start[:2]) * 60 + int(start[2:]), int(end[:2]) * 60 + int(end[2:])


def _in_session(index: pd.DatetimeIndex, spec: str) -> np.ndarray:
    """Whether each bar's OPEN time falls inside the session.

    This is `time(timeframe.period, session)`: the function "returns a UNIX
    timestamp for the opening time of the current bar, or na if the bar is not
    in the specified session", and the Sessions page counts "all bars that start
    within the session". Membership is a property of the bar's open, NOT of the
    bar's [open, open + timeframe) extent, so a session that no bar opens inside
    is false on every bar -- precisely what the Sessions page's Notice to align
    session bounds with bar bounds warns about.
    """
    start, end = _session_bounds(spec)
    minute_of_day = index.hour.to_numpy() * 60 + index.minute.to_numpy()
    return (minute_of_day >= start) & (minute_of_day < end)


def _level(value) -> float | None:
    """A Pine order level, with na mapped to "no level" (Pine's own meaning)."""
    if value is None:
        return None
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    return value if np.isfinite(value) else None


def _prev(series: pd.Series) -> pd.Series:
    """`series[1]` -- Pine's previous-bar reference, na on the first bar."""
    return series.shift(1)


def _prev_bool(series: pd.Series) -> pd.Series:
    """`series[1]` as a boolean: Pine's na -> false in a boolean context."""
    return series.shift(1).fillna(False).astype(bool)


def _truthy(series: pd.Series) -> pd.Series:
    """Pine's boolean context: na compares false, so na becomes False."""
    return series.fillna(False).astype(bool)


class SM10EmaDoubleCross_48ce0d(PinePortBase, IStrategy):
    source_id = "SM_48ce0df7ec53a7e7"
    source_file = (
        "10EMA双重交叉趋势追踪策略"
        "-10EMA-Double-Cross-Trend-Tracking-Strategy.md"
    )
    timeframe = "1d"
    # The source really does carry a short entry (`strategy.entry("sell",
    # strategy.short, ...)`), reached on the bearish mirror of the long setup.
    can_short = True
    source_defaults: dict = {
        "ema1": 10,
        "ema2": 50,
        "ema3": 200,
        "src": "close",
        "offsetema": 0,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # strategy.exit(stop=..., limit=...) exists, so the engine's stop and
    # take-profit levels are what the framework must reproduce.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "Both entries are stop-limit orders in Pine; the engine reads only the "
        "stop leg and treats limit= as inert (PINE_SEMANTICS.md 2.11). The two "
        "legs point the same way here, so they differ only on a bar that opens "
        "beyond the limit.",
        "strategy.exit('exit', ...) is called twice per bar with the SAME id "
        "(from_entry 'buy' then 'sell'). The engine keeps one order per id, so "
        "the sell leg replaces the buy leg on every bar, and the long position "
        "never carries a resting stop or take-profit in the ledger. Longs exit "
        "only through the market strategy.close('buy'). Load-bearing, and "
        "recorded as a blocker.",
        "trail_points = low is a price, not a point distance, so the trail can "
        "never arm; passed through unchanged so the engine's ratchet stays "
        "inert too.",
        "A same-id re-place restarts the engine's trail ratchet, and this "
        "source re-places its exit every bar, so the ratchet never carries "
        "across bars (PINE_SEMANTICS.md 3.6). Unverified against the original.",
        "qty_percent=100 has no engine parameter; the engine's exits always "
        "close the whole position, which is what 100% asks for.",
        "t1 = time(timeframe.period, '0930-1500') tests the bar's OPENING time "
        "(Pine: time() returns the bar's opening timestamp, or na if the bar is "
        "not in the session). On the 1d period a daily candle opens at 00:00, "
        "whose minute-of-day is not in [570, 900), so t1 is na on every bar, "
        "emabull/emabear never become true and the port places ZERO trades on "
        "BTC/USDT:USDT. The source's window is a market-hours window for an "
        "instrument with a real session, not a 24/7 filter; 0 trades is the "
        "faithful result here.",
        "An earlier revision of this port modelled t1 as a range intersection "
        "between the session and the bar's [open, open+1d) extent -- a rule "
        "adopted from the batch_002 port before that port was corrected. It "
        "made the filter a no-op and manufactured trades (engine 3 / framework "
        "3) the source does not place. Removed; _TIMEFRAME_MINUTES is gone.",
        "barstate.isconfirmed is always true historically, so that conjunct is "
        "a no-op.",
        "bullcandle / bearcandle and the offsetema input are computed and never "
        "read; kept for the record. The commented-out line/label blocks are NOT "
        "restored.",
        "ta.ema seeding is TradingView-internal and unpublished; all three EMAs "
        "and both crosses inherit pine_ta's first-non-na seeding "
        "(PINE_SEMANTICS.md 3.1).",
        "The md describes the auxiliary filter as 'the 10EMA on the hourly "
        "chart in an uptrend'. There is no request.security in the source: "
        "hema is ta.ema(src, 200) on the chart's own timeframe and the test is "
        "close > hema. The input title and the md are leftovers from the "
        "hourly original.",
        "The md's argument table renders the Offset default as 'false'; the "
        "source declares input.int(defval=0). Source wins.",
        "The bear stop's second test is sign-flipped in the source "
        "((bearentryh - bearentryhigh) <= 10.40), so it is true almost always "
        "and bearstop is bearentryhigh; the bull test uses the same sign as its "
        "first branch and can reach na. Reproduced literally.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        open_ = dataframe["open"]
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        times = dataframe.index
        if not isinstance(times, pd.DatetimeIndex):
            times = pd.to_datetime(dataframe["date"])
        # t1 = time(timeframe.period, "0930-1500"): the bar's OPEN time must lie
        # inside the session. On this source's 1d period it never does, so this
        # column is constant false -- see the docstring's FIDELITY note.
        t1 = pd.Series(
            _in_session(times, SESSION),
            index=dataframe.index,
        )

        # barstate.isconfirmed is true on every historical bar.
        bullish = _truthy(close > open_)
        bearish = _truthy(open_ > close)

        # bullcandle / bearcandle: computed by the source, never read.
        bullcandle = ta.pine_valuewhen(bullish, close, 0)
        bearcandle = ta.pine_valuewhen(bearish, close, 0)

        ema1 = int(params["ema1"])
        ema2 = int(params["ema2"])
        ema3 = int(params["ema3"])
        sema = ta.pine_ema(close, ema1)
        lema = ta.pine_ema(close, ema2)
        hema = ta.pine_ema(close, ema3)

        bullcrosscount = ta.pine_barssince(ta.pine_crossover(sema, lema))
        bearcrosscount = ta.pine_barssince(ta.pine_crossunder(sema, lema))
        ideallong = _truthy(bullcrosscount <= 5)
        idealshort = _truthy(bearcrosscount <= 5)

        emabull = _truthy(
            (sema > lema) & bearish & (close > sema) & (close > hema)
            & ideallong & t1
        )
        emabear = _truthy(
            (sema < lema) & bullish & (close < sema) & (close < hema)
            & idealshort & t1
        )
        emabull_prev = _prev_bool(emabull)
        emabear_prev = _prev_bool(emabear)
        xemabull = ta.pine_barssince(emabull)
        xemabear = ta.pine_barssince(emabear)
        dbullema = _truthy(emabull & emabull_prev & (xemabull <= 1))
        dbearema = _truthy(emabear & emabear_prev & (xemabear <= 1))

        # bullentry = if dbullema: valuewhen(emabull[1], ...) else valuewhen(emabull, ...)
        bullentry = ta.pine_valuewhen(emabull_prev, high + 0.05).where(
            dbullema, ta.pine_valuewhen(emabull, high + 0.05)
        )
        # bullentryh = dbullema ? bullentry[1] : bullentry
        bullentryh = _prev(bullentry).where(dbullema, bullentry)
        bullentrylow = ta.pine_valuewhen(emabull, low - 0.05)
        # (h - l) <= 1.00 ? h - 1.00 : (h - l) <= 10.40 ? l : na
        bull_span = bullentryh - bullentrylow
        bullstop = (bullentryh - 1.00).where(
            bull_span <= 1.00, bullentrylow.where(bull_span <= 10.40)
        )
        bulltarget = (bullentryh - bullstop) * 1.62 + bullentryh

        bearentry = ta.pine_valuewhen(emabear_prev, low - 0.05).where(
            dbearema, ta.pine_valuewhen(emabear, low - 0.05)
        )
        bearentryh = _prev(bearentry).where(dbearema, bearentry)
        bearentryhigh = ta.pine_valuewhen(emabear, high + 0.05)
        # (high - h) <= 1.00 ? h + 1.00 : (h - high) <= 10.40 ? high : na
        bear_span = bearentryhigh - bearentryh
        bearstop = (bearentryh + 1.00).where(
            bear_span <= 1.00, bearentryhigh.where((-bear_span) <= 10.40)
        )
        beartarget = bearentryh - (bearstop - bearentryh) * 1.62

        bullclose = _truthy((xemabull <= 7) & bullish & (bullcrosscount >= 1))
        bearclose = _truthy((xemabear <= 7) & bearish & (bearcrosscount >= 1))
        buyzone = ta.pine_barssince(bullclose)
        shortzone = ta.pine_barssince(bearclose)
        idealbuy = _truthy((close >= bullentryh) & bullclose & (buyzone <= 7))
        idealsell = _truthy((close <= bearentryh) & bearclose & (shortzone <= 7))

        for name, series in (
            ("pine_t1", t1.astype(int)),
            ("pine_bullish", bullish.astype(int)),
            ("pine_bearish", bearish.astype(int)),
            ("pine_bullcandle", bullcandle),
            ("pine_bearcandle", bearcandle),
            ("pine_sema", sema),
            ("pine_lema", lema),
            ("pine_hema", hema),
            ("pine_bullcrosscount", bullcrosscount),
            ("pine_bearcrosscount", bearcrosscount),
            ("pine_emabull", emabull.astype(int)),
            ("pine_emabear", emabear.astype(int)),
            ("pine_xemabull", xemabull),
            ("pine_xemabear", xemabear),
            ("pine_dbullema", dbullema.astype(int)),
            ("pine_dbearema", dbearema.astype(int)),
            ("pine_bullentryh", bullentryh),
            ("pine_bullentrylow", bullentrylow),
            ("pine_bullstop", bullstop),
            ("pine_bulltarget", bulltarget),
            ("pine_bearentryh", bearentryh),
            ("pine_bearentryhigh", bearentryhigh),
            ("pine_bearstop", bearstop),
            ("pine_beartarget", beartarget),
            ("pine_bullclose", bullclose.astype(int)),
            ("pine_bearclose", bearclose.astype(int)),
            ("pine_idealbuy", idealbuy.astype(int)),
            ("pine_idealsell", idealsell.astype(int)),
        ):
            dataframe[name] = series
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "low": dataframe["low"].to_numpy(dtype=float),
            "idealbuy": dataframe["pine_idealbuy"].to_numpy(dtype=bool),
            "idealsell": dataframe["pine_idealsell"].to_numpy(dtype=bool),
            "bull_entryh": dataframe["pine_bullentryh"].to_numpy(dtype=float),
            "bull_stop": dataframe["pine_bullstop"].to_numpy(dtype=float),
            "bull_target": dataframe["pine_bulltarget"].to_numpy(dtype=float),
            "bear_entryh": dataframe["pine_bearentryh"].to_numpy(dtype=float),
            "bear_stop": dataframe["pine_bearstop"].to_numpy(dtype=float),
            "bear_target": dataframe["pine_beartarget"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # if idealbuy
        #     strategy.close("sell", comment=na)
        #     strategy.entry("buy", strategy.long, limit=bullentryh, stop=bullstop)
        if ctx["idealbuy"][i]:
            broker.close("sell")
            broker.entry(
                "buy", "long",
                limit=_level(ctx["bull_entryh"][i]),
                stop=_level(ctx["bull_stop"][i]),
            )
        # strategy.exit("exit","buy", trail_points=low, trail_offset=5,
        #               qty_percent=100, limit=bulltarget, stop=bullstop)
        # Called unconditionally, every bar, exactly as the source does.
        broker.exit(
            "exit", "buy",
            trail_points=float(ctx["low"][i]), trail_offset=5.0,
            limit=_level(ctx["bull_target"][i]),
            stop=_level(ctx["bull_stop"][i]),
        )
        # if idealsell
        #     strategy.close("buy", comment=na)
        #     strategy.entry("sell", strategy.short, limit=bearentryh, stop=bearstop)
        if ctx["idealsell"][i]:
            broker.close("buy")
            broker.entry(
                "sell", "short",
                limit=_level(ctx["bear_entryh"][i]),
                stop=_level(ctx["bear_stop"][i]),
            )
        # strategy.exit("exit","sell", ...) -- same id, so it replaces the
        # "buy" leg above on every bar the engine processes.
        broker.exit(
            "exit", "sell",
            trail_points=float(ctx["low"][i]), trail_offset=5.0,
            limit=_level(ctx["bear_target"][i]),
            stop=_level(ctx["bear_stop"][i]),
        )
