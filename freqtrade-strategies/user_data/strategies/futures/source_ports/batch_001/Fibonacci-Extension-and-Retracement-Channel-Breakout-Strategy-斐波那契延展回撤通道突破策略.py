"""Port of sources/SM_a902184bc655fa0e.pine
(batch_001/Fibonacci-Extension-and-Retracement-Channel-Breakout-Strategy-斐波那契延展回撤通道突破策略.md).

Pine v5. A highest-high / lowest-low channel, a persistent one-bar-lagged
breakout state machine on top of it, and a direction flip derived from that
state:

    length  = input(20)
    reverse = input(false, title='Trade reverse')
    hh      = ta.highest(high, length)
    ll      = ta.lowest(low, length)

    pos = 0.0
    iff_1 = close < ll[1] ? -1 : nz(pos[1], 0)
    pos := close > hh[1] ? 1 : iff_1
    iff_2 = reverse and pos == -1 ? 1 : pos
    possig = reverse and pos == 1 ? -1 : iff_2

    if possig == 1
        strategy.entry('Long', strategy.long)
    if possig == -1
        strategy.entry('Short', strategy.short)

`pos` is Pine series state, not a recomputed expression: it carries forward
whatever the previous bar held unless THIS bar's break says otherwise. The
port therefore replays the assignment per bar instead of vectorising it -- a
`where`-style rewrite would silently read the wrong bar's `pos`.

Both entries are placed on EVERY bar the state holds its sign, not only on the
transition. Pine's `pyramiding` default is 0 and the source does not override
it, so a repeated same-direction entry is a no-op; the engine models that
(`PineBroker._can_add`), and the port keeps the calls unconditional so the
order sequence still matches the source.

`reverse` is an input that defaults to false, at which point `possig == pos`.
Its two ternaries are still implemented, because an input default is a value,
not an absence.

All the Fibonacci targets (`fib_long_target1..5`, `fib_short_target1..5`) and
`barcolor` / `plot` / `label.new` are display-only: no executed statement reads
them. They are computed below anyway so the port carries the source's formulas.

The source declares no `strategy()` properties beyond title/overlay, so Pine's
documented defaults apply: initial_capital 1000000 USD, default_qty_type
`strategy.fixed`, default_qty_value 1, commission 0%, pyramiding 0. There is no
exit call: a position is closed only by the opposite entry reversing it, so
`source_reproduce_stops` is False and a position open at the end stays open.
`can_short` is True.
"""
from __future__ import annotations

import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFibonacciChannelBreakout_a90218(PinePortBase, IStrategy):
    source_id = "SM_a902184bc655fa0e"
    source_file = (
        "Fibonacci-Extension-and-Retracement-Channel-Breakout-Strategy-"
        "斐波那契延展回撤通道突破策略.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {"length": 20, "reverse": False}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close / stop= / limit= anywhere.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`pos` is Pine series state: `pos := close > hh[1] ? 1 : iff_1` where "
        "iff_1 falls back to nz(pos[1], 0). The port replays the assignment bar by "
        "bar; a vectorised rewrite would read the wrong bar's pos.",
        "hh / ll are ta.highest(high, length) / ta.lowest(low, length), i.e. a "
        "rolling max/min over `length` bars including the current one, na until the "
        "window is full (PINE_SEMANTICS.md 3.2). The comparisons use hh[1] / ll[1], "
        "so the breakout level is the previous bar's channel and the na prefix "
        "extends one bar further.",
        "An na channel compares false under Pine's na-compares-false rule, so the "
        "state machine reads iff_1 (and `nz(pos[1], 0)` reads 0 on the first bar) "
        "rather than taking either breakout branch.",
        "`reverse` defaults to false, so possig == pos by default; both ternaries are "
        "still implemented because an input default is a value, not an absence. Its "
        "`and` binds looser than `==`, so each reads `reverse and (pos == -1)`.",
        "Both strategy.entry calls sit on every bar the state holds, not on the "
        "transition only; pyramiding is Pine's default 0, so a repeated "
        "same-direction entry is a no-op. The calls are kept unconditional so the "
        "order sequence matches the source's.",
        "The Fibonacci target levels (fib_long_target1..5 / fib_short_target1..5) are "
        "read only by plot() and label.new(), i.e. display-only; they are computed "
        "here to carry the formulas but no trade behaviour depends on them.",
        "barcolor / plot / label.new / the plot.style_stepline arguments are "
        "display-only and are not reproduced.",
        "No exit call exists: a position is closed only by the opposite entry "
        "reversing it, so source_reproduce_stops is False and a position open at the "
        "end of the data stays open.",
        "The source declares no strategy() properties beyond title/overlay, so Pine's "
        "documented defaults are used: fixed / 1 contract, initial capital 1000000, "
        "commission 0%, pyramiding 0.",
        "Leverage, margin, liquidation and funding are not modelled; the venue's "
        "contract-step rounding is not modelled either and is measured separately by "
        "verify_chain.",
    ]

    # ---- ta.* / bare builtins ---------------------------------------------
    def pine_indicators(self, dataframe, params):
        high = dataframe["high"].astype(float)
        low = dataframe["low"].astype(float)
        close = dataframe["close"].astype(float)
        length = int(params["length"])
        reverse = bool(params["reverse"])

        # hh = ta.highest(high, length) ; ll = ta.lowest(low, length)
        hh = ta.pine_highest(high, length)
        ll = ta.pine_lowest(low, length)
        dataframe["pine_hh"] = hh
        dataframe["pine_ll"] = ll

        # Fibonacci level constants -- literals in the source, not inputs.
        fib_retracement1, fib_retracement2 = 0.236, 0.382
        fib_extension1, fib_extension2, fib_extension3 = 1.272, 1.414, 1.618
        # fib_long_entry = hh ; fib_short_entry = ll
        dataframe["pine_fib_long_entry"] = hh
        dataframe["pine_fib_short_entry"] = ll
        dataframe["pine_fib_long_target1"] = hh + (hh - ll) * fib_extension1
        dataframe["pine_fib_long_target2"] = hh + (hh - ll) * fib_extension2
        dataframe["pine_fib_long_target3"] = hh + (hh - ll) * fib_extension3
        dataframe["pine_fib_long_target4"] = hh - (hh - ll) * fib_retracement1
        dataframe["pine_fib_long_target5"] = hh - (hh - ll) * fib_retracement2
        dataframe["pine_fib_short_target1"] = ll - (hh - ll) * fib_extension1
        dataframe["pine_fib_short_target2"] = ll - (hh - ll) * fib_extension2
        dataframe["pine_fib_short_target3"] = ll - (hh - ll) * fib_extension3
        dataframe["pine_fib_short_target4"] = ll + (hh - ll) * fib_retracement1
        dataframe["pine_fib_short_target5"] = ll + (hh - ll) * fib_retracement2

        # The state machine, replayed bar by bar.
        #   pos = 0.0
        #   iff_1  = close < ll[1] ? -1 : nz(pos[1], 0)
        #   pos   := close > hh[1] ? 1 : iff_1
        #   iff_2  = reverse and pos == -1 ? 1 : pos
        #   possig = reverse and pos == 1 ? -1 : iff_2
        close_values = close.to_numpy(dtype=float)
        hh_prev = hh.shift(1).to_numpy(dtype=float)
        ll_prev = ll.shift(1).to_numpy(dtype=float)
        pos = np.zeros(len(dataframe), dtype=float)
        possig = np.zeros(len(dataframe), dtype=float)
        previous = np.nan  # pos[1]; na on the first bar, hence nz(..., 0)
        for i in range(len(dataframe)):
            if close_values[i] < ll_prev[i]:
                iff_1 = -1.0
            elif np.isnan(previous):
                iff_1 = 0.0  # nz(pos[1], 0)
            else:
                iff_1 = previous
            current = 1.0 if close_values[i] > hh_prev[i] else iff_1
            pos[i] = current
            previous = current
            iff_2 = 1.0 if (reverse and current == -1) else current
            possig[i] = -1.0 if (reverse and current == 1) else iff_2

        dataframe["pine_pos"] = pos
        dataframe["pine_possig"] = possig
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "pos": dataframe["pine_pos"].to_numpy(dtype=float),
            "possig": dataframe["pine_possig"].to_numpy(dtype=float),
        }

    # ---- strategy.* -------------------------------------------------------
    def pine_script(self, broker, i, ctx):
        possig = ctx["possig"][i]
        # if possig == 1
        #     strategy.entry('Long', strategy.long)
        if possig == 1:
            broker.entry("Long", "long")
        # if possig == -1
        #     strategy.entry('Short', strategy.short)
        if possig == -1:
            broker.entry("Short", "short")
