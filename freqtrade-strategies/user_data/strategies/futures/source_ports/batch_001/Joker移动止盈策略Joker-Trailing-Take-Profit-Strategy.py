"""Port of sources/SM_8593237acfa02842.pine
(batch_001/Joker移动止盈策略Joker-Trailing-Take-Profit-Strategy.md).

Pine v5 -- "Joker Trailing TP Bot". Two SMAs of `close` (23 / 50) drive the
direction, and every position carries a take-profit that is either a resting
limit or a trailing stop:

    fastMA = ta.sma(close, 23)
    slowMA = ta.sma(close, 50)
    isWithinPeriod    = true                       // literal; see FIDELITY
    openLongPosition  = isWithinPeriod and ta.crossover(fastMA, slowMA)
    openShortPosition = isWithinPeriod and ta.crossunder(fastMA, slowMA)
    longIsActive      = openLongPosition  or strategy.position_size > 0
    shortIsActive     = openShortPosition or strategy.position_size < 0

    float longTakeProfitPrice = na
    longTakeProfitPrice := if longIsActive
        if openLongPosition and not (strategy.position_size > 0)
            close * (1 + longTakeProfitPerc)
        else
            nz(longTakeProfitPrice[1], close * (1 + longTakeProfitPerc))
    else
        na

    float shortTakeProfitPrice = na
    shortTakeProfitPrice := if shortIsActive
        if openShortPosition and not (strategy.position_size < 0)
            close * (1 - shortTakeProfitPerc)
        else
            nz(shortTakeProfitPrice[1], close * (1 - shortTakeProfitPrice))
    else
        na

`longTakeProfitPrice` is therefore latched on the bar the crossover fires --
`close * (1 + 0.5%)` of THAT bar -- and then carried forward by the `nz(...[1],
...)` self-reference for as long as the leg stays active. `shortTakeProfitPrice`
is the same machine, except that the source's own fallback argument is
`close * (1 - shortTakeProfitPrice)` rather than `...(1 - shortTakeProfitPerc)`.

`fromDate` / `toDate` are declared and then never read: `isWithinPeriod` is the
literal `true`, so the session filter is inert and both sides trade at any
bar. Carried as declared inputs and nothing else -- not restored to a working
filter.

Timeframe "1h" from the `/*backtest` header (`period: 1h`); the header's
`basePeriod: 15m` is the backtester's fill granularity and is not modelled.

FIDELITY: see `source_fidelity_notes` -- chiefly the two conversions the engine
cannot take verbatim (`trail_price` is an absolute price in Pine while
pine_engine exposes `trail_points` as a distance from the position's average
entry price, and Pine's tick-unit arguments have to be turned into prices) and
the na `strategy.position_avg_price` on the entry's own fill bar.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMJokerTrailingTakeProfit_859323(PinePortBase, IStrategy):
    source_id = "SM_8593237acfa02842"
    source_file = "Joker移动止盈策略Joker-Trailing-Take-Profit-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        # input(timestamp('01 Jan 2021 00:00 UTC'), 'From Date')  -- never read
        "fromDate": "2021-01-01T00:00:00Z",
        # input(timestamp('31 Dec 2121 23:59 UTC'), 'To Date')    -- never read
        "toDate": "2121-12-31T23:59:00Z",
        # input.int(23, 'Fast SMA Length')
        "fastMALen": 23,
        # input.int(50, 'Slow SMA Length')
        "slowMALen": 50,
        # input.float(0.5, 'Long Take Profit %', ...) * 0.01
        "longTakeProfitPerc": 0.5,
        # input.float(0.5, 'Short Take Profit %', ...) * 0.01
        "shortTakeProfitPerc": 0.5,
        # input.bool(true, 'Enable Trailing')
        "enableTrailing": True,
        # input.float(0.01, 'Trailing Take Profit %', ...) * 0.01
        "trailingTakeProfitPerc": 0.01,
    }
    # strategy(commission_type=strategy.commission.percent, commission_value=0.07,
    #          default_qty_type=strategy.percent_of_equity, default_qty_value=100,
    #          initial_capital=1000, pyramiding=0, process_orders_on_close=false,
    #          close_entries_rule='ANY', calc_on_every_tick=false,
    #          calc_on_order_fills=false, currency=currency.USD)
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.07
    source_pyramiding = 0
    source_initial_capital = 1_000.0
    # `syminfo.mintick` is read off the symbol by the platform and is stated
    # nowhere in the source; the engine's declared BTC/USDT:USDT tick is used.
    source_mintick = 0.1
    source_reproduce_stops = True
    source_fidelity_notes = [
        "`trail_price` is an ABSOLUTE price in Pine; the engine's `trail_points` "
        "is a distance from the position's average entry price (it arms on "
        "`(bar_extreme - avg_price) * side >= trail_points`). The port converts: "
        "`(trail_price - position_avg_price) * side`. That is the only mapping "
        "the engine's interface accepts, and it is a modelling step, not "
        "something the source states.",
        "Consequence of the conversion above, on an entry's OWN fill bar: the "
        "distance is computed on the bar the exit order is CREATED, from "
        "`strategy.position_avg_price` as it stands there, while pine_engine "
        "applies that stored distance against `position_avg_price` as it stands "
        "on the bar the order is EVALUATED. (a) Flat on the creation bar (a "
        "from-flat entry): the distance is na, so the trail cannot arm on that "
        "one fill bar and the engine misses an activation Pine's absolute "
        "`trail_price` would have allowed. (b) A position was already open on "
        "the creation bar -- and every crossover but the first is a REVERSAL, "
        "so this is the ordinary case: the distance is anchored to the OLD "
        "position's average entry price, so the engine's activation threshold "
        "on that bar is `trail_price + (new_avg - old_avg)` rather than "
        "`trail_price`, and it can miss an activation or take one earlier "
        "depending on that sign. Only the one fill bar is affected, because the "
        "port re-places the order there (`longIsActive` / `shortIsActive` are "
        "true); pine_engine's interface has no absolute-price form of the "
        "trail, so this is not repairable in the port. Measured on the "
        "3000-bar synthetic run: 4 of 53 round trips open and close on the same "
        "bar, i.e. the engine does take fill-bar trail exits, with the stale "
        "anchor case (b) in force.",
        "Pine's `trail_offset` (and `trail_points`, had the source used tick "
        "form) is in TICKS; the engine reads both as price distances, so the "
        "source's `longTrailingTakeProfitStepTicks = longTakeProfitPrice * "
        "trailingTakeProfitPerc / syminfo.mintick` is multiplied back by "
        "`mintick` before being handed over. `syminfo.mintick` itself is not "
        "stated in the source; 0.1 (the engine's BTC/USDT:USDT tick) is assumed "
        "and is load-bearing for the trailing distance.",
        "`nz(shortTakeProfitPrice[1], close * (1 - shortTakeProfitPrice))` is "
        "kept verbatim, typo and all: the long leg's fallback is "
        "`close * (1 + longTakeProfitPerc)` while the short leg's fallback "
        "references `shortTakeProfitPrice` -- the PRICE series being assigned, "
        "not the percentage. `shortTakeProfitPrice` has no `var` and is "
        "re-initialised to `na` on every bar, so a same-bar self-reference "
        "resolves to that `na` (Pine's documented rule for a non-`var` "
        "self-reference) and the fallback argument is itself na; nz then "
        "degrades to its first argument. NOT 'corrected' to `...Perc`.",
        "`fromDate` / `toDate` are `input(timestamp(...))` values the source "
        "never reads -- `bool isWithinPeriod = true` is a literal, so the date "
        "gate is always open and both sides trade in any period. The inputs are "
        "carried as declared parameters only; no filter was invented.",
        "`close_entries_rule='ANY'` cannot change any outcome here: with "
        "`pyramiding=0` at most one entry is open per direction, so ANY and "
        "FIFO select the same entry.",
        "`process_orders_on_close=false`, `calc_on_every_tick=false` and "
        "`calc_on_order_fills=false` all match the engine's model (the script "
        "runs once per closed bar, orders placed there fill at the next bar's "
        "open).",
        "MEASURED on the 3000-bar synthetic run: `pine_stop_level` and "
        "`pine_limit_level` are nan on EVERY bar (0 non-nan values each), while "
        "the engine books 53 round trips of which 45 exit at a trailing level "
        "rather than at a bar open. Both follow from the point above -- the "
        "engine records a resting exit's trail level BEFORE that bar's arming "
        "test, and this source re-places the order every bar, so the level is "
        "unarmed at the moment it is recorded. The Pine-engine ledger is the "
        "authoritative reproduction; a consumer that reads only the published "
        "levels sees a hold-only strategy.",
        "pine_engine replaces a same-id `strategy.exit` order wholesale, so the "
        "trailing ratchet restarts on every bar the source re-places it; the "
        "source re-places it every bar `longIsActive` / `shortIsActive` is "
        "true, so only a same-bar arm-and-trigger is reachable. Whether the "
        "original platform keeps the ratchet across a same-id replacement is "
        "UNPUBLISHED (PINE_SEMANTICS 3.6); the engine's choice is recorded, not "
        "changed.",
        "`currency=currency.USD` is not modelled (single-instrument, "
        "unlevered). Leverage, margin, liquidation, funding and venue "
        "contract-step rounding are not modelled either.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # float fastMA = ta.sma(close, fastMALen) / float slowMA = ta.sma(close, slowMALen)
        fast = ta.pine_sma(close, params["fastMALen"])
        slow = ta.pine_sma(close, params["slowMALen"])
        dataframe["pine_fast_ma"] = fast
        dataframe["pine_slow_ma"] = slow
        # ta.crossover / ta.crossunder: na on either side is false.
        dataframe["pine_open_long"] = ta.pine_crossover(fast, slow).to_numpy(bool)
        dataframe["pine_open_short"] = ta.pine_crossunder(fast, slow).to_numpy(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "open_long": dataframe["pine_open_long"].to_numpy(bool),
            "open_short": dataframe["pine_open_short"].to_numpy(bool),
            # The `* 0.01` is part of the script body in the source, so the
            # parameters carry the raw input defaults and are scaled here.
            "long_take_profit_perc": float(params["longTakeProfitPerc"]) * 0.01,
            "short_take_profit_perc": float(params["shortTakeProfitPerc"]) * 0.01,
            "trailing_perc": float(params["trailingTakeProfitPerc"]) * 0.01,
            "enable_trailing": bool(params["enableTrailing"]),
            # longTakeProfitPrice / shortTakeProfitPrice, carried bar to bar so
            # that `...[1]` can be read. na at bar 0, as `= na` leaves it.
            "state": {"long_tp": float("nan"), "short_tp": float("nan")},
        }

    def pine_script(self, broker, i, ctx):
        close = float(ctx["close"][i])
        state = ctx["state"]
        position = broker.position_size

        open_long = bool(ctx["open_long"][i])
        open_short = bool(ctx["open_short"][i])
        # longIsActive / shortIsActive, from the position as of THIS bar.
        long_active = open_long or position > 0
        short_active = open_short or position < 0

        long_perc = ctx["long_take_profit_perc"]
        short_perc = ctx["short_take_profit_perc"]

        prev_long_tp = state["long_tp"]
        prev_short_tp = state["short_tp"]

        # longTakeProfitPrice := if longIsActive / if openLongPosition and not
        # (strategy.position_size > 0) / else nz(longTakeProfitPrice[1], ...)
        if long_active:
            if open_long and not (position > 0):
                long_tp = close * (1.0 + long_perc)
            else:
                long_tp = ta.nz(prev_long_tp, close * (1.0 + long_perc))
        else:
            long_tp = float("nan")

        # shortTakeProfitPrice := if shortIsActive / ...
        # else nz(shortTakeProfitPrice[1], close * (1 - shortTakeProfitPrice))
        # The bare `shortTakeProfitPrice` is the same-bar self-reference of a
        # variable with no `var`, so it is the `na` initialiser: the fallback
        # argument is na and nz falls through to its first argument.
        if short_active:
            if open_short and not (position < 0):
                short_tp = close * (1.0 - short_perc)
            else:
                bare_self = float("nan")
                short_tp = ta.nz(prev_short_tp, close * (1.0 - bare_self))
        else:
            short_tp = float("nan")

        state["long_tp"] = long_tp
        state["short_tp"] = short_tp

        # longTrailingTakeProfitStepTicks = longTakeProfitPrice *
        #     trailingTakeProfitPerc / syminfo.mintick
        # ... and the short mirror.
        long_step_ticks = long_tp * ctx["trailing_perc"] / float(self.source_mintick)
        short_step_ticks = short_tp * ctx["trailing_perc"] / float(self.source_mintick)

        # strategy.entry(id='Long Entry', direction=strategy.long, when=openLongPosition)
        if open_long:
            broker.entry("Long Entry", "long")
        # strategy.entry(id='Short Entry', direction=strategy.short, when=openShortPosition)
        if open_short:
            broker.entry("Short Entry", "short")

        avg_price = broker.position_avg_price
        trailing = ctx["enable_trailing"]

        # strategy.exit(id='Long Take Profit', from_entry='Long Entry',
        #     limit = enableTrailing ? na : longTakeProfitPrice,
        #     trail_price = enableTrailing ? longTakeProfitPrice : na,
        #     trail_offset = enableTrailing ? longTrailingTakeProfitStepTicks : na,
        #     when = longIsActive)
        if long_active:
            if trailing:
                # trail_price is absolute; the engine wants the distance from
                # the average entry price (positive for a long).
                broker.exit(
                    "Long Take Profit", from_entry="Long Entry",
                    trail_points=long_tp - avg_price,
                    trail_offset=long_step_ticks * float(self.source_mintick),
                )
            else:
                broker.exit(
                    "Long Take Profit", from_entry="Long Entry", limit=long_tp,
                )

        # strategy.exit(id='Short Take Profit', from_entry='Short Entry',
        #     limit = enableTrailing ? na : shortTakeProfitPrice,
        #     trail_price = enableTrailing ? shortTakeProfitPrice : na,
        #     trail_offset = enableTrailing ? shortTrailingTakeProfitStepTicks : na,
        #     when = shortIsActive)
        if short_active:
            if trailing:
                broker.exit(
                    "Short Take Profit", from_entry="Short Entry",
                    trail_points=avg_price - short_tp,
                    trail_offset=short_step_ticks * float(self.source_mintick),
                )
            else:
                broker.exit(
                    "Short Take Profit", from_entry="Short Entry", limit=short_tp,
                )
