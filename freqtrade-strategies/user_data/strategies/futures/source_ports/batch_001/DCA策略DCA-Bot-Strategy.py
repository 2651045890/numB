"""Port of sources/SM_d6003112f5a8d715.pine (batch_001/DCA策略DCA-Bot-Strategy.md).

Pine v4. A 3commas-style DCA backtester (author: rouxam):

    var bo_level = 0.0 ; var latest_so_level = 0.0 ; var next_so_level = 0.0
    var ttp_active = false ; var ttp_max = 0.0 ; var ttp_level = 0.0
    var take_profit_level = 0.0

    if strategy.position_size <= 0.0
        ttp_max := 0.0
        ttp_active := false

    if (strategy.opentrades == 0 and window and close > 0)
        bo_level := open
        strategy.entry("BO", limit=bo_level, long=strategy.long, qty=base_order/bo_level)
        latest_so_level := open

    place_safety_orders = latest_so_level == bo_level
    if place_safety_orders
        for i = 1 to max_safe_order
            next_so_level := latest_so_level * (1 - price_deviation * pow(safe_order_step_scale, i-1))
            strategy.entry("SO"+tostring(i), long=strategy.long, limit=next_so_level,
                           qty=safe_order * pow(safe_order_volume_scale, i-1)/next_so_level)
            latest_so_level := next_so_level

    if strategy.position_size > 0
        take_profit_level := strategy.position_avg_price * (1 + take_profit)
        if ttp <= 0.0
            strategy.exit(id="TP", limit=take_profit_level)
        else
            if take_profit_level <= close
                ttp_max := max(high, ttp_max)
                ttp_active := true
            if ttp_active
                ttp_level := ttp_max * (1 - ttp)
                strategy.exit(id="TTP", stop=ttp_level)

Every statement is reproduced in the source's own order, including the five
`var` initialisations that share the bar with the blocks that read them.

THREE PROPERTIES OF THIS SOURCE MATTER MORE THAN THE TRANSLATION:

1. EVERY entry carries `limit=`. The base order rests at the OPEN of the bar
   that created it, so it fills on a later bar and at the limit (or better),
   not at the next bar's open. PINE_SEMANTICS.md section 二 11 records that a
   resting entry cannot be projected onto the framework: the projection can
   only emit enter_long on the bar the order was CREATED. The engine's ledger
   fills at the right bar and price; the signal columns do not.
2. The safety orders are placed from `latest_so_level`, which starts at 0.0 and
   equals `bo_level` (also 0.0). So on a bar where the base-order block does
   not fire, `latest_so_level == bo_level` is TRUE and the loop still runs --
   placing SO1..SO5 at a limit of 0.0 with a quantity of `x / 0`. Pine has no
   infinities, so that quotient is na, and an na `qty` means "use the
   strategy's default order size" (the `qty` argument's own documented
   default). The port passes NaN for exactly that case and the engine applies
   its default size, as Pine does. See source_fidelity_notes -- this is not
   hypothetical: the validation frame starts in 2019, before the source's
   default window opens in 2021, so every validation bar is outside the window
   and takes this path.
3. `strategy()` IS COMMENTED OUT (source line 16), so Pine's documented
   defaults are in force: `strategy.fixed` / 1 contract, initial capital
   1000000, commission 0%, `pyramiding = 0`, `process_orders_on_close = false`.
   The commented line asks for pyramiding = 99, process_orders_on_close = true
   and a 0.1% commission. The pyramiding fork is the load-bearing one: with
   `pyramiding = 0` the engine refuses a same-direction entry once the base
   order is open, so the five safety orders are dropped on the bar the base
   order fills and the DCA legs never scale in. That is what the commented
   declaration would have changed, and it is recorded rather than applied --
   and it could not be reproduced through the framework either way, because
   Freqtrade position adjustment is not wired into PinePortBase
   (PINE_SEMANTICS.md section 二 10).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


def _minute_key(index) -> np.ndarray:
    """Pine's `time` comparison, as an order-preserving integer key.

    The source gates its base order on `time >= start and time <= finish` with
    `start = timestamp(from_year, from_month, from_day, 00, 00)` and
    `finish = timestamp(to_year, to_month, to_day, 23, 59)`, both built from
    inputs. `to_year` DEFAULTS TO 9999, which `pd.Timestamp` cannot represent
    (its ceiling is 2262-04-11), so the comparison is made on a
    year/month/day/hour/minute integer key instead of on timestamps -- exact,
    and free of any date-range ceiling.

    Pine evaluates `time` in the EXCHANGE's time zone; this layer's frames are
    UTC and no exchange time zone is declared anywhere in the source, so UTC
    components are used (PINE_SEMANTICS.md 3.4).
    """
    idx = pd.DatetimeIndex(index)
    if idx.tz is not None:
        idx = idx.tz_convert("UTC")
    return (
        idx.year.to_numpy(dtype=np.int64) * 100_000_000
        + idx.month.to_numpy(dtype=np.int64) * 1_000_000
        + idx.day.to_numpy(dtype=np.int64) * 10_000
        + idx.hour.to_numpy(dtype=np.int64) * 100
        + idx.minute.to_numpy(dtype=np.int64)
    )


def _key(year, month, day, hour, minute) -> int:
    return (
        int(year) * 100_000_000 + int(month) * 1_000_000 + int(day) * 10_000
        + int(hour) * 100 + int(minute)
    )


def _pine_divide(numerator: float, denominator: float) -> float:
    """Pine division: a zero denominator is na, never an exception.

    Pine has no infinities -- `x / 0` is na -- and Python raises
    ZeroDivisionError. The difference is reachable in this source (see the
    module docstring, point 2), so the Pine result is produced explicitly.
    """
    if denominator == 0:
        return float("nan")
    return numerator / denominator


class SMDcaBotStrategy_d60031(PinePortBase, IStrategy):
    source_id = "SM_d6003112f5a8d715"
    source_file = "DCA策略DCA-Bot-Strategy.md"
    timeframe = "15h"
    # The source only ever opens LONG positions (every entry is
    # `long=strategy.long`); there is no short call anywhere.
    can_short = False
    source_defaults: dict = {
        # input(1.0, type=input.float, title='Price deviation to open safety orders (%)')/100
        "price_deviation": 1.0,
        # input(1.0, ... title='Target Take Profit (%)')/100
        "take_profit": 1.0,
        # input(0.5, ... title='Trailing Take Profit (%) [0 = Disabled]')/100
        "ttp": 0.5,
        # input(10.0, type=input.float, title='base order')
        "base_order": 10.0,
        # input(20.0, type=input.float, title='safe order')
        "safe_order": 20.0,
        # input(2.0, type=input.float, title='Safety order volume scale', step=0.1)
        "safe_order_volume_scale": 2.0,
        # input(1.5, type=input.float, title='Safety order step scale', step=0.1)
        "safe_order_step_scale": 1.5,
        # input(5, title='Max safe order', minval=1, maxval=99, step=1)
        "max_safe_order": 5,
        # Date window inputs, in the source's own units (the three "%" inputs
        # above are divided by 100 where they are READ, not at declaration).
        "from_month": 1,
        "from_day": 1,
        "from_year": 2021,
        "to_month": 1,
        "to_day": 1,
        "to_year": 9999,
    }
    # The ONLY strategy() declaration in the file (line 16) is commented out, so
    # it declares nothing: Pine's documented defaults apply. The commented line
    # asks for pyramiding=99, process_orders_on_close=true and
    # commission_type=percent with commission_value=0.1; none of that is in
    # force (see source_fidelity_notes for what the pyramiding fork does here).
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The trailing take profit is a live `strategy.exit(stop=...)` leg.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "NOT a converter-appended order block, despite its tier_reason. The "
        "file declares no indicator() and no study(), its only strategy() line "
        "(line 16) is COMMENTED OUT, and every order call is the author's own "
        "active code, including a live strategy.exit(limit=) take profit and a "
        "live strategy.exit(stop=) trailing take profit. The tier_reason's "
        "'declares indicator()/study(), tool appended strategy.entry pair; NO "
        "exits' is false on all three counts. The source is followed.",
        "The file's only strategy() declaration is COMMENTED OUT (line 16), so "
        "Pine's documented defaults are in force: default_qty_type fixed / 1 "
        "contract, initial_capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. RECORDED BUT NOT APPLIED: the commented "
        "line asks for pyramiding = 99, process_orders_on_close = true, and "
        "commission_type = strategy.commission.percent with commission_value = "
        "0.1.",
        "THE PYRAMIDING FORK IS LOAD-BEARING HERE. This source's whole point is "
        "the DCA ladder: the base order plus up to 5 safety orders, each with "
        "its own limit and its own quantity. Under the declared pyramiding = 0, "
        "the engine refuses a same-direction entry once the base order is open "
        "(_can_add), so SO1..SO5 are dropped on the bar the base order fills and "
        "the ladder never scales in -- the port then behaves as 'buy once, trail "
        "out'. Under the commented pyramiding = 99 it would scale in. The "
        "commented value is not applied (a commented-out line declares nothing), "
        "and the fork is recorded instead of resolved. Note that neither "
        "reading could be verified through the framework: PinePortBase sets "
        "position_adjustment_enable = False, so Freqtrade can only hold one "
        "position regardless (PINE_SEMANTICS.md section 二 10, pyramiding "
        "unimplemented).",
        "process_orders_on_close: the commented declaration asks for true, Pine's "
        "default is false, and the engine models false only (PineBrokerConfig "
        "has no such field) -- a market order placed at bar t fills at bar t+1's "
        "open. Under `true` the fill would be at bar t's own CLOSE, which this "
        "layer cannot express. Every entry here is a limit order rather than a "
        "market order, so the flag's effect is limited to how `open`-anchored "
        "limits interact with the bar they were placed on.",
        "EVERY ENTRY IS A RESTING LIMIT ORDER, not a market order: 'BO' rests at "
        "the bar's own open and SO1..SO5 rest below it. PINE_SEMANTICS.md "
        "section 二 11 records that such an entry cannot be projected onto a "
        "framework whose only entry is a next-open market order -- the "
        "projection can only emit enter_long on the bar the order was CREATED. "
        "The engine's ledger fills each order on the bar price actually reaches "
        "its limit; the signal columns are one-sided by construction.",
        "THE SAFETY-ORDER BLOCK RUNS EVEN WHEN THE BASE-ORDER BLOCK DOES NOT. "
        "`latest_so_level` and `bo_level` both start at 0.0, so "
        "`place_safety_orders = latest_so_level == bo_level` is TRUE from the "
        "first bar until one of the two blocks makes them differ. On a bar "
        "where `strategy.opentrades == 0 and window and close > 0` is false, "
        "the loop therefore runs with `latest_so_level = 0.0`: every SO level "
        "is 0.0 and every quantity is `safe_order * scale / 0`. Pine has no "
        "infinities, so that quotient is na, and an na qty means 'use the "
        "strategy's default order size' (the qty argument's documented default, "
        "and the branch the engine's own `_size_for` fallback implements). The "
        "port reproduces that: a zero denominator yields NaN qty, not a "
        "ZeroDivisionError, and the engine sizes the order from "
        "default_qty_value as Pine would. The limit of 0.0 can never be "
        "reached, so those orders rest un-filled.",
        "CONSEQUENCE OF THE ABOVE FOR validate_pine: its synthetic frame starts "
        "at 2019-01-01 while this source's default window opens at 2021-01-01, "
        "so EVERY validation bar is outside the window, the base order is never "
        "placed, and the run takes the zero-level safety-order path on every "
        "bar. That is the source's own behaviour on that data, not a port "
        "defect. Measured: 3000 projected enter_long signals (one per synthetic "
        "bar -- the creation bar of each limit-0.0 order) and 0 engine fills, "
        "because a limit of 0.0 is never reached; load / run / causal all pass. "
        "In the real 2024 chain-verification window the base order fires on the "
        "first bar, so the path never arises there.",
        "PUBLIC-LAYER DEVIATION (reported, not worked around): the engine does "
        "not replace a same-id stop/limit ENTRY order -- `_place` only replaces "
        "same-id `exit` orders -- so re-issuing 'BO'/'SO1'.. before the previous "
        "copies have filled leaves several copies resting at once, where Pine "
        "keeps one order per id. PINE_SEMANTICS.md 1.12 records exactly this as "
        "an open, unverified question, and this source is one that reaches it "
        "(the base-order block re-fires on every bar until an entry fills). "
        "Recorded rather than fixed, per the same section's own instruction; "
        "fixing it would change the resting-order set and needs an original-"
        "platform comparison to settle. MEASURED on a 2000-bar in-window smoke "
        "frame (2024, 15h): 177 entry cycles placed 285 'BO' orders -- 108 of "
        "them while an earlier copy was still resting -- plus 285 of each "
        "'SO1'..'SO5'. The extra copies cannot stack the position (the "
        "pyramiding gate drops every later same-direction entry once one is "
        "open), but they can change WHICH resting level the base order fills at.",
        "MEASURED, SAME SMOKE FRAME: 0 of the 1425 safety orders ever filled. "
        "The base order fills on the bar after it is placed, and the five "
        "resting safety orders are dropped at that same bar by the pyramiding "
        "gate, not re-queued. So the safety-order leg is inert IN THIS "
        "CONFIGURATION and the port is, in practice, 'rest a buy at the open, "
        "trail out with the take profit, repeat'. That frame produced 177 entry "
        "cycles / 176 round trips with 353 entry-or-exit fills -- one base-order "
        "fill plus one take-profit fill per cycle, the last cycle still open. On "
        "a seed whose price never closed 1% above the entry, the single position "
        "was simply held to the end of the frame: the source has NO stop loss, "
        "only the take profit, which is why its own description warns that "
        "'strict stop loss is crucial'.",
        "The take-profit legs are reproduced on both sides. `strategy.exit(id="
        "'TP', limit=take_profit_level)` is a resting LIMIT (the framework's ROI "
        "hooks mirror it) and `strategy.exit(id='TTP', stop=ttp_level)` is a "
        "resting STOP (mirrored through custom_stoploss). Both are re-issued on "
        "every bar while `strategy.position_size > 0`, and the engine's same-id "
        "replacement applies to them, which is the modelling choice recorded in "
        "PINE_SEMANTICS.md 3.6. The trailing 'ratchet' here is not Pine's "
        "trail_points machinery -- the author implements it in the script by "
        "keeping ttp_max and re-issuing an absolute stop -- so the same-id "
        "replacement cannot reset it, and it is reproduced exactly.",
        "The trailing take profit only comes alive after "
        "`take_profit_level <= close`, i.e. after a close above "
        "avg_price * (1 + take_profit). Until then NO exit order of any kind "
        "rests (the `if ttp_active` guard decides that), so a position entered "
        "before its first qualifying close has no stop at all. Reproduced as "
        "written.",
        "`window` gates ONLY the base-order block; the safety-order block and "
        "the take-profit block have no window condition. Reproduced as written "
        "(it is what makes the zero-level path above reachable).",
        "MD/SOURCE MISMATCH (rendered defaults): the md's argument table renders "
        "the three percentage inputs as `true` (they are the floats 1.0 / 1.0 / "
        "0.5) and the four date inputs as `true` (they are integers). The "
        "source's literal defaults are what is carried here; the /100 is "
        "applied where each input is READ, exactly as the source writes it.",
        "The date window is DECLARED IN THE SOURCE BUT CANNOT BE APPLIED BY THE "
        "REPO'S BACKTEST WINDOW: `to_year` defaults to 9999 and `from_year` to "
        "2021, so on the repo's 2024 chain-verification data the gate is "
        "inert (every bar is inside it). It is implemented as an integer "
        "year/month/day/hour/minute key rather than with pd.Timestamp, which "
        "cannot represent the 9999 default (ceiling 2262-04-11).",
        "Pine's `time` is exchange-time-zone; this layer's frames are UTC and no "
        "exchange time zone is declared, so UTC components are used "
        "(PINE_SEMANTICS.md 3.4).",
        "The /*backtest header names Futures_Binance / BTC_USDT while the repo's "
        "chain verification uses BTC/USDT:USDT -- a venue mapping, not a source "
        "property. Leverage, margin, liquidation, funding and the venue's "
        "contract-step rounding are not modelled (PINE_SEMANTICS.md 1.6 "
        "measures the step rounding separately). The header's `basePeriod: 15m` "
        "is the FMZ backtester's own fill granularity, not the strategy period.",
        "`plot` calls and the title are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        index = dataframe.index
        full = _minute_key(index)
        start = _key(params["from_year"], params["from_month"], params["from_day"], 0, 0)
        finish = _key(params["to_year"], params["to_month"], params["to_day"], 23, 59)
        # window = time >= start and time <= finish ? true : false
        dataframe["pine_window"] = ((full >= start) & (full <= finish))
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "open": dataframe["open"].to_numpy(dtype=float),
            "high": dataframe["high"].to_numpy(dtype=float),
            "low": dataframe["low"].to_numpy(dtype=float),
            "close": dataframe["close"].to_numpy(dtype=float),
            "window": dataframe["pine_window"].to_numpy(dtype=bool),
            # The three percentage inputs are divided by 100 where they are
            # READ (`input(...)/100`), not at declaration.
            "price_deviation": float(params["price_deviation"]) / 100.0,
            "take_profit": float(params["take_profit"]) / 100.0,
            "ttp": float(params["ttp"]) / 100.0,
            "base_order": float(params["base_order"]),
            "safe_order": float(params["safe_order"]),
            "safe_order_volume_scale": float(params["safe_order_volume_scale"]),
            "safe_order_step_scale": float(params["safe_order_step_scale"]),
            "max_safe_order": int(params["max_safe_order"]),
            # `var` slots, initialised once per run (fresh dict per call, so a
            # truncated re-run starts from the same zeros the source does).
            "state": {
                "bo_level": 0.0,
                "latest_so_level": 0.0,
                "next_so_level": 0.0,
                "ttp_active": False,
                "ttp_max": 0.0,
                "ttp_level": 0.0,
                "take_profit_level": 0.0,
            },
        }

    def pine_script(self, broker, i, ctx):
        st = ctx["state"]
        position_size = broker.position_size

        # if strategy.position_size <= 0.0
        if position_size <= 0.0:
            st["ttp_max"] = 0.0
            st["ttp_active"] = False

        # if(strategy.opentrades == 0 and window and close > 0)
        if broker.open_trades == 0 and ctx["window"][i] and ctx["close"][i] > 0:
            # bo_level := open
            st["bo_level"] = float(ctx["open"][i])
            # strategy.entry("BO", limit=bo_level, long=strategy.long,
            #                qty=base_order/bo_level)
            broker.entry(
                "BO", "long",
                qty=_pine_divide(ctx["base_order"], st["bo_level"]),
                limit=st["bo_level"],
            )
            # latest_so_level := open
            st["latest_so_level"] = float(ctx["open"][i])

        # place_safety_orders = latest_so_level == bo_level
        if st["latest_so_level"] == st["bo_level"]:
            level = st["latest_so_level"]
            for n in range(1, int(ctx["max_safe_order"]) + 1):
                # next_so_level := latest_so_level * (1 - price_deviation *
                #                  pow(safe_order_step_scale, i - 1))
                next_level = level * (
                    1.0 - ctx["price_deviation"]
                    * ctx["safe_order_step_scale"] ** (n - 1)
                )
                st["next_so_level"] = next_level
                # strategy.entry("SO"+tostring(i), long=strategy.long,
                #                limit=next_so_level,
                #                qty=safe_order * pow(safe_order_volume_scale, i-1)/next_so_level)
                broker.entry(
                    "SO" + str(n), "long",
                    qty=_pine_divide(
                        ctx["safe_order"] * ctx["safe_order_volume_scale"] ** (n - 1),
                        next_level,
                    ),
                    limit=next_level,
                )
                # latest_so_level := next_so_level
                level = next_level
            st["latest_so_level"] = level

        # if strategy.position_size > 0
        if position_size > 0:
            # take_profit_level := strategy.position_avg_price * (1 + take_profit)
            st["take_profit_level"] = broker.position_avg_price * (
                1.0 + ctx["take_profit"]
            )
            if ctx["ttp"] <= 0.0:
                # No trailing take profit -- strategy.exit(id="TP", limit=take_profit_level)
                broker.exit("TP", limit=st["take_profit_level"])
            else:
                # if take_profit_level <= close
                if st["take_profit_level"] <= ctx["close"][i]:
                    # ttp_max := max(high, ttp_max) ; ttp_active := true
                    st["ttp_max"] = max(float(ctx["high"][i]), st["ttp_max"])
                    st["ttp_active"] = True
                # if ttp_active
                if st["ttp_active"]:
                    # ttp_level := ttp_max * (1 - ttp)
                    st["ttp_level"] = st["ttp_max"] * (1.0 - ctx["ttp"])
                    # strategy.exit(id="TTP", stop=ttp_level)
                    broker.exit("TTP", stop=st["ttp_level"])
