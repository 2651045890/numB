"""Port of sources/SM_3fbebcbb47eff286.pine (batch_001/3EMA-Boullinger-PIVOT.md).

Pine v4, long and short. The script draws three EMAs of close and a Bollinger
band pair, and then trades PIVOT confirmations -- and nothing else:

    periodo1 = input(8,  ...)          // EMAs of close, plotted only
    periodo2 = input(20, ...)
    periodo3 = input(200, ...)
    plot(ema(close, periodo1), ...)
    plot(ema(close, periodo2), ...)
    plot(ema(close, periodo3), ...)

    longitudbb = input(20,  ...)       // bb() over `fuente`, plotted only
    multbb     = input(2.0, ...)
    fuente     = input(close, ...)
    [mm, banda_sup, banda_inf] = bb(fuente, longitudbb, multbb)
    ps = plot(banda_sup, ...)
    pi = plot(banda_inf, ...)

    dist = input(6, ...)

    pl = pivotlow(low, dist, dist)
    if not na(pl)
        strategy.entry("Enter Long", strategy.long)

    ph = pivothigh(high, dist, dist)
    if not na(ph)
        strategy.entry("Enter Short", strategy.short)

Only the two `strategy.entry` calls trade. Every `plot()` / `fill()` in the
source is display-only, and the three EMAs and the Bollinger bands are never
read by the script body: they are reproduced as columns so the port still
computes every series the source computes, but they place no condition.

`pivotlow` / `pivothigh` are confirmed `dist` (=6) bars AFTER the swing bar, and
their value is reported on the confirmation bar. So the signal bar is six bars
after the low/high it names, and the entry is a market order placed on that bar:
the engine fills it at the NEXT bar's open, seven bars after the pivot. Both
entries are plain market orders -- no stop, limit, quantity or `when` argument --
so they use the script's default sizing, and a signal against an open position
reverses it (Pine's `pyramiding` default of 0 ignores a same-direction stacking
entry). No `strategy.close` / `strategy.exit` / `strategy.cancel` appears
anywhere, so the only way out of a position is the opposite pivot signal.

The two entries are separate `if` statements, not an if/else-if chain, so they
keep the source's written order: long first, then short. (On one bar they
cannot both fire -- `pl` needs that bar to be the window's unique low and `ph`
its unique high, which would make the whole window equal and therefore not
unique -- but the port reproduces the source's two independent `if`s rather
than assuming that.)

The source declares no `strategy()` block at all -- it is a `study()` script that
calls `strategy.entry` -- so the Pine-documented defaults are what the
`source_*` attributes below record: fixed sizing of 1, 0% commission,
pyramiding 0, initial capital 1000000 USD. See source_fidelity_notes for the
platform caveat that carries and for the pivot-confirmation finding.

FIDELITY: `pivotlow`/`pivothigh` are pine_ta's modelled rule (the middle bar must
be the UNIQUE strict extreme of the left+right+1 window; TradingView does not
publish its tie handling). `bb()` is translated as middle = sma(source, length),
upper/lower = middle +/- mult*stdev(source, length) with the population standard
deviation, which is Pine v4's built-in definition and pine_ta's stdev model.
Pine v4 `ema` is pine_ta.pine_ema (seeded with the first non-na observation --
an unpublished TradingView rule, recorded as a parity risk in
PINE_SEMANTICS.md 3.1). `input.source` is resolved through pine_ta.pine_source.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _na(value) -> bool:
    """Pine `na(x)`; pine_ta reports na as NaN."""
    return value != value


class SM3EmaPivot_3fbebc(PinePortBase, IStrategy):
    source_id = "SM_3fbebcbb47eff286"
    source_file = "3EMA-Boullinger-PIVOT.md"
    # /*backtest ... period: 1h, basePeriod: 15m
    timeframe = "1h"
    can_short = True
    source_defaults = {
        "periodo1": 8,
        "periodo2": 20,
        "periodo3": 200,
        "longitudbb": 20,
        "multbb": 2.0,
        "fuente": "close",
        "dist": 6,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The source places no stop, limit or exit order of any kind, so the engine
    # has no resting level for the framework's stop hooks to reproduce.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "PIVOT CONFIRMATION (the reason mapping.csv flags this source): "
        "`pivotlow(low, dist, dist)` / `pivothigh(high, dist, dist)` confirm a "
        "swing point `dist` = 6 bars after the bar that made it, and the source "
        "enters on the confirmation bar. That is a LAG, not future data: the "
        "value reported on bar t is decided by bars t-6..t alone, and pine_ta's "
        "pivot is causal (validate_pine.py's prefix recompute passes on this "
        "port). It does mean every entry is placed 6 bars after the extreme it "
        "names and fills at the following bar's open, 7 bars after it.",
        "pivothigh/pivotlow tie handling is pine_ta's modelled rule: the middle "
        "bar must be the UNIQUE strict extreme of the left+right+1 window. "
        "TradingView does not publish how it breaks ties between equal "
        "highs/lows, so a different rule there would confirm a different set of "
        "pivots.",
        "The source declares `study(...)`, not `strategy(...)`, so no "
        "strategy() properties exist and Pine's documented defaults are used: "
        "default_qty_type fixed, default_qty_value 1, commission 0%, pyramiding "
        "0, initial capital 1000000 USD. On TradingView `strategy.entry` inside "
        "a study does not compile; the host named by the source's /*backtest "
        "header and Detail link (fmz.com/strategy/361802) is what ran it, and "
        "that platform's Pine dialect -- not TradingView -- is the original "
        "behaviour this port reproduces.",
        "The three EMAs (periodo1/2/3 = 8/20/200) and the Bollinger bands "
        "(longitudbb = 20, multbb = 2.0 over `fuente`, default close) are "
        "computed and plotted but never read by the script body: they are "
        "display-only and have no effect on entries or exits. They are kept as "
        "columns so the port still computes every series the source computes.",
        "bb() is translated as middle = sma(source, length), "
        "upper/lower = middle +/- mult * stdev(source, length) with the "
        "POPULATION standard deviation (ddof=0), which is how pine_ta models "
        "Pine's stdev. Display-only, so a different convention there would not "
        "change a single trade.",
        "ta.ema is seeded with the first non-na observation (pine_ta's "
        "documented model); TradingView's seeding rule is unpublished, so the "
        "three EMAs differ from the original platform's until the recursion "
        "converges. They are display-only here.",
        "The markdown prose describes the EMAs as '4, 20 and 200 last candles' "
        "and then lists 'Fast EMA1 = 8'; the code's input() default is 8, which "
        "is what this port uses (code wins over prose). Either way the EMAs are "
        "display-only.",
        "The two entries are written as two separate `if` statements, not an "
        "if/else-if chain, and the port keeps that shape and the source's order "
        "(long, then short) instead of collapsing them.",
        "The backtest header declares period: 1h with basePeriod: 15m "
        "(intrabar data). The engine evaluates at bar close and fills at the "
        "next open, so intrabar path differences are not modelled.",
        "The input.time-style backtest window in the header (2022-04-07 to "
        "2022-05-06) is not applied: the port runs on whatever range the caller "
        "supplies.",
        "source_reproduce_stops is False: the source has no stop-based exit, so "
        "there is no engine level for custom_stoploss to mirror.",
    ]

    def pine_indicators(self, dataframe, params):
        # plot(ema(close, periodo1/2/3)) -- display-only in the source.
        dataframe["ema_periodo1"] = ta.pine_ema(dataframe["close"], params["periodo1"])
        dataframe["ema_periodo2"] = ta.pine_ema(dataframe["close"], params["periodo2"])
        dataframe["ema_periodo3"] = ta.pine_ema(dataframe["close"], params["periodo3"])
        # [mm, banda_sup, banda_inf] = bb(fuente, longitudbb, multbb)
        source = ta.pine_source(dataframe, params["fuente"])
        basis = ta.pine_sma(source, params["longitudbb"])
        deviation = params["multbb"] * ta.pine_stdev(source, params["longitudbb"])
        dataframe["mm"] = basis
        dataframe["banda_sup"] = basis + deviation
        dataframe["banda_inf"] = basis - deviation
        # pl = pivotlow(low, dist, dist) / ph = pivothigh(high, dist, dist)
        dataframe["pl"] = ta.pine_pivotlow(dataframe["low"], params["dist"], params["dist"])
        dataframe["ph"] = ta.pine_pivothigh(dataframe["high"], params["dist"], params["dist"])
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "pl": dataframe["pl"].to_numpy(dtype=float),
            "ph": dataframe["ph"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # pl = pivotlow(low, dist, dist) / if not na(pl)
        if not _na(ctx["pl"][i]):
            broker.entry("Enter Long", "long")
        # ph = pivothigh(high, dist, dist) / if not na(ph)
        if not _na(ctx["ph"][i]):
            broker.entry("Enter Short", "short")
