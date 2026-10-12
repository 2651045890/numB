"""Port of sources/SM_c7c850b45fadbe99.pine (batch_001/Brick-count-Renko.md).

Pine v4. The file declares `study("Renko count", overlay=false)`, NOT
`strategy(...)`: the two `strategy.entry` calls at the bottom are an order block
APPENDED to the indicator by the converter that published it (fmz.com/strategy/
368734, named in the md's Detail link). Pine does not compile `strategy.entry`
inside `study()`, so the "original strategy" is the indicator PLUS that appended
block, and the trading behaviour it defines is entry-only:

    if brick_red
       strategy.entry("buy", strategy.long)
    else if brick_green
        strategy.entry("sell", strategy.short)

The indicator itself is a renko-style brick counter:

    counter_green = iff(close > open, 1, 0)      # a green bar -> 1, else 0
    counter_red   = iff(close > open, 0, 1)      # a red bar   -> 1, else 0
    size          = iff(bar_index>39, 40, bar_index+1)
    pine_sum(x, y) =>
        sum = 0.0
        for i = 0 to y - 1
            sum := sum + x[i]
    brick_red   = pine_sum(counter_red,   size)
    brick_green = pine_sum(counter_green, size)

so `brick_red` / `brick_green` are the NUMBER of red / green bars in the last
`size` bars, where `size` ramps 1,2,3,... and is clamped at 40.

THE ENTRY CONDITION IS THAT COUNT USED AS A BARE TRUTH VALUE, and this is the
part that must not be "normalised". `if brick_red` is TRUE whenever the count
is non-zero, i.e. whenever the window contains at least one red bar, and
`brick_red + brick_green == size` exactly, so at most ONE of the two can be
zero. The literal consequence is severe and is reproduced rather than fixed:
a long is placed on essentially every bar, and a short is reachable only when
ALL `size` bars in the window are green (`brick_red == 0`). Rewriting the test
as `brick_red == 1` / `brick_red > 0`-style normalisation, or bool()-ing the
column, would silently change which bars trade -- exactly the failure mode
PINE_SEMANTICS.md 1.17 warns about for this converter family.

There is NO exit of any kind in the source -- no `strategy.close`, no
`strategy.exit`, and not even a commented-out one. A position is therefore only
ever left by the opposite entry, which the engine models as a reversal.
`pyramiding` keeps Pine's default of 0, so a repeated signal while already
positioned that way is ignored.

FIDELITY:

* `pine_sum(x, size)` is a rolling sum over the window `size`, and `size` is
  `min(bar_index + 1, 40)` for every bar (the `bar_index>39` test switches it to
  a hard 40 exactly when `bar_index+1` would exceed it). On bars 0..38 the
  window is therefore the whole history so far, and from bar 39 on it is the
  last 40 bars, which is `counter.rolling(40, min_periods=1).sum()` exactly --
  an identity, not an approximation, and written that way.
* The truth value is preserved as a NUMBER in the port: `if ctx["brick_red"][i]`
  is Python's non-zero test, which agrees with Pine's (`0` false, any other
  number true). The column is NOT cast to bool.
* `x[i]` inside the loop is a history reference with a per-bar offset; the
  rolling sum reproduces it. The counter series never contains na, so the sum
  never becomes na and `brick_red`/`brick_green` are finite on every bar.
* `cross(brick_red, brick_green)` guards only a `label.new(...)` drawing call;
  it places no order and is dropped.
* `plot(brick_red, ...)` / `plot(brick_green, ...)` are display-only; dropped.
* The source declares `study(...)`, so no strategy() properties exist and
  Pine's documented defaults apply: fixed size 1, 0% commission, pyramiding 0,
  initial capital 1000000 USD.
* MD-vs-SOURCE: the md's Strategy Description is the two characters "砖形指标"
  and its author line reads "Zer3192"; the source file carries only the MPL
  header and no author. The md argument table is empty and matches the source
  (no `input()` call exists). The md's embedded source block is verbatim
  identical to the .pine source.
* The header's backtest window (2021-05-08 to 2022-05-07) is extraction
  metadata, not an `input.time` filter, so no data is trimmed. The header's
  `basePeriod: 15m` is the host's intrabar granularity for filling 4h bars, not
  the strategy's period; the header's `period: 4h` is what `timeframe` uses.
* No stop, limit or trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled (PINE_SEMANTICS.md 1.6 measures the rounding separately).
"""
import pandas as pd
from freqtrade.strategy import IStrategy

from pine_port_base import PinePortBase


class SMBrickCountRenko_c7c850(PinePortBase, IStrategy):
    source_id = "SM_c7c850b45fadbe99"
    source_file = "Brick-count-Renko.md"
    timeframe = "4h"
    can_short = True
    # No input() call exists anywhere in the source.
    source_defaults: dict = {}
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
        "pair at the bottom is an order block appended by the converter "
        "(fmz.com/strategy/368734 per the md's Detail link). The port "
        "reproduces the indicator PLUS that appended block, i.e. entry-only "
        "behaviour (PINE_SEMANTICS.md 1.17).",
        "`if brick_red` / `else if brick_green` test the brick COUNTS as bare "
        "truth values (0 is false, any other number is true), NOT as "
        "booleans. The port keeps the integer/float semantics: `if "
        "ctx[\"brick_red\"][i]` is Python's non-zero test, matching Pine. The "
        "column is deliberately NOT bool()-ed and NOT rewritten as `== 1` / "
        "`> 0`; PINE_SEMANTICS.md 1.17 records that such a rewrite silently "
        "kills the short side of this converter family.",
        "Because brick_red + brick_green == size and both are counts, "
        "`if brick_red` is true on essentially every bar (any red bar in the "
        "window) and `brick_green` is only reached when the whole window is "
        "green. The strategy therefore goes long almost unconditionally. That "
        "is what the source says; it is reproduced, not repaired.",
        "pine_sum(counter, size) is a rolling sum. size = iff(bar_index>39, 40, "
        "bar_index+1) equals min(bar_index+1, 40) on every bar, so the window is "
        "the full history up to 40 bars and the last 40 after that, i.e. "
        "counter.rolling(40, min_periods=1).sum() exactly -- an identity.",
        "The counter series contains no na, so the sums are finite on every "
        "bar and the truthiness test is never applied to na.",
        "`cross(brick_red, brick_green)` guards only a label.new(...) drawing "
        "call and places no order; dropped, together with the two plot(...) "
        "calls.",
        "The source declares study(...), so no strategy() properties exist and "
        "Pine's documented defaults are used: default_qty_type fixed, "
        "default_qty_value 1, commission 0%, pyramiding 0, initial capital "
        "1000000 USD.",
        "The source has NO exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order, and no commented-out exit "
        "line. A position is only left by the opposite entry, modelled as a "
        "reverse fill; source_reproduce_stops is False.",
        "MD-vs-SOURCE: the md's Strategy Description is the two characters "
        "'砖形指标' and it names the author 'Zer3192'; the source carries no "
        "author line at all. No effect on behaviour; recorded, not reconciled.",
        "The header's backtest window is extraction metadata, not an "
        "input.time filter, so the port runs on whatever range the caller "
        "supplies; basePeriod: 15m is the host's intrabar fill granularity, "
        "not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 1.6).",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        open_ = dataframe["open"]
        close = dataframe["close"]

        # counter_green = iff(close > open, 1, 0)
        counter_green = (close > open_).astype(float)
        # counter_red = iff(close > open, 0, 1)
        counter_red = (~(close > open_)).astype(float)

        # size = iff(bar_index>39, 40, bar_index+1) == min(bar_index + 1, 40).
        # pine_sum(x, size) sums x over exactly that window, so the rolling sum
        # below is the same quantity, not an approximation of it.
        brick_red = counter_red.rolling(40, min_periods=1).sum()
        brick_green = counter_green.rolling(40, min_periods=1).sum()

        dataframe["pine_counter_red"] = counter_red
        dataframe["pine_counter_green"] = counter_green
        dataframe["pine_brick_red"] = brick_red
        dataframe["pine_brick_green"] = brick_green
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "brick_red": dataframe["pine_brick_red"].to_numpy(),
            "brick_green": dataframe["pine_brick_green"].to_numpy(),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if brick_red
        #    strategy.entry("buy", strategy.long)
        # else if brick_green
        #     strategy.entry("sell", strategy.short)
        #
        # The tests are TRUTHINESS tests on the brick counts (Pine treats a
        # non-zero number as true), kept as plain Python truthiness here.
        if ctx["brick_red"][i]:
            broker.entry("buy", "long")
        elif ctx["brick_green"][i]:
            broker.entry("sell", "short")
