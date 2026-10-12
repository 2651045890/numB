"""Port of sources/SM_46ece42e0ed49b67.pine (batch_001/KijunSen-Line-With-Cross.md).

Pine v5 source that is NOT an author-written strategy: it declares
`indicator('KijunSen Line With Cross', overlay=true)` and only plots; the file's
last four statements are an order block appended by the conversion station:

    if showCross and crossUp
        strategy.entry("Enter Long", strategy.long)
    else if showCross and crossDown
        strategy.entry("Enter Short", strategy.short)

That block is the entire trade behaviour (PINE_SEMANTICS.md 1.17): enter on the
cross of `hl2` over the Kijun-sen line, never exit.

Indicators, transcribed from the source:

    n       = input(26, 'Length')
    h       = ta.highest(high, n)
    l       = ta.lowest(low, n)
    value   = (h + l) / 2
    crossUp   = ta.crossover(hl2, value)
    crossDown = ta.crossunder(hl2, value)

with `showCross = input(true, title='Show Candle Cross?')` gating BOTH the
plotted labels and the orders -- unlike the plotshape calls, the entry block is
not a display artifact and its `showCross` term is load-bearing.

`strategy()` is absent from the source, so every `source_*` property below is
Pine's DOCUMENTED DEFAULT: fixed / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`.

The source carries NO backtest-period header (the md's "**backtest**" section is
an image link only), so `timeframe` falls back to the mandated "1h" default of
the shared layer. That is a port choice, not something the source states: on a
different bar size every cross lands on a different bar. Recorded here rather
than presented as sourced.

FIDELITY:

* The md's prose adds nothing the code does not contain ("Kijen Sen Independent
  Line of Ichimoku Trading System"); no md-vs-source disagreement was found.
* `value = (ta.highest(high, n) + ta.lowest(low, n)) / 2` is the Kijun-sen
  line. `pine_ta.pine_highest` / `pine_lowest` return na until the window is
  full, so `value` is na for the first 25 bars and both crosses are false
  there; na propagates rather than being filled.
* `hl2` is Pine's builtin `(high + low) / 2`, not a series the source defines.
* ta.crossover/ta.crossunder compare against the previous bar; `pine_ta`'s
  modelled definitions (`a > b and a[1] <= b[1]`, and its mirror) are used, and
  an na on either side is false, as Pine treats na comparisons.
* `plotshape`, `plot` and every `color.*` are display-only and place no order;
  `size`, `text`, `textcolor` and the `color.new(colour.green, 0)` transparency
  arguments are likewise dropped.
* No exit of any kind exists, so `source_reproduce_stops` is False and a
  position open at the end of the window stays open; the only way out of a
  position is the opposing `strategy.entry` netting it (PINE_SEMANTICS.md 1.1).
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled.
"""
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMKijunSenLineWithCross_46ece4(PinePortBase, IStrategy):
    source_id = "SM_46ece42e0ed49b67"
    source_file = "KijunSen-Line-With-Cross.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {"n": 26, "showCross": True}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The file is an `indicator()` plus an order block APPENDED by the "
        "conversion station: `if showCross and crossUp -> "
        "strategy.entry(\"Enter Long\", long) else if showCross and crossDown "
        "-> strategy.entry(\"Enter Short\", short)` is the whole trade "
        "behaviour, and there is no exit call anywhere "
        "(PINE_SEMANTICS.md 1.17).",
        "`showCross` gates the orders as well as the plotted labels; it is "
        "kept as a real condition on the entry, not treated as a display "
        "switch.",
        "The source declares `indicator(...)`, not `strategy(...)`, so Pine's "
        "documented defaults apply: fixed / 1 contract, initial capital "
        "1000000, commission 0%, pyramiding 0.",
        "The source has NO backtest-period header (the md shows only a "
        "`**backtest**` image link), so the port uses the mandated \"1h\" "
        "fallback. This is a port choice with no source evidence: on another "
        "bar size every cross would land on a different bar.",
        "`value` is `(highest(high, n) + lowest(low, n)) / 2`, the Kijun-sen "
        "line; highest/lowest are na until the window is full, so `value` is "
        "na for the first 25 bars and no cross can fire there.",
        "`hl2` is Pine's builtin (high + low) / 2; it is not defined by the "
        "source.",
        "ta.crossover / ta.crossunder use pine_ta's modelled definitions; an "
        "na on either side is false, as Pine treats na comparisons.",
        "plotshape/plot and every color.* argument are display-only and place "
        "no order.",
        "No exit exists, so source_reproduce_stops is False and a position "
        "open at the window's end stays open; only an opposing entry nets it "
        "(PINE_SEMANTICS.md 1.1).",
        "md-vs-source: none found -- the md prose adds nothing the code does "
        "not contain.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the venue's rounding can differ from the engine's float "
        "quantity, which the chain verifier measures separately.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        high = dataframe["high"]
        low = dataframe["low"]
        n = int(params["n"])

        # h = ta.highest(high, n); l = ta.lowest(low, n); value = (h + l) / 2
        h = ta.pine_highest(high, n)
        l = ta.pine_lowest(low, n)
        value = (h + l) / 2.0

        # hl2 is Pine's builtin (high + low) / 2.
        hl2 = (high + low) / 2.0

        # crossUp = ta.crossover(hl2, value); crossDown = ta.crossunder(hl2, value)
        cross_up = ta.pine_crossover(hl2, value)
        cross_down = ta.pine_crossunder(hl2, value)

        show_cross = bool(params["showCross"])
        long_condition = show_cross & cross_up
        short_condition = show_cross & cross_down

        dataframe["pine_kijun"] = value
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if showCross and crossUp
        #     strategy.entry("Enter Long", strategy.long)
        # else if showCross and crossDown
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
