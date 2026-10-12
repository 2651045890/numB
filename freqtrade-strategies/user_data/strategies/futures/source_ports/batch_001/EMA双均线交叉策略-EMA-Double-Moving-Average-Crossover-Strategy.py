"""Port of sources/SM_f6440204b0b6fcd2.pine (batch_001/EMA双均线交叉策略-EMA-Double-Moving-Average-Crossover-Strategy.md).

Peter Gangmei's EMA crossover strategy: a 20/50 EMA cross, long on the cross
above and short on the cross below.

    ema20 = ta.ema(close, short_ma_length)        // 20
    ema50 = ta.ema(close, long_ma_length)         // 50
    ema200 = ta.ema(close, long_ma_200_length)    // 200
    crossed_above = ta.crossover(ema20, ema50)
    crossed_below = ta.crossunder(ema20, ema50)
    if crossed_above -> strategy.entry("Buy",  strategy.long)
    if crossed_below -> strategy.entry("Sell", strategy.short)

`strategy()` declares only title / overlay, so every order property is Pine's
default: fixed quantity of 1 contract, 0% commission, pyramiding 0, initial
capital 1000000. There is no exit call, so a position goes flat only when the
opposite entry reverses it: `source_reproduce_stops` is False and a position
open at the end of the window stays open.

FIDELITY:

* Three source statements have NO effect on the orders and are not reproduced
  as trading logic, because nothing reads them:
  `start_time = timestamp(2024, 01, 01, 00, 00)` and `current_time = timenow`
  are assigned and never referenced, so no date window is applied; the
  enclosing `if true` is a constant-true wrapper. The port trades every bar of
  the supplied data, exactly as the source does.
* `ema200` is computed and plotted but never enters a condition, so it changes
  no order; it is still computed here because the source computes it, and is
  kept out of `pine_context` since nothing reads it.
* `alert("Buy Condition", alert.freq_once_per_bar_close)` and the matching sell
  alert are notifications, not orders (PINE_SEMANTICS.md 2.7), and the two
  `plotshape` markers are display-only.
* `plot()`/`overlay` are display-only.
* `ta.ema` is seeded with the first non-na observation in `pine_ta`
  (PINE_SEMANTICS.md 3.1); TradingView does not publish its seeding rule, so the
  early bars of both EMAs carry that documented parity risk. Both EMAs share it,
  so the cross dates are only at risk while a cross falls inside the warmup.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding -- the chain verifier measures that
  separately rather than treating it as a signal difference.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEmaDoubleMovingAverageCrossover_f64402(PinePortBase, IStrategy):
    source_id = "SM_f6440204b0b6fcd2"
    source_file = "EMA双均线交叉策略-EMA-Double-Moving-Average-Crossover-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "short_ma_length": 20,
        "long_ma_length": 50,
        "long_ma_200_length": 200,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "start_time = timestamp(2024,01,01,00,00) and current_time = timenow are "
        "assigned and never referenced in the source, and the if true wrapper "
        "is constant-true, so no date window is applied: the port trades every "
        "bar of the supplied data just as the source does. The names suggest a "
        "time filter was intended but never wired up; per rule 2 the source's "
        "actual behaviour is reproduced.",
        "ema200 is computed and plotted but never read by a condition, so it "
        "changes no order. It is computed for completeness and excluded from "
        "pine_context because nothing consumes it.",
        "alert() calls are notifications, not orders (PINE_SEMANTICS.md 2.7), "
        "and the plotshape markers plus the three plot() calls are display-only.",
        "strategy() declares only title/overlay, so qty_type=fixed, qty_value=1, "
        "commission=0%, pyramiding=0 and initial_capital=1000000 are Pine's "
        "documented defaults.",
        "ta.ema seeding is the modelled first-non-na choice (PINE_SEMANTICS.md "
        "3.1); TradingView does not publish its rule, so the warmup bars of both "
        "EMAs carry that parity risk. Both averages share it, so only a cross "
        "falling inside the warmup would be affected.",
        "There is no exit call: a position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False and a position "
        "open at the end of the window stays open.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema_short = ta.pine_ema(close, int(params["short_ma_length"]))
        ema_long = ta.pine_ema(close, int(params["long_ma_length"]))
        # Computed because the source computes it; never read by a condition.
        ema_200 = ta.pine_ema(close, int(params["long_ma_200_length"]))
        dataframe["pine_ema_short"] = ema_short
        dataframe["pine_ema_long"] = ema_long
        dataframe["pine_ema_200"] = ema_200
        dataframe["pine_crossed_above"] = ta.pine_crossover(ema_short, ema_long)
        dataframe["pine_crossed_below"] = ta.pine_crossunder(ema_short, ema_long)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "crossed_above": dataframe["pine_crossed_above"].to_numpy(),
            "crossed_below": dataframe["pine_crossed_below"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if true
        #     if (crossed_above)
        #         strategy.entry("Buy", strategy.long)
        if ctx["crossed_above"][i]:
            broker.entry("Buy", "long")
        #     if (crossed_below)
        #         strategy.entry("Sell", strategy.short)
        if ctx["crossed_below"][i]:
            broker.entry("Sell", "short")
