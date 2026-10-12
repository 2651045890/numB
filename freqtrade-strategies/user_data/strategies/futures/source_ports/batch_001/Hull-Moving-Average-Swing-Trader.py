"""Port of sources/SM_6b7dfef937f1f685.pine (batch_001/Hull-Moving-Average-Swing-Trader.md).

Pine v4 ("Hull Moving Average Swing Trader" by SEASIDE420). Both sides, on the
input source `open` (the md's argument table and the `input(open, ...)` default
both say open). The script builds two Hull-style series -- one from the current
bar's price, one from the previous bar's -- and derives two bands from them:

    n2ma = 2 * wma(price, round(hullperiod / 2))
    nma  =     wma(price, hullperiod)
    diff = n2ma - nma
    sqn  = round(sqrt(hullperiod))

    n2ma1 = 2 * wma(price[1], round(hullperiod / 2))
    nma1  =     wma(price[1], hullperiod)
    diff1 = n2ma1 - nma1

    n1 = wma(diff,  sqn)
    n2 = wma(diff1, sqn)

    Hull_Line = n1 / n1 * n2
    Hull_retracted = if n1 > n2
        Hull_Line - 2
    else
        Hull_Line + 2
    c1 = Hull_retracted + n1 - price
    c2 = Hull_retracted - n2 + price

    if price < c2
        strategy.close("BUY", when=window())
    if price > c2
        strategy.close("SELL", when=window())
    if price > c2 and price[1] > c1
        strategy.entry("BUY", strategy.long, when=window())
    if price < c1 and price[1] < c2
        strategy.entry("SELL", strategy.short, when=window())

All four calls are reproduced in exactly that order, the two `strategy.close`
calls BEFORE the two entries. `window()` is `=> true` and ignores the eight
input values it is built next to, so `when=` is always true here; `start` and
`finish` are computed (and therefore kept, with their own columns) but never
read -- the date inputs are inert in this source.

`Hull_Line = n1 / n1 * n2` is Pine's left-to-right `(n1 / n1) * n2`, which is
`n2` except where `n1` is 0 or na, where it is na. It is NOT simplified to `n2`
in this port.

FIDELITY NOTES. `strategy.close` is a MARKET close, so the engine fills it at
the next bar's open, one bar after the signal bar; the two `strategy.entry`
calls likewise fill at the next open. There is no `strategy.exit` and no stop,
limit or trail argument anywhere in the source -- only the entry id ("BUY" /
"SELL") distinguishes the two sides, so `strategy.close("BUY")` closes only the
long side's entry and is a no-op while a short is open (and vice versa).
"""
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _window() -> bool:
    """Pine `window() => true`.

    The source defines it inside the block that computes `start` / `finish`
    from the From/To date inputs, then hard-codes the result; the date inputs
    therefore never gate an order.
    """
    return True


def _pine_timestamp(year: int, month: int, day: int, hour: int, minute: int) -> int:
    """Pine `timestamp(year, month, day, hour, minute)`, in milliseconds.

    UTC rather than the exchange timezone: the value is never read by the
    source (see `_window`), so the timezone is unobservable here. datetime is
    used rather than pandas because `timestamp(9999, 1, 1, ...)` overflows
    pandas' nanosecond resolution.
    """
    moment = datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
    return int(moment.timestamp()) * 1000


class SMHullMovingAverageSwingTrader_6b7dfe(PinePortBase, IStrategy):
    source_id = "SM_6b7dfef937f1f685"
    source_file = "Hull-Moving-Average-Swing-Trader.md"
    # /*backtest ... period: 15m, basePeriod: 5m
    timeframe = "15m"
    can_short = True
    source_defaults = {
        "hullperiod": 210,
        # input(open, type=input.source, title="Price data")
        "price": "open",
        "FromMonth": 1,
        "FromDay": 1,
        "FromYear": 2020,
        "ToMonth": 1,
        "ToDay": 1,
        "ToYear": 9999,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    # strategy(...) declares no initial_capital, so Pine's documented default
    # (1000000 USD) is what the engine is told.
    source_initial_capital = 1_000_000.0
    # No strategy.exit and no stop/limit/trail argument in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Hull_Line = `n1 / n1 * n2` is kept as written (Pine divides left to "
        "right) rather than simplified to `n2`: the two differ wherever n1 is 0 "
        "or na, where Pine's 0/0 and na arithmetic give na. No source bar is "
        "expected to have n1 == 0, but the expression is transcribed, not "
        "optimised.",
        "round(hullperiod / 2) and round(sqrt(hullperiod)) are Pine math.round "
        "(half away from zero), written as pine_ta.pine_round. With the default "
        "hullperiod = 210 they are 105 and 14; Python's built-in round would "
        "disagree on a .5 case and is not used.",
        "`Hull_retracted = if n1 > n2 ... else ...` is Pine's if-as-expression. "
        "An na comparison is false on the original platform, so a warmup bar "
        "takes the ELSE branch, giving na there; np.where on a NaN comparison "
        "does the same here.",
        "`window() => true` is defined immediately after start/finish and "
        "ignores them, so every `when=window()` is true and the From/To date "
        "inputs never gate an order. `start` and `finish` ARE still computed "
        "every bar by the source (pine_timestamp_start / pine_timestamp_finish) "
        "and are carried as columns even though nothing reads them. Pine "
        "resolves timestamp() in the exchange timezone; this port uses UTC, "
        "which is unobservable because the value is never read.",
        "strategy.close('BUY') / strategy.close('SELL') are MARKET closes and "
        "are placed BEFORE the entries, in that order. The engine fills them at "
        "the next bar's open under the from_entry id, so a close for the side "
        "that is not open closes nothing (PINE_SEMANTICS.md 1.12 for the same "
        "guard on exits).",
        "strategy(...) declares default_qty_type = strategy.percent_of_equity "
        "and default_qty_value = 100 with pyramiding = 0, and NO "
        "initial_capital and NO commission, so Pine's documented defaults are "
        "used for those two (1000000 USD, 0%). The framework-side sizing basis "
        "for percent_of_equity is PINE_SEMANTICS.md 1.4/1.5.",
        "calc_on_order_fills=true and calc_on_every_tick=true are declared, so "
        "the original recalculates WITHIN a bar and can act on a bar whose "
        "orders have just filled. The engine evaluates once per bar at the "
        "close and fills at the next open, so intrabar paths are not modelled "
        "(PINE_SEMANTICS.md section 2 item 2, and the manifest flags this source "
        "as intrabar_recalculation). Not corrected.",
        "The md's prose says '2 X HMA's ... signal on crossover', but the code "
        "has no crossover call -- the only `cross` in the file is inside a "
        "COMMENTED-OUT plot on line 84. The live entry conditions are the "
        "two-bar comparisons `price > c2 and price[1] > c1` (long) and "
        "`price < c1 and price[1] < c2` (short). Code followed; the prose is "
        "the author's loose summary.",
        "The md's embedded PineScript block is byte-identical to "
        "sources/SM_6b7dfef937f1f685.pine apart from the trailing ASCII-art "
        "comment lines, which the md truncates. No code differs.",
        "plot(), fill() and c4 (`n1 > n2 ? color.green : color.red`) are "
        "display-only and are reproduced as no code. No variable other than "
        "start/finish is computed and left unread.",
        "The backtest window in the header (2022-04-25 to 2022-05-24) is not "
        "applied: the port runs on whatever range the caller supplies. Pine's "
        "own date window is the inert start/finish pair described above.",
        "Leverage, margin, liquidation and funding are not modelled, and the "
        "venue's contract-step rounding of order quantities is not modelled "
        "either.",
    ]

    def pine_indicators(self, dataframe, params):
        hullperiod = int(params["hullperiod"])
        price = ta.pine_source(dataframe, str(params["price"]))
        # round(hullperiod / 2) and round(sqrt(hullperiod)): Pine math.round
        half = int(ta.pine_round(hullperiod / 2.0))
        sqn = int(ta.pine_round(np.sqrt(hullperiod)))

        # start = timestamp(FromYear, FromMonth, FromDay, 00, 00)
        # finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
        # Computed every bar by the source and never read by anything, because
        # window() returns true regardless. Kept as columns for that reason.
        start = _pine_timestamp(
            int(params["FromYear"]), int(params["FromMonth"]),
            int(params["FromDay"]), 0, 0,
        )
        finish = _pine_timestamp(
            int(params["ToYear"]), int(params["ToMonth"]),
            int(params["ToDay"]), 23, 59,
        )
        dataframe["pine_timestamp_start"] = start
        dataframe["pine_timestamp_finish"] = finish

        # n2ma = 2 * wma(price, round(hullperiod / 2)); nma = wma(price, hullperiod)
        n2ma = 2.0 * ta.pine_wma(price, half)
        nma = ta.pine_wma(price, hullperiod)
        diff = n2ma - nma
        # n2ma1 = 2 * wma(price[1], ...); nma1 = wma(price[1], ...)
        previous = price.shift(1)
        n2ma1 = 2.0 * ta.pine_wma(previous, half)
        nma1 = ta.pine_wma(previous, hullperiod)
        diff1 = n2ma1 - nma1
        # n1 = wma(diff, sqn); n2 = wma(diff1, sqn)
        n1 = ta.pine_wma(diff, sqn)
        n2 = ta.pine_wma(diff1, sqn)

        # Hull_Line = n1 / n1 * n2  -- (n1 / n1) * n2, na where n1 is 0 or na.
        with np.errstate(divide="ignore", invalid="ignore"):
            hull_line = (n1 / n1) * n2
        # Hull_retracted = if n1 > n2 -> Hull_Line - 2 else Hull_Line + 2
        # (an na comparison is false, so warmup bars take the else branch)
        hull_retracted = pd.Series(
            np.where(n1 > n2, hull_line - 2.0, hull_line + 2.0), index=dataframe.index
        )
        # c1 = Hull_retracted + n1 - price;  c2 = Hull_retracted - n2 + price
        c1 = hull_retracted + n1 - price
        c2 = hull_retracted - n2 + price

        dataframe["pine_n1"] = n1
        dataframe["pine_n2"] = n2
        dataframe["pine_hull_line"] = hull_line
        dataframe["pine_hull_retracted"] = hull_retracted
        dataframe["pine_c1"] = c1
        dataframe["pine_c2"] = c2
        dataframe["pine_price"] = price
        dataframe["pine_price_prev"] = previous
        # if price < c2 ... / if price > c2 ... / the two entries' conditions.
        # na comparisons are false on both sides, so fillna(False) is explicit.
        dataframe["pine_close_buy"] = (price < c2).fillna(False)
        dataframe["pine_close_sell"] = (price > c2).fillna(False)
        dataframe["pine_entry_buy"] = ((price > c2) & (previous > c1)).fillna(False)
        dataframe["pine_entry_sell"] = ((price < c1) & (previous < c2)).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "close_buy": dataframe["pine_close_buy"].to_numpy(dtype=bool),
            "close_sell": dataframe["pine_close_sell"].to_numpy(dtype=bool),
            "entry_buy": dataframe["pine_entry_buy"].to_numpy(dtype=bool),
            "entry_sell": dataframe["pine_entry_sell"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if price < c2
        #     strategy.close("BUY", when=window())
        broker.close("BUY", when=bool(ctx["close_buy"][i]) and _window())
        # if price > c2
        #     strategy.close("SELL", when=window())
        broker.close("SELL", when=bool(ctx["close_sell"][i]) and _window())
        # if price > c2 and price[1] > c1
        #     strategy.entry("BUY", strategy.long, when=window())
        if bool(ctx["entry_buy"][i]) and _window():
            broker.entry("BUY", "long")
        # if price < c1 and price[1] < c2
        #     strategy.entry("SELL", strategy.short, when=window())
        if bool(ctx["entry_sell"][i]) and _window():
            broker.entry("SELL", "short")
