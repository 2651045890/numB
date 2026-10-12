"""Port of sources/SM_02be0d3ecf7fd5c9.pine (batch_001/Buy-Sell-Strat.md).

Pine v5. A 9/21 EMA crossover gated by three filters: the current volume must
be well above the average of the previous five bars, price must be on the
crossover's side of the fast EMA, and the last four closes must form a reversal
pattern:

    a = ta.ema(close, 9)
    b = ta.ema(close, 21)
    crossUp   = ta.crossover(a, b)
    crossDown = ta.crossunder(a, b)

    volAvg = 0
    for i = 1 to 5
        volAvg := volAvg + volume[i]
    volAvg := volAvg / 5

    reversalPatternUp   = close > close[1] and close[1] > close[2]
                          and close[3] > close[2] and close > close[3]
    reversalPatternDown = close < close[1] and close[1] < close[2]
                          and close[3] < close[2] and close < close[3]

    if (crossUp)
        strategy.entry("long",  strategy.long,
                       when = ((volume * 0.85) > volAvg and close > a
                               and reversalPatternUp == true))
    if (crossDown)
        strategy.entry("short", strategy.short,
                       when = ((volume * 0.85) > volAvg and close < a
                               and reversalPatternDown == true))

The `when=` guard sits INSIDE the `if (crossUp)` block, so the effective entry
condition is the conjunction of the two; the port reproduces that conjunction,
it does not promote the guard into the outer `if` (which would be identical
here) nor drop the outer test (which would not be).

`volAvg` is the mean of `volume[1] .. volume[5]`, i.e. the five bars BEFORE the
current one -- the loop starts at 1, so the current bar's volume is not in the
average. It is `volume.shift(1).rolling(5).mean()`, not `rolling(5)` on the
current bar.

`strategy()` declares only `title` / `overlay`, so every property is Pine's
documented default: `strategy.fixed` / 1 contract, initial capital 1000000,
commission 0%, pyramiding 0, `process_orders_on_close=false`. There is no
`input()` in the source, so `source_defaults` is empty and every length is a
literal in the source and a literal here.

There is no exit call: the `strategy.close` block at the end of the source is
COMMENTED OUT, so a position is only ever closed or reversed by the opposite
entry. `source_reproduce_stops` is therefore False and a position still open at
the end of the window stays open. Both ids exist and can be live, so
`can_short` is True.

FIDELITY:

* `reversalPatternUp == true` compares a bool to a bool; `== true` places no
  additional restriction, and no `bool`-as-number comparison is involved
  (PINE_SEMANTICS.md 1.16 does not apply -- there are no `input(type=bool)`
  values in this source at all).
* The commented-out exit block is not restored. The source's comments state the
  author's intent (`close_condition_long = close < a`), but they place no
  condition, and reviving them would add exits the shipped script never had.
* md-vs-source: the md prose says the reversal bar carries "15% higher average
  volume than previous 5 candles". The code tests `volume * 0.85 > volAvg`,
  i.e. `volume > volAvg / 0.85`, which is about 17.6% above the average, and it
  compares against the average of the preceding five bars. The code's constant
  is used; the prose is recorded, not reconciled.
* md-vs-source: the md prose lists the filters as independent features; the
  code ANDs all three into one `when=` expression.
* `ta.ema` follows pine_ta's documented first-value seeding, listed in
  PINE_SEMANTICS.md as a parity risk (`seed='first'`).
* `ta.crossover` / `ta.crossunder` are `a > b and a[1] <= b[1]` and its mirror;
  na on either side is false, so no signal can exist while an EMA is warming up.
* `plot` / `plotchar` / `plotshape` are display-only and place no condition.
* The `/*backtest` header declares `period: 2h`; its `basePeriod: 15m` is the
  FMZ backtester's own granularity for filling those 2h bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled; the chain verifier measures the rounding separately.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMBuySellStrat_02be0d(PinePortBase, IStrategy):
    source_id = "SM_02be0d3ecf7fd5c9"
    source_file = "Buy-Sell-Strat.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "No exit call exists: the source's strategy.close block is commented "
        "out, so a position is only closed or reversed by the opposite entry. "
        "source_reproduce_stops is False and a position open at the window end "
        "stays open.",
        "The commented-out exit block is NOT restored -- it places no condition "
        "in the shipped script.",
        "volAvg averages volume[1]..volume[5] -- the five bars BEFORE the "
        "current one -- because the loop starts at 1. Not a rolling mean over "
        "the current bar.",
        "md-vs-source: the md prose says '15% higher average volume'; the code "
        "tests `volume * 0.85 > volAvg` (~17.6% above the preceding 5-bar "
        "average). The code's constant is used, the prose recorded.",
        "The three filters are ANDed into one `when=` expression evaluated "
        "inside the `if (crossUp)` / `if (crossDown)` block; both the outer "
        "test and the guard are reproduced.",
        "There is no input() in the source, so source_defaults is empty and "
        "every length (9, 21, 5, 0.85) stays a literal in the port.",
        "`reversalPatternUp == true` is a bool-to-bool comparison and places no "
        "extra restriction; no numeric bool comparison exists here, so "
        "PINE_SEMANTICS.md 1.16 does not apply.",
        "ta.ema uses pine_ta's first-value seeding, a parity risk recorded in "
        "PINE_SEMANTICS.md 3.1.",
        "crossover/crossunder are false while an EMA is na, so nothing fires "
        "during warm-up.",
        "plot/plotchar/plotshape are display-only and place no condition.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled; the chain verifier measures the rounding "
        "separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        a = ta.pine_ema(close, 9)
        b = ta.pine_ema(close, 21)
        cross_up = ta.pine_crossover(a, b)
        cross_down = ta.pine_crossunder(a, b)
        # volAvg = sum(volume[1..5]) / 5 -- the five bars BEFORE this one.
        vol_avg = dataframe["volume"].shift(1).rolling(5, min_periods=5).mean()
        volume = dataframe["volume"]
        reversal_up = (
            (close > close.shift(1))
            & (close.shift(1) > close.shift(2))
            & (close.shift(3) > close.shift(2))
            & (close > close.shift(3))
        )
        reversal_down = (
            (close < close.shift(1))
            & (close.shift(1) < close.shift(2))
            & (close.shift(3) < close.shift(2))
            & (close < close.shift(3))
        )
        volume_ok = (volume * 0.85) > vol_avg
        dataframe["pine_ema_fast"] = a
        dataframe["pine_ema_slow"] = b
        dataframe["pine_vol_avg"] = vol_avg
        dataframe["pine_reversal_up"] = reversal_up.fillna(False)
        dataframe["pine_reversal_down"] = reversal_down.fillna(False)
        dataframe["pine_long_condition"] = (
            cross_up & volume_ok & (close > a) & reversal_up.fillna(False)
        ).fillna(False)
        dataframe["pine_short_condition"] = (
            cross_down & volume_ok & (close < a) & reversal_down.fillna(False)
        ).fillna(False)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (crossUp)
        #     strategy.entry("long", strategy.long, when = (...))
        if ctx["long_condition"][i]:
            broker.entry("long", "long")
        # if (crossDown)
        #     strategy.entry("short", strategy.short, when = (...))
        if ctx["short_condition"][i]:
            broker.entry("short", "short")
