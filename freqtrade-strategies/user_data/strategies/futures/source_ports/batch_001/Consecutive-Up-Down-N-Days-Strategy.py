"""Port of sources/SM_efd7dbe1e7f00fcd.pine (batch_001/Consecutive-Up-Down-N-Days-Strategy.md).

Pine v4. Two consecutive-bar counters drive a pair of STOP (breakout) entries:

    ups = close > close[1] ? nz(ups[1]) + 1 : 0
    dns = close < close[1] ? nz(dns[1]) + 1 : 0

    if (ups >= consecutiveBarsUp)  and time_cond
        strategy.entry("Long",  strategy.long,  stop = high + syminfo.mintick, ...)
    if (dns >= consecutiveBarsDown) and time_cond
        strategy.entry("Short", strategy.short, stop = low  + syminfo.mintick, ...)

Both counters are the SAME recursion written twice: an up bar resets `dns` to 0
and increments `ups`, and vice versa, so with the declared defaults of 1 bar the
two conditions are mutually exclusive (they can both be false when close equals
close[1], and can never both be true). The whole file is `strategy.entry` -- and
nothing else. There is NO exit call of any kind: no `strategy.exit`, no
`strategy.close`, no `strategy.close_all`, and no commented-out one either. The
position is therefore only ever changed by the next entry, which nets against it
(PINE_SEMANTICS.md 1.1: a reverse `strategy.entry` closes the old side and opens
the order's own quantity on the new side).

BOTH ENTRIES ARE RESTING `stop=` ORDERS, NOT MARKET ORDERS. The long rests at
`high + mintick` (a buy-stop above the signal bar's high) and the short at
`low + mintick` (a sell-stop at the signal bar's low). They fill on a LATER bar,
not on the next bar's open, and PINE_SEMANTICS.md section 二 11 records that a
resting entry cannot be projected onto a framework whose only entry is a
next-open market order. The engine's own ledger fills them at the right bar and
the right price; the `enter_long` / `enter_short` columns are the projection,
and they are placed on the bar the order was CREATED. Expect the chain
comparison to disagree about entry timing for that reason, not because of a
translation error.

`strategy()` IS COMMENTED OUT (source line 12). A commented-out line declares
nothing -- the same rule PINE_SEMANTICS.md 1.17 applies to commented-out exit
lines -- so Pine's documented defaults are in force: `strategy.fixed` / 1
contract, initial capital 1000000, commission 0%, `pyramiding = 0`,
`process_orders_on_close = false`. The commented line asks for something
different (initial_capital = 10000, `default_qty_type = strategy.cash` with
`default_qty_value = 10000`) and it is recorded in `source_fidelity_notes`
rather than applied.

MD/SOURCE MISMATCHES (recorded, source followed):

* The md's prose is wrong about both entries. It says "This is a long-only
  strategy that determines entries and exits based on user-defined consecutive
  up days and consecutive down days" and "When ups reaches consecutiveBarsUp,
  we go long. When dns reaches consecutiveBarsDown, we EXIT positions." The
  source's active code has no exit at all, and its second entry is
  `strategy.entry("Short", strategy.short, ...)`, i.e. a SHORT ENTRY, not an
  exit. The commented-out `strategy.risk.allow_entry_in(strategy.direction.long)`
  on line 15 shows the author's own intent was long-only, but it is commented
  out and inert (and `strategy.risk.*` is unmodelled anyway, PINE_SEMANTICS.md
  section 二 3). `can_short` is True because the source opens shorts.
* The md's argument table renders both `input(1)` defaults as `true`. In Pine
  v4 an integer literal makes an integer input, so the declared defaults are
  the integers 1 and 1, which is what this port carries.
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


def _consecutive(up_or_down: np.ndarray) -> np.ndarray:
    """Pine's `x := cond ? nz(x[1]) + 1 : 0`.

    `x[1]` on the first bar is na and `nz()` turns it into 0, but the first
    bar's condition is false anyway (it compares against an na `close[1]`), so
    a plain carry of the running count is exact. The `x = 0.0` line above each
    of the two assignments is a fresh declaration, not `var`, so the count
    never survives a bar on which the condition fails.
    """
    values = np.asarray(up_or_down, dtype=bool)
    out = np.zeros(values.shape[0], dtype=float)
    run = 0.0
    for i, flag in enumerate(values):
        run = run + 1.0 if flag else 0.0
        out[i] = run
    return out


class SMConsecutiveUpDownNDays_efd7db(PinePortBase, IStrategy):
    source_id = "SM_efd7dbe1e7f00fcd"
    source_file = "Consecutive-Up-Down-N-Days-Strategy.md"
    timeframe = "12h"
    # The source's active code holds strategy.entry("Short", strategy.short, ...)
    # in addition to the long one, so the port can hold a short.
    can_short = True
    source_defaults: dict = {
        # consecutiveBarsUp = input(1)   -- integer input (the md renders it `true`)
        "consecutiveBarsUp": 1,
        # consecutiveBarsDown = input(1)
        "consecutiveBarsDown": 1,
        # startDate = input(timestamp("2021-01-01T00:00:00"), type=input.time)
        # READ BY NOTHING in the source: `time_cond` is the bare literal `true`
        # (line 32), so there is no date window and every bar is eligible. Kept
        # so the input is not silently dropped.
        "startDate": "2021-01-01T00:00:00",
        # finishDate = input(timestamp("2021-12-31T00:00:00"), type=input.time)
        "finishDate": "2021-12-31T00:00:00",
        # message_buy = input("{{strategy.order.alert_message}}", title="Buy message")
        "message_buy": "{{strategy.order.alert_message}}",
        # message_sell = input("{{strategy.order.alert_message}}", title="Sell message")
        "message_sell": "{{strategy.order.alert_message}}",
    }
    # The ONLY strategy() declaration in the file (line 12) is commented out, so
    # it declares nothing: Pine's documented defaults apply. The commented line
    # asks for initial_capital = 10000, default_qty_type = strategy.cash and
    # default_qty_value = 10000; none of that is in force.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No exit call of any kind exists in the source -- no stop, limit or trail
    # leg for the engine to mirror, and no market close either.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NO EXITS AT ALL. The source is two `strategy.entry` calls and nothing "
        "else: no strategy.exit, no strategy.close, no strategy.close_all, and "
        "no commented-out exit line either. The only way the position ever "
        "changes is the next entry netting against it (PINE_SEMANTICS.md 1.1). "
        "source_reproduce_stops is False because there is no stop/limit/trail "
        "leg to mirror; the framework is still sent the reversal legs the "
        "engine's own ledger produces.",
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 12) is COMMENTED OUT, and the two strategy.entry calls are the "
        "author's own active code carrying an `alert_message=` argument and a "
        "`stop=` level -- nothing a converter template appends. The "
        "tier_reason's 'declares indicator()/study(), tool appended "
        "strategy.entry pair; NO exits' is false on the first two counts (the "
        "NO exits part is true). The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 12), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED: the commented "
        "line asks for initial_capital = 10000, default_qty_type = "
        "strategy.cash with default_qty_value = 10000 -- i.e. an all-in stake "
        "of 10000 cash per entry on a 10000 account, which is a completely "
        "different sizing rule from 1 contract. PINE_SEMANTICS.md 1.6 makes "
        "initial_capital load-bearing (it decides how much the venue's contract "
        "step eats), so the fork is recorded rather than quietly resolved.",
        "MD/SOURCE MISMATCH (entries): the md says the strategy is long-only "
        "and that `dns >= consecutiveBarsDown` EXITS the long. The source's "
        "active code has no exit and its second call is "
        "strategy.entry(\"Short\", strategy.short, stop = low + syminfo.mintick) "
        "-- a SHORT ENTRY. can_short is therefore True. The md's claim matches "
        "the COMMENTED-OUT strategy.risk.allow_entry_in(strategy.direction.long) "
        "on line 15, which is inert (and strategy.risk.* is unmodelled, "
        "PINE_SEMANTICS.md section 二 3).",
        "MD/SOURCE MISMATCH (rendered defaults): the md's argument table renders "
        "v_input_1 and v_input_2 (the two `input(1)` calls) as `true`. An "
        "integer literal in Pine v4 makes an integer input, so the defaults are "
        "1 and 1 as carried here; the difference is invisible at runtime because "
        "`ups >= 1` and `ups >= true` agree, but the declared types differ.",
        "time_cond = true is a bare literal (source line 32). The startDate / "
        "finishDate inputs above it are never read, so there is no date window "
        "-- the port carries the conjunct as the constant True rather than "
        "dropping it, and records both timestamp() inputs so they are not "
        "silently lost. (PINE_SEMANTICS.md section 二 8: input.time windows are "
        "not applied by this layer; here it does not matter, because the source "
        "never applies it either.)",
        "Both entries are RESTING stop orders, not market orders: the long "
        "rests at high + mintick, the short at low + mintick, and each fills on "
        "a later bar at the stop price (or at the open when the bar gaps "
        "through it). PINE_SEMANTICS.md section 二 11 records that such an entry "
        "cannot be projected onto the framework: the projection can only emit "
        "enter_long / enter_short on the bar the order was CREATED, and "
        "Freqtrade then fills at the next open. The engine's ledger is "
        "faithful; the projected signal columns are not, structurally.",
        "syminfo.mintick is a venue property, not a source constant; "
        "TradingView reads it off the symbol. BTC/USDT:USDT quotes in 0.1, so "
        "source_mintick = 0.1 and the two stop levels are high + 0.1 and "
        "low + 0.1. A different mintick would move both levels.",
        "alert_message = message_buy / message_sell, and the message_buy / "
        "message_sell alert-string inputs themselves, are trading-irrelevant "
        "(PINE_SEMANTICS.md section 二 7) and are not forwarded to the engine; "
        "they are carried in source_defaults for provenance only.",
        "pyramiding = 0 (Pine's default): the engine refuses a same-direction "
        "entry at CREATION time, so while a long is open a second `Long` order "
        "is not placed, is not projected and never fills; the opposite "
        "direction is still allowed and reverses (PINE_SEMANTICS.md 1.1). With "
        "the declared default of 1 bar both counters fire on nearly every bar, "
        "so this gate -- not the counters -- is what decides how often the "
        "position actually changes.",
        "`ups` / `dns` are declared `ups = 0.0` and then assigned with `:=` "
        "inside the same bar; without `var` the declaration re-runs every bar, "
        "so the count is a pure function of the two closes and the previous "
        "bar's count. Reproduced as a per-bar carry; nz(x[1]) on the first bar "
        "would be 0 and the first bar's condition is false anyway.",
        "The /*backtest header names Futures_Binance / BTC_USDT while the "
        "repo's chain verification uses BTC/USDT:USDT -- a venue mapping, not a "
        "source property. Leverage, margin, liquidation, funding and the "
        "venue's contract-step rounding are not modelled (PINE_SEMANTICS.md 1.6 "
        "measures the step rounding separately). The header's `basePeriod: 15m` "
        "is the FMZ backtester's own fill granularity, not the strategy period.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]

        # price = close
        price = close
        # ups := price > price[1] ? nz(ups[1]) + 1 : 0
        up_bar = (price > price.shift(1)).fillna(False).to_numpy(dtype=bool)
        # dns := price < price[1] ? nz(dns[1]) + 1 : 0
        down_bar = (price < price.shift(1)).fillna(False).to_numpy(dtype=bool)

        dataframe["pine_ups"] = _consecutive(up_bar)
        dataframe["pine_dns"] = _consecutive(down_bar)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "high": dataframe["high"].to_numpy(dtype=float),
            "low": dataframe["low"].to_numpy(dtype=float),
            "ups": dataframe["pine_ups"].to_numpy(dtype=float),
            "dns": dataframe["pine_dns"].to_numpy(dtype=float),
            "bars_up": float(params["consecutiveBarsUp"]),
            "bars_down": float(params["consecutiveBarsDown"]),
            # time_cond = true  (the startDate / finishDate inputs above it are
            # never read, so there is no date window)
            "time_cond": True,
            "mintick": float(self.source_mintick),
        }

    def pine_script(self, broker, i, ctx):
        # if (ups >= consecutiveBarsUp) and time_cond
        if (ctx["ups"][i] >= ctx["bars_up"]) and ctx["time_cond"]:
            # strategy.entry("Long", strategy.long, stop = high + syminfo.mintick,
            #                alert_message = message_buy)
            broker.entry("Long", "long", stop=float(ctx["high"][i]) + ctx["mintick"])

        # if (dns >= consecutiveBarsDown) and time_cond
        if (ctx["dns"][i] >= ctx["bars_down"]) and ctx["time_cond"]:
            # strategy.entry("Short", strategy.short, stop = low + syminfo.mintick,
            #                alert_message = message_sell)
            broker.entry("Short", "short", stop=float(ctx["low"][i]) + ctx["mintick"])
