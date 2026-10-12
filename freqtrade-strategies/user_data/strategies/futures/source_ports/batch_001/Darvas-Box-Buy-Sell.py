"""Port of sources/SM_9e9701dfa19cc88a.pine (batch_001/Darvas-Box-Buy-Sell.md).

Pine v4. The file declares `study("Darvas Box Buy Sell")`, NOT `strategy(...)`:
the two `strategy.entry` calls at the bottom are an order block APPENDED to the
indicator by the converter site that published it (fmz.com/strategy/366948,
named in the md's Detail link). Pine does not compile `strategy.entry` inside
`study()`, so the "original strategy" is the indicator PLUS that appended block,
and the trading behaviour it defines is entry-only:

    if Buy
        strategy.entry("Enter Long", strategy.long)
    else if Sell
        strategy.entry("Enter Short", strategy.short)

The indicator is ceyhun's Darvas box:

    LL        = lowest(low, boxp)
    k1        = highest(high, boxp)
    k2        = highest(high, boxp - 1)
    k3        = highest(high, boxp - 2)
    NH        = valuewhen(high > k1[1], high, 0)
    box1      = k3 < k2
    TopBox    = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, NH, 0)
    BottomBox = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, LL, 0)
    Buy       = crossover(close, TopBox)
    Sell      = crossunder(close, BottomBox)

`barssince(high > k1[1]) == boxp - 2` is the bar on which a fresh box has been
confirmed for `boxp - 2` bars, `box1` requires the box to be narrowing
(k3 < k2), `NH` is the new high that started the box, and TopBox / BottomBox
latch that bar's `NH` / `LL` forward as the box boundaries. `Buy` / `Sell` fire
when the close crosses them.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* The four `valuewhen(...)` / `barssince(...)` / `highest(...)` / `lowest(...)`
  builtins are Pine v4 bare forms and map onto pine_ta's `pine_valuewhen` /
  `pine_barssince` / `pine_highest` / `pine_lowest`, which reproduce Pine's
  na semantics (occurrence 0 = most recent; na before the first true; na until
  the window is full).
* In `valuewhen(condition, source, 0)` the trailing `0` is the OCCURRENCE
  argument, not a fill value. The result stays na until the condition first
  holds, and `crossover(close, na)` is false, so a missing box simply places no
  order -- it is not treated as a box at price 0.
* `box1 = k3 < k2` compares two rolling maxima; before either window is full
  both are na, the comparison is false, and the port's boolean term is
  likewise False. `k3 = highest(high, boxp - 2)` needs `boxp >= 3`; the source
  declares `minval=1`, so a `boxp` of 1 or 2 would make `highest(high, 0)` /
  `highest(high, -1)` nonsensical in Pine too. The default is 5 and the port is
  faithful at every value where Pine's own expression is meaningful.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply (fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000).
* `plot` / `plotshape` / `alertcondition` are display- or alert-only and place
  no order; dropped.
* The header's backtest window (2022-04-30 to 2022-05-29) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 5m` is the host's intrabar granularity for filling 45m bars, not
  the strategy's period. The header's `period: 45m` is what `timeframe` uses.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMDarvasBoxBuySell_9e9701(PinePortBase, IStrategy):
    source_id = "SM_9e9701dfa19cc88a"
    source_file = "Darvas-Box-Buy-Sell.md"
    timeframe = "45m"
    can_short = True
    # Input defaults exactly as written.
    source_defaults: dict = {"boxp": 5}
    # study(...), not strategy(...): Pine's documented defaults apply.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop / limit / trail anywhere.
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The file declares study(...), not strategy(...): the strategy.entry "
        "pair at the bottom is an order block appended by the converter site "
        "(fmz.com/strategy/366948 per the md's Detail link). The port reproduces "
        "the indicator PLUS that appended block, i.e. entry-only behaviour.",
        "valuewhen(...)'s trailing 0 is the OCCURRENCE argument (most recent), "
        "not a fill value. TopBox/BottomBox stay na until the box condition "
        "first holds, and crossover(close, na) is false, so a missing box "
        "places no order rather than being read as a box at price 0.",
        "barssince(high > k1[1]) is na before the first true bar; the comparison "
        "`== boxp - 2` is then false, so the precondition simply does not hold "
        "during the warmup. pine_barssince reproduces that.",
        "highest/lowest are na until their window is full (Pine v4); "
        "pine_highest/pine_lowest use min_periods = length to match. box1 = k3 "
        "< k2 is therefore false during the warmup, exactly as in Pine, and the "
        "port's boolean term is likewise False rather than a comparison on 0.",
        "k3 = highest(high, boxp - 2) needs boxp >= 3. The source declares "
        "minval=1, so a boxp of 1 or 2 makes highest(high, 0) / highest(high, "
        "-1) nonsensical in Pine itself; the port is faithful at every value "
        "where Pine's own expression is meaningful, and the default is 5.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit line. "
        "A position is only left by the opposite entry, which the engine models "
        "as a reverse fill. source_reproduce_stops is False accordingly.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "MD-vs-SOURCE: the md front matter names the author as 'ChaoZhang', "
        "while the source file's own header reads '(c) ceyhun' -- the md "
        "records the fmz uploader, the source the original author. No effect on "
        "behaviour; recorded, not reconciled.",
        "The md's argument table (v_input_1 = 5 Length) and its embedded source "
        "block are verbatim identical to the .pine source.",
        "The header's backtest window is extraction metadata, not an input.time "
        "filter, so the port runs on whatever range the caller supplies; "
        "basePeriod: 5m is the host's intrabar fill granularity, not the "
        "strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        boxp = int(params["boxp"])
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # LL = lowest(low, boxp)
        ll = ta.pine_lowest(low, boxp)
        # k1 = highest(high, boxp); k2 = highest(high, boxp - 1); k3 = highest(high, boxp - 2)
        k1 = ta.pine_highest(high, boxp)
        k2 = ta.pine_highest(high, boxp - 1)
        k3 = ta.pine_highest(high, boxp - 2)

        # NH = valuewhen(high > k1[1], high, 0)
        new_high = high > k1.shift(1)
        nh = ta.pine_valuewhen(new_high, high, 0)

        # box1 = k3 < k2
        box1 = k3 < k2
        # TopBox = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, NH, 0)
        # BottomBox = valuewhen(barssince(high > k1[1]) == boxp - 2 and box1, LL, 0)
        box_confirmed = (ta.pine_barssince(new_high) == boxp - 2) & box1
        top_box = ta.pine_valuewhen(box_confirmed, nh, 0)
        bottom_box = ta.pine_valuewhen(box_confirmed, ll, 0)

        dataframe["pine_ll"] = ll
        dataframe["pine_nh"] = nh
        dataframe["pine_top_box"] = top_box
        dataframe["pine_bottom_box"] = bottom_box
        # Buy = crossover(close, TopBox); Sell = crossunder(close, BottomBox)
        dataframe["pine_long_condition"] = ta.pine_crossover(close, top_box)
        dataframe["pine_short_condition"] = ta.pine_crossunder(close, bottom_box)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "top_box": dataframe["pine_top_box"].to_numpy(),
            "bottom_box": dataframe["pine_bottom_box"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if Buy
        #     strategy.entry("Enter Long", strategy.long)
        # else if Sell
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
