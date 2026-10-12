"""Port of sources/SM_c5893b39f3d0f147.pine (batch_001/3EMA.md).

Pine v5, long and short. Three EMAs of close -- short 20, mid 50, long 100 --
form a stacked-trend filter and two mutually exclusive "areas":

    short = input.int(20, "短期均线")
    mid   = input.int(50, "中期均线")
    long  = input.int(100, "长期均线")

    short_ma = ta.ema(close, short)
    mid_ma   = ta.ema(close, mid)
    long_ma  = ta.ema(close, long)

    long_condition  = short_ma > mid_ma and mid_ma > long_ma and ta.rising(mid_ma, 2)
    IN_LONG_AREA    = long_condition  and close > mid_ma  and close <= short_ma

    short_condition = short_ma < mid_ma and mid_ma < long_ma and ta.falling(mid_ma, 2)
    IN_SHORT_AREA   = short_condition and close <= mid_ma and close > short_ma

    if IN_LONG_AREA
        alert("Long " + timeframe.period + " " + syminfo.basecurrency)
    else if IN_SHORT_AREA
        alert("Short " + timeframe.period + " " + syminfo.basecurrency)

    p3 = plot(long_ma, ...)                 // display-only
    p2 = plot(mid_ma, ...)
    p1 = plot(short_ma, ...)
    fill(p1, p2, ...)
    fill(p1, p2, ...)
    bgcolor(IN_LONG_AREA  ? ... : na)
    bgcolor(IN_SHORT_AREA ? ... : na)

    if IN_LONG_AREA
        strategy.entry("Enter Long", strategy.long)
    else if IN_SHORT_AREA
        strategy.entry("Enter Short", strategy.short)

Only the LAST if/else-if chain trades. The earlier chain exists solely to raise
`alert()` calls, which place no order, and the plots, fills and bgcolors are
display-only: they are all reproduced as no code. The `else if` is kept, so a
bar meeting both conditions takes the LONG branch only -- in practice the two
areas cannot both be true on one bar, since one needs close <= short_ma and the
other close > short_ma, so at most one entry is placed per bar.

Both entries are plain market orders with no stop, limit or quantity argument,
so the engine fills them at the NEXT bar's open using the script's default
sizing. The source contains no `strategy.close`, no `strategy.exit` and no stop
of any kind: a position is only ever left by the opposite entry, which the
engine models as a reversal (close the old side, open the new one). Pine's
`pyramiding` default of 0 additionally means a repeated signal while already
positioned in that direction is ignored.

The source declares `indicator(...)`, not `strategy(...)`, so Pine's documented
defaults are what the `source_*` attributes record: fixed sizing of 1, 0%
commission, pyramiding 0, initial capital 1000000 USD.

FIDELITY: `ta.rising` / `ta.falling` are not exposed by pine_ta, so they are
translated in this file from Pine's definition -- the source is "now rising for
`length` bars", i.e. source[i] > source[i+1] for every i in 0..length-1, so the
steps are CONSECUTIVE and equality breaks the run -- and na comparisons are
false, as Pine treats them. `ta.ema` is pine_ta.pine_ema, seeded with the first
non-na observation (an unpublished TradingView rule; see PINE_SEMANTICS.md 3.1).
"""
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _rising(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.rising`: strictly higher on each of the last `length` steps.

    Pine's documented test is "is now rising for `length` bars long" --
    source[i] > source[i+1] for every i in 0..length-1 -- so the steps are
    CONSECUTIVE and equality breaks the run. na on either side of a comparison
    makes it false, as Pine treats na comparisons.
    """
    rising = pd.Series(True, index=series.index)
    for step in range(int(length)):
        rising &= series.shift(step) > series.shift(step + 1)
    return rising


def _falling(series: pd.Series, length: int) -> pd.Series:
    """Pine `ta.falling`: strictly lower on each of the last `length` steps."""
    falling = pd.Series(True, index=series.index)
    for step in range(int(length)):
        falling &= series.shift(step) < series.shift(step + 1)
    return falling


class SM3Ema_c5893b(PinePortBase, IStrategy):
    source_id = "SM_c5893b39f3d0f147"
    source_file = "3EMA.md"
    # /*backtest ... period: 5m, basePeriod: 1m
    timeframe = "5m"
    can_short = True
    source_defaults = {"short": 20, "mid": 50, "long": 100}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.close / strategy.exit / stop anywhere in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "ta.rising / ta.falling are not exposed by pine_ta, so they are "
        "translated in this file from Pine's definition: the source is now "
        "rising (falling) for `length` bars, i.e. source[i] > source[i+1] "
        "(source[i] < source[i+1]) for EVERY i in 0..length-1 -- the steps are "
        "consecutive, with equality breaking the run. TradingView additionally "
        "documents that na values are skipped when counting the `length` bars; "
        "how it does so is not published, and it cannot bite here because "
        "pine_ema returns a value from bar 0 and never an interior na.",
        "ta.ema is seeded with the first non-na observation (pine_ta's "
        "documented model); TradingView's seeding rule is unpublished, so the "
        "three EMAs -- and therefore every condition built on them -- differ "
        "from the original platform's until the recursion converges. See "
        "PINE_SEMANTICS.md 3.1.",
        "The source declares `indicator(...)`, not `strategy(...)`, so no "
        "strategy() properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, "
        "pyramiding 0, initial capital 1000000 USD. On TradingView "
        "`strategy.entry` inside an indicator does not compile; the host named "
        "by the source's /*backtest header and Detail link "
        "(fmz.com/strategy/362572) is what ran it, and that platform's Pine "
        "dialect -- not TradingView -- is the original behaviour this port "
        "reproduces.",
        "The source has no exit of any kind: no strategy.close, no "
        "strategy.exit, no stop or limit order. A position is only left by the "
        "opposite entry, which the engine models as a reverse fill (close the "
        "old side, open the new one). source_reproduce_stops is False "
        "accordingly.",
        "The first if / else-if chain in the source calls alert() only and "
        "places no order; it is reproduced as no code. plot / fill / bgcolor "
        "are display-only. The markdown table of Strategy Arguments confirms "
        "the three defaults (20 / 50 / 100).",
        "The final entry chain is an if / ELSE-IF, so a bar satisfying both "
        "IN_LONG_AREA and IN_SHORT_AREA takes the long branch only. The port "
        "keeps the `elif` rather than testing both.",
        "The backtest header declares period: 5m with basePeriod: 1m "
        "(intrabar data). The engine evaluates at bar close and fills at the "
        "next open, so intrabar path differences are not modelled.",
        "The backtest window in the header (2022-05-03 to 2022-05-09) is not "
        "applied: the port runs on whatever range the caller supplies.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        short_ma = ta.pine_ema(close, params["short"])
        mid_ma = ta.pine_ema(close, params["mid"])
        long_ma = ta.pine_ema(close, params["long"])
        dataframe["short_ma"] = short_ma
        dataframe["mid_ma"] = mid_ma
        dataframe["long_ma"] = long_ma

        # long_condition = (short_ma > mid_ma) and (mid_ma > long_ma) and (ta.rising(mid_ma, 2))
        long_condition = (short_ma > mid_ma) & (mid_ma > long_ma) & _rising(mid_ma, 2)
        # IN_LONG_AREA = long_condition and (close > mid_ma) and (close <= short_ma)
        dataframe["IN_LONG_AREA"] = (
            long_condition & (close > mid_ma) & (close <= short_ma)
        )
        # short_condition = (short_ma < mid_ma) and (mid_ma < long_ma) and (ta.falling(mid_ma, 2))
        short_condition = (short_ma < mid_ma) & (mid_ma < long_ma) & _falling(mid_ma, 2)
        # IN_SHORT_AREA = short_condition and (close <= mid_ma) and (close > short_ma)
        dataframe["IN_SHORT_AREA"] = (
            short_condition & (close <= mid_ma) & (close > short_ma)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "IN_LONG_AREA": dataframe["IN_LONG_AREA"].to_numpy(),
            "IN_SHORT_AREA": dataframe["IN_SHORT_AREA"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if IN_LONG_AREA / strategy.entry("Enter Long", strategy.long)
        # else if IN_SHORT_AREA / strategy.entry("Enter Short", strategy.short)
        if ctx["IN_LONG_AREA"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["IN_SHORT_AREA"][i]:
            broker.entry("Enter Short", "short")
