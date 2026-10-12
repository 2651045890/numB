"""Port of sources/SM_bb8c1b65fb5cb6dc.pine (batch_001/Donchian渠道趋势跟踪策略Donchian-Channel-Trend-Following-Strategy.md).

Pine v5, `strategy(title="Donchian", overlay=true, calc_on_every_tick=true)`.
Two Donchian windows over CLOSE (a big one for entries, a small one for the
`strategy.close`), a stop whose initial distance is `stopOffset` ATRs and which
moves to break-even once open profit exceeds the position's risk, and sizing
that puts `risk_percent` of equity at risk over that stop distance:

    donch_len_big / donch_len_small     <- table on donch_string
    big_maxclose   = ta.highest(close, donch_len_big)
    big_minclose   = ta.lowest(close, donch_len_big)
    small_maxclose = ta.highest(close, donch_len_small)
    small_minclose = ta.lowest(close, donch_len_small)
    atrValue = ta.atr(atrLen)[1]            // PREVIOUS bar's ATR
    tradeWindow = true

    risk_usd     = (risk_percent / 100) * strategy.equity
    atr_currency = atrValue * syminfo.pointvalue
    notopen_qty  = risk_usd / (stopOffset * atr_currency)

    long_stop_price :=
       strategy.position_size > 0 and na(long_stop_price[1]) ? strategy.position_avg_price - stopOffset * atrValue :
       strategy.position_size > 0 and strategy.openprofit > risk_usd ? strategy.position_avg_price :
       strategy.position_size > 0 ? long_stop_price[1] :
       na
    short_stop_price := <mirror on position_size < 0, avg + stopOffset * atrValue>

    if strategy.position_size <= 0 and close == big_maxclose and close >= syminfo.mintick and tradeWindow and permit_long
        strategy.entry("Long",  strategy.long,  qty=notopen_qty)
    if strategy.position_size >= 0 and close == big_minclose and close >= syminfo.mintick and tradeWindow and permit_short
        strategy.entry("Short", strategy.short, qty=notopen_qty)

    if strategy.position_size > 0 and permit_stop
        strategy.exit(id="Stop", from_entry="Long", stop=long_stop_price)
    if strategy.position_size < 0 and permit_stop
        strategy.exit(id="Stop", from_entry="Short", stop=short_stop_price)

    if strategy.position_size > 0 and close == small_minclose and not barstate.islast
        strategy.close(id="Long", comment='Donch')
    if strategy.position_size < 0 and close == small_maxclose and not barstate.islast
        strategy.close(id="Short", comment='Donch')

    if close_in_end
        if not tradeWindow
            strategy.close_all(comment='In end')

`close == big_maxclose` is an exact float equality, and it is deterministic:
`ta.highest` / `ta.lowest` return a value that IS one of the window's closes, so
the comparison holds exactly when the current close is the window's extreme.
The same holds for the small window in the exit. Reproduced as written.

`ta.atr(atrLen)[1]` is the PREVIOUS bar's ATR -- `shift(1)`, not the current ATR
-- and it is the only ATR use in the source. On the first bar it is na, which
makes `notopen_qty` na and, in Pine, falls back to `default_qty_type` (fixed, 1
contract); the port reproduces that fallback.

`strategy.position_size <= 0` for the long and `>= 0` for the short mean both
sides may fire while a position is open on the OPPOSITE side; Pine nets such an
entry against the position (one reversing fill), which the engine reproduces.

THE `close_in_end` BLOCK IS DEAD CODE: `tradeWindow` is the literal `true` and
is never reassigned, so `not tradeWindow` is always false and `strategy.close_all`
is unreachable. `close_in_end` therefore changes nothing. Reproduced as
unreachable rather than "implemented".

The header declares `period: 1h` on Futures_Binance BTC_USDT, so `timeframe` is
"1h"; `basePeriod: 15m` is the FMZ backtester's own granularity for filling the
hourly bars, not the strategy's period.

FIDELITY:

* `calc_on_every_tick=true` is NOT modelled. The engine evaluates the script once
  per bar, at its close, so a bar's intrabar path is invisible: the source can
  see `close == big_maxclose`, `strategy.openprofit > risk_usd` and the
  `strategy.close` conditions on every tick DURING the bar and act then, while
  this port only ever sees the bar's final close. Where an intrabar touch of the
  entry condition later reverses before the bar closes, the source enters and
  this port does not (and vice versa for the two closes); the break-even stop
  move can likewise land a bar earlier on the source. Recorded as a blocker
  below -- it cannot be recovered from OHLCV.
* `not barstate.islast` in the two `strategy.close` guards is modelled as
  always-true. `barstate.islast` is true only on the final bar of the LOADED
  series, which the engine cannot distinguish from any other last row of a
  prefix; keeping the conjunct would make the ledger's exits depend on where the
  data happens to end and would fail the causality prefix check. Impact: at most
  one terminal `strategy.close` is emitted on the very last bar that the source
  would skip. Every other bar is identical. Recorded, not hidden.
* `strategy.exit` is a RESTING stop (PINE_SEMANTICS.md 二.11) and is faithfully
  reproduced: `source_reproduce_stops = True` routes the engine's level into the
  ledger's `pine_stop_level`, so the framework exits inside the bar at the same
  price. `strategy.exit` is re-issued every bar with the (possibly ratcheted)
  level; the engine replaces a same-id exit rather than stacking copies, which is
  Pine's own rule.
* `strategy.exit(stop=na)` on an unreachable bar would place no leg; the port
  skips the call instead of resting a legless order. Unreachable here: the stop
  is assigned on every bar the position is open, and `atrValue` is finite by the
  time any position can exist (an entry needs a full big window first).
* The `long_stop_price[1]` / `short_stop_price[1]` self-references are Pine `var`
  carries. They are held in the context state, initialised na so the first bar of
  a position takes the `avg_price -/+ stopOffset * atrValue` branch, exactly as
  the source's `na(long_stop_price[1])` test does.
* `risk_usd` is read from `broker.equity` at the bar's close, the same quantity
  `strategy.equity` holds when the source sizes the order. The framework is
  handed the engine's recorded fill notional rather than a re-derived one
  (PINE_SEMANTICS.md 1.4).
* An na or zero-divisor `notopen_qty` maps to None and the engine then sizes with
  `strategy.fixed` / 1 contract, which is what Pine does with `qty = na`.
* `syminfo.mintick` is modelled as 0.1 (BTC/USDT's increment): `close >= 0.1` is
  effectively always true on this symbol. `syminfo.pointvalue` is the literal 1.0
  for BINANCE:BTCUSDT and only scales the stop distance into the quantity.
* `bgcolor`, the five `plot()` calls and the `s1`/`s2`/`s3` line series are
  display-only, as are `cross_up` / `cross_dn` in every use OTHER than the entry
  conditions (the two variables are the entry conditions spelled out once more).
* `comment='Donch'` is display-only; the engine's `close` ignores it.
* `strategy()` declares only title/overlay/calc_on_every_tick, so
  `strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
  pyramiding 0 and `process_orders_on_close=false` are Pine's defaults. `qty` is
  passed explicitly, so the default quantity only binds when `notopen_qty` is na.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures that rounding separately rather
  than treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# donch_string -> (donch_len_big, donch_len_small), transcribed from the source's
# two ternary chains. Anything else is na in the source, i.e. both windows are na
# and no condition can hold.
DONCH_LENGTHS = {
    "50/20": (50, 20),
    "50/50": (50, 50),
    "20/20": (20, 20),
    "20/10": (20, 10),
    "100/100": (100, 100),
}


def _level(value) -> float | None:
    """An na level is no level: the engine wants None, not a NaN."""
    if value is None:
        return None
    value = float(value)
    return value if np.isfinite(value) else None


def _pine_ratio(numerator: float, denominator: float) -> float | None:
    """Pine's `/` with na semantics: na in, or a zero divisor, yields na."""
    if not np.isfinite(numerator) or not np.isfinite(denominator) or denominator == 0.0:
        return None
    return numerator / denominator


class SMDonchianChannelTrendFollowing_bb8c1b(PinePortBase, IStrategy):
    source_id = "SM_bb8c1b65fb5cb6dc"
    source_file = "Donchian渠道趋势跟踪策略Donchian-Channel-Trend-Following-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "donch_string": "20/10",
        "permit_long": True,
        "permit_short": True,
        "risk_percent": 0.5,
        "stopOffset": 2.0,
        "atrLen": 20,
        "close_in_end": True,
        "permit_stop": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # strategy.exit(id="Stop", stop=...) is a real resting stop: the engine's
    # level is mirrored into pine_stop_level so the framework exits inside the
    # bar at the same price.
    source_reproduce_stops = True
    source_mintick = 0.1
    source_fidelity_notes = [
        "calc_on_every_tick=true is NOT modelled: the engine evaluates the script "
        "once per bar at its close, so the source can act on an intrabar touch of "
        "close == big_maxclose / strategy.openprofit > risk_usd / the two closes "
        "that this port only sees at the bar's final close. Cannot be recovered "
        "from OHLCV; recorded as the port's blocker.",
        "`not barstate.islast` in the two strategy.close guards is modelled as "
        "always-true. barstate.islast is true only on the final bar of the loaded "
        "series, which the engine cannot tell apart from the last row of a prefix; "
        "keeping it would make the ledger depend on where the data ends and fail "
        "the causality prefix check. Impact: at most one terminal strategy.close is "
        "emitted that the source would skip; every other bar is identical.",
        "The close_in_end block is dead code: tradeWindow is the literal true and "
        "is never reassigned, so `not tradeWindow` is always false and "
        "strategy.close_all is unreachable. Reproduced as unreachable.",
        "close == big_maxclose (and the small-window exit) is an exact float "
        "equality and is deterministic: ta.highest / ta.lowest return a value that "
        "IS one of the window's closes, so the comparison holds exactly when the "
        "current close is the window's extreme. Reproduced as written.",
        "ta.atr(atrLen)[1] is the PREVIOUS bar's ATR (shift(1)); on the first bar "
        "it is na, which makes notopen_qty na and falls back to the declared "
        "default_qty_type (fixed, 1 contract) -- the same thing Pine does with "
        "qty = na. An na or zero-divisor notopen_qty therefore maps to None.",
        "strategy.exit(id='Stop', stop=...) is a resting stop (PINE_SEMANTICS 2.11) "
        "and is faithfully reproduced: source_reproduce_stops routes the level to "
        "pine_stop_level so the framework exits inside the bar. The exit is "
        "re-issued every bar with the ratcheted level; the engine replaces a "
        "same-id exit rather than stacking copies, which is Pine's own rule.",
        "long_stop_price[1] / short_stop_price[1] are Pine var carries, held in the "
        "context state and initialised na so the first bar of a position takes the "
        "avg_price -/+ stopOffset*atrValue branch, exactly as the source's "
        "na(long_stop_price[1]) test does.",
        "The break-even move (strategy.openprofit > risk_usd -> stop := "
        "position_avg_price) is evaluated at the bar's close; with "
        "calc_on_every_tick the source could move it intrabar, one bar earlier. "
        "Same blocker as above.",
        "risk_usd reads strategy.equity at the bar close and the framework is handed "
        "the engine's recorded fill notional rather than a re-derived one "
        "(PINE_SEMANTICS.md 1.4).",
        "syminfo.mintick is modelled as 0.1 (BTC/USDT's increment), so close >= "
        "0.1 is effectively always true on this symbol; syminfo.pointvalue is the "
        "literal 1.0 for BINANCE:BTCUSDT.",
        "bgcolor, the five plot() calls, the s1/s2/s3 line series and "
        "comment='Donch' are display-only. cross_up / cross_dn are the entry "
        "conditions spelled out a second time and are used only for those entries "
        "in the script.",
        "strategy() declares only title/overlay/calc_on_every_tick, so "
        "strategy.fixed / 1 contract, initial capital 1000000, commission 0%, "
        "pyramiding 0 and process_orders_on_close=false are Pine's defaults; qty is "
        "explicit, so the default quantity binds only when notopen_qty is na.",
        "strategy.exit(stop=na) would place no leg; the port skips the call instead "
        "of resting a legless order. Unreachable here -- the stop is assigned on "
        "every bar the position is open and atrValue is finite before any position "
        "can exist.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures that rounding "
        "separately rather than treating it as a signal difference.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        lengths = DONCH_LENGTHS.get(str(params["donch_string"]))

        if lengths is None:
            # Pine: ta.highest(close, na) is na, so both windows are na and every
            # condition that reads them is false. Only reachable from a
            # donch_string outside the declared options.
            empty = pd.Series(np.nan, index=dataframe.index, dtype=float)
            big_maxclose = big_minclose = small_maxclose = small_minclose = empty
        else:
            donch_len_big, donch_len_small = lengths
            big_maxclose = ta.pine_highest(close, donch_len_big)
            big_minclose = ta.pine_lowest(close, donch_len_big)
            small_maxclose = ta.pine_highest(close, donch_len_small)
            small_minclose = ta.pine_lowest(close, donch_len_small)

        # atrValue = ta.atr(atrLen)[1] -- the PREVIOUS bar's ATR.
        atr_value = ta.pine_atr(dataframe, int(params["atrLen"])).shift(1)

        dataframe["pine_big_maxclose"] = big_maxclose
        dataframe["pine_big_minclose"] = big_minclose
        dataframe["pine_small_maxclose"] = small_maxclose
        dataframe["pine_small_minclose"] = small_minclose
        dataframe["pine_atr_value"] = atr_value
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "big_maxclose": dataframe["pine_big_maxclose"].to_numpy(dtype=float),
            "big_minclose": dataframe["pine_big_minclose"].to_numpy(dtype=float),
            "small_maxclose": dataframe["pine_small_maxclose"].to_numpy(dtype=float),
            "small_minclose": dataframe["pine_small_minclose"].to_numpy(dtype=float),
            "atr_value": dataframe["pine_atr_value"].to_numpy(dtype=float),
            "risk_fraction": float(params["risk_percent"]) / 100.0,
            "stop_offset": float(params["stopOffset"]),
            "permit_long": bool(params["permit_long"]),
            "permit_short": bool(params["permit_short"]),
            "permit_stop": bool(params["permit_stop"]),
            "mintick": float(self.source_mintick),
            # syminfo.pointvalue for BINANCE:BTCUSDT is 1.
            "pointvalue": 1.0,
            # tradeWindow is the literal true and is never reassigned.
            "trade_window": True,
            # `long_stop_price = 0.0` / `short_stop_price = 0.0` and their `[1]`
            # self-references: the carries start na (there is no bar -1).
            "state": {"long_stop": float("nan"), "short_stop": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        position_size = broker.position_size
        state = ctx["state"]

        # risk_usd = (risk_percent / 100) * strategy.equity
        risk_usd = broker.equity * ctx["risk_fraction"]
        atr_value = float(ctx["atr_value"][i])
        stop_offset = ctx["stop_offset"]
        pointvalue = ctx["pointvalue"]
        # notopen_qty = risk_usd / (stopOffset * atrValue * pointvalue)
        notopen_qty = _pine_ratio(risk_usd, stop_offset * (atr_value * pointvalue))

        # ---- long stop: initial ATR stop, then break-even once the profit beats
        # ---- the risk, then carried. na while flat.
        prev_long_stop = state["long_stop"]
        if position_size > 0 and not np.isfinite(prev_long_stop):
            long_stop_price = broker.position_avg_price - stop_offset * atr_value
        elif position_size > 0 and broker.open_profit > risk_usd:
            long_stop_price = broker.position_avg_price
        elif position_size > 0:
            long_stop_price = prev_long_stop
        else:
            long_stop_price = float("nan")
        state["long_stop"] = long_stop_price

        # ---- short stop: the mirror.
        prev_short_stop = state["short_stop"]
        if position_size < 0 and not np.isfinite(prev_short_stop):
            short_stop_price = broker.position_avg_price + stop_offset * atr_value
        elif position_size < 0 and broker.open_profit > risk_usd:
            short_stop_price = broker.position_avg_price
        elif position_size < 0:
            short_stop_price = prev_short_stop
        else:
            short_stop_price = float("nan")
        state["short_stop"] = short_stop_price

        # ---- entry orders. `close == big_maxclose` is the exact float equality
        # ---- the source uses; a NaN window compares false, as na does.
        if (
            position_size <= 0
            and close == ctx["big_maxclose"][i]
            and close >= ctx["mintick"]
            and ctx["trade_window"]
            and ctx["permit_long"]
        ):
            broker.entry("Long", "long", qty=notopen_qty)

        if (
            position_size >= 0
            and close == ctx["big_minclose"][i]
            and close >= ctx["mintick"]
            and ctx["trade_window"]
            and ctx["permit_short"]
        ):
            broker.entry("Short", "short", qty=notopen_qty)

        # ---- exit orders: one resting stop per side, re-issued at the carried
        # ---- level. An na stop places no leg, so the call is skipped.
        if position_size > 0 and ctx["permit_stop"]:
            level = _level(long_stop_price)
            if level is not None:
                broker.exit("Stop", from_entry="Long", stop=level)

        if position_size < 0 and ctx["permit_stop"]:
            level = _level(short_stop_price)
            if level is not None:
                broker.exit("Stop", from_entry="Short", stop=level)

        # ---- strategy.close on the small window. `not barstate.islast` is
        # ---- modelled as always true (see FIDELITY).
        if position_size > 0 and close == ctx["small_minclose"][i]:
            broker.close("Long", comment="Donch")

        if position_size < 0 and close == ctx["small_maxclose"][i]:
            broker.close("Short", comment="Donch")

        # ---- if close_in_end: if not tradeWindow: strategy.close_all(...)
        # ---- tradeWindow is the literal true, so this branch never runs.
