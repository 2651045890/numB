"""Port of sources/SM_53585e263bbea19a.pine (batch_001/Hull-Suite-Strategy.md).

Pine v4 (InSilico's "Basic Hull Ma Pack", wrapped as a strategy by DashTrader),
both directions, on the `/*backtest` header's `period: 30m`. The trading logic
is four lines:

    HULL  = Mode(modeSwitch, src, length)
    MHULL = HULL[0]
    SHULL = HULL[2]

    if HULL[0] > HULL[2] and testPeriod()
        strategy.entry("buy", strategy.long)
    if HULL[0] < HULL[2] and testPeriod()
        strategy.entry("sell", strategy.short)

`HULL[0] > HULL[2]` / `HULL[0] < HULL[2]` are mutually exclusive, so at most
one entry is placed per bar and there is no else-if to preserve. `testPeriod()`
returns the literal `true`, so both `if`s reduce to the comparison.

The three Hull variants are the source's own functions, translated verbatim:

    HMA(_src, _length)  => wma(2 * wma(_src, _length / 2) - wma(_src, _length),
                               round(sqrt(_length)))
    EHMA(_src, _length) => ema(2 * ema(_src, _length / 2) - ema(_src, _length),
                               round(sqrt(_length)))
    THMA(_src, _length) => wma(wma(_src, _length / 3) * 3
                               - wma(_src, _length / 2) - wma(_src, _length),
                               _length)
    Mode(modeSwitch, src, len) =>
        modeSwitch == "Hma"  ? HMA(src, len) :
        modeSwitch == "Ehma" ? EHMA(src, len) :
        modeSwitch == "Thma" ? THMA(src, len / 2) : na

with `modeSwitch` defaulting to "Hma", so the default path is

    HULL = wma(2*wma(close, 27) - wma(close, 55), 7)

`_length / 2`, `_length / 3` and `len / 2` are INT-ONLY divisions. The source is
`//@version=4` and `length` comes from `input(55, ...)`, i.e. an `int`, so Pine
v4's `/` -- which returns an integer when both operands are integers, discarding
the fractional part -- gives 27, not 27.5. See FIDELITY below: this port used to
carry the repository's round-half-away-from-zero cast (27.5 -> 28), taken from a
`//@version=5` source where `/` genuinely yields a float; the two are different
implementations of the same-looking expression and were not homogenised.

`Mode` is modelled as a lazy selection, i.e. only the branch the input selects
is evaluated. That is a deliberate choice, not an omission: the three branches
write to independent series and share no state, so an untaken branch cannot
change the value `HULL` takes, while evaluating it eagerly could raise on an
input the source itself would accept (length=1 with "Thma" would ask for
`wma(src, 0)`). Whether the original platform evaluates untaken ternary
branches is not something this port verified. The source's own `na` fallback
for an unrecognised `modeSwitch` string is reproduced.

`strategy()` declares `default_qty_type = strategy.percent_of_equity` with
`default_qty_value = 100` (a full-equity position per entry), `pyramiding = 1`,
`commission_type = strategy.commission.percent` with `commission_value = 0`,
`slippage = 0` and `calc_on_order_fills = false`. `initial_capital` is NOT
declared, so Pine's documented default 1000000 USD is recorded.

The source has no `strategy.exit`, no `strategy.close`, no stop and no trailing
exit of any kind: a position is only ever left by the opposite entry, which the
engine models as a reverse (close the old side, open the new one), so
`source_reproduce_stops` is False. With `pyramiding = 1` the engine holds TWO
stacked entries in one direction when the signal repeats. MEASURED on three
synthetic 3000-bar 30m frames (seeds 782/11/42): the engine's open-entry list
holds at most 2 entries of non-zero size on all three, and closes 413 / 325 /
318 trades. On two of the three its raw list length reaches 3 because a reversal
can leave a dust entry (|qty| 9.1e-12 on seed 11, 1.8e-11 on seed 42) that the
engine's own `opening > 1e-12` guard admits; on seed 782 the list is 2 with no
dust. The Freqtrade side structurally cannot stack
(`PinePortBase.position_adjustment_enable` is False, PINE_SEMANTICS.md 2.10), so
the framework ledger can differ from the engine's by one position per direction
-- see the note below.

FIDELITY:

* `_length / 2`, `_length / 3` and `len / 2` are INT / INT divisions and are
  reproduced as such (`_pine_int_div`): the source is `//@version=4`, the length
  comes from `input(55, ...)` and is an `int`, and Pine v4's `/` returns an
  integer when both operands are integers, discarding the fractional part --
  TradingView documents this for v3/v4 ("If both operands are integers, then the
  result will also have the type integer"; the same guide's worked example is
  `bad_fraction = 1 / 2`, which "does not equal 0.5"). Measured at the default
  length 55: half 55/2 -> 27, outer round(sqrt(55)) -> 7, i.e.
  `wma(2*wma(close,27) - wma(close,55), 7)`; EHMA half 27, outer 7; THMA's
  `len/2` -> 27, so `wma(wma(close,9)*3 - wma(close,13) - wma(close,27), 27)`.
  CHANGED during this port's review: the file previously used the repository's
  round-half-away-from-zero cast (`_pine_int`, 27.5 -> 28 -> `wma(...,28)`)
  copied from `SMOptimizedMultiTimeframeHma_64f8cf`. That source is
  `//@version=5` and calls `ta.wma`, so its `_length / 2` really is the float
  27.5 and needs a cast; this source is v4, where the division is already an
  integer. Same-looking formula, different implementation. RESIDUAL RISK: the
  host that produced the source (FMZ, per the md's detail link) is not
  TradingView and whether its interpreter applies v4's integer division is
  unpublished and unverified; the rounding reading would give 55/2 -> 28
  (against 27), and for THMA the middle term 13.75 -> 14 and the outer length
  27.5 -> 28 (against 13 and 27). The two readings select different HMA
  constants and therefore a different signal series -- MEASURED, they differ:
  the rounding reading closes 413 / 386 / 381 engine trades on the three frames
  against 413 / 325 / 318 now.
* `round(sqrt(_length))` is explicit in the source and reproduced as such: Pine's
  round, half away from zero (`_pine_int`), giving 7 at length 55.
* Pyramid risk, MEASURED on three synthetic 3000-bar 30m frames (seeds
  782/11/42) with the v4 integer-division lengths in place: `pyramiding = 1`
  lets the engine hold 2 stacked non-zero entries in one direction (max non-zero
  entry count 2 on all three frames, closing 413 / 325 / 318 trades). This port
  can therefore report `final_bar_position_only` or `mismatch` for a reason that
  is a framework boundary rather than a translation error, and the framework
  cannot stack (`position_adjustment_enable = False`, PINE_SEMANTICS.md 2.10).
* md-vs-source: the md's argument table records the two date defaults as
  `v_input_3 = true` and `v_input_4 = true`; the SOURCE says
  `input(1, "Backtest Start Month")` and `input(1, "Backtest Start Day")`. The
  code is followed (`1`).
* md-vs-source: the md describes the script as "added ability to specify a time
  periods to backtest over". `testPeriod()` is a one-line function returning
  the literal `true` -- the four date inputs are turned into `testPeriodStart`
  / `testPeriodStop`, and neither is read anywhere else in the source. The date
  range therefore has NO effect on trading. Reproduced as written.
* `strat_dir_input` ("Strategy Direction", default "long") is likewise dead:
  the two lines that would consume it (`strategy.risk.allow_entry_in`) are
  commented out in the source, and `strategy.risk.*` is not modelled anyway
  (PINE_SEMANTICS.md 2.3). Recorded as an input, not implemented.
* `switchColor`, `candleCol`, `visualSwitch`, `thicknesSwitch`, `transpSwitch`,
  `MHULL`, `SHULL`, `hullColor`, the two `plot` calls, the `fill` and the
  `barcolor` are display-only: nothing reads them for trading and they place no
  order. They are recorded in `source_defaults` (they are plain scalars) but
  are not otherwise reproduced.
* `ta.ema` is `pine_ta.pine_ema`, seeded with the first non-na observation;
  TradingView's seeding rule is unpublished (PINE_SEMANTICS.md 3.1). This only
  affects the non-default "Ehma" variation.
* The source has no future-data reference and does not repaint: `HULL[2]` is a
  two-bar HISTORY reference, and entries are market orders filling next open.
* The `/*backtest` window (2022-04-24 to 2022-05-23) is the host's extraction
  metadata, not an `input.time` filter, so no data is trimmed; its
  `basePeriod: 15m` is the host's intrabar granularity for filling 30m bars.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_int(value: float) -> int:
    """Pine's `round`: half away from zero, not Python's banker's rounding.

    Used for the source's explicit `round(sqrt(_length))`, which Pine also
    rounds half away from zero.
    """
    return int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)


def _pine_int_div(value: int, divisor: int) -> int:
    """Pine v4's `/` on two integers: the result is an int, the remainder lost.

    `length / 2` in a `//@version=4` script whose length comes from
    `input(55, ...)` is 27, not 27.5 -- TradingView documents the int/int rule
    for v3/v4. This is NOT the same expression as the `//@version=5` HMA
    sources', where `/` always yields a float and a cast is genuinely needed.
    """
    return int(value / divisor)


class SMHullSuite_53585e(PinePortBase, IStrategy):
    source_id = "SM_53585e263bbea19a"
    source_file = "Hull-Suite-Strategy.md"
    # /*backtest ... period: 30m, basePeriod: 15m
    timeframe = "30m"
    # Both directions are entered by the source.
    can_short = True
    source_defaults: dict = {
        "strat_dir_input": "long",
        "testStartYear": 2016,
        "testStartMonth": 1,
        "testStartDay": 1,
        "testStopYear": 2030,
        "testStopMonth": 12,
        "testStopDay": 30,
        "src": "close",
        "modeSwitch": "Hma",
        "length": 55,
        "switchColor": True,
        "candleCol": False,
        "visualSwitch": True,
        "thicknesSwitch": 1,
        "transpSwitch": 40,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 1
    # Not declared by strategy(), so Pine's documented default.
    source_initial_capital = 1_000_000.0
    # No strategy.exit / strategy.close / stop anywhere in the source.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`_length / 2`, `_length / 3` and `len / 2` are INT / INT divisions, "
        "reproduced as such (_pine_int_div). The source is //@version=4, its "
        "length comes from input(55, ...) and is an int, and Pine v4's `/` "
        "returns an integer when both operands are integers (TradingView's "
        "v3/v4 operators page: 'if both operands are integers, then the result "
        "will also have the type integer'; its worked example is `1 / 2`, which "
        "'does not equal 0.5'). Measured at length 55: half 55/2 -> 27, outer "
        "round(sqrt(55)) -> 7, so wma(2*wma(close,27) - wma(close,55), 7); EHMA "
        "half 27, outer 7; THMA len/2 -> 27, so wma(wma(close,9)*3 - "
        "wma(close,13) - wma(close,27), 27). CHANGED during review: the file "
        "previously used the round-half-away-from-zero cast (_pine_int), 27.5 -> "
        "28, copied from SMOptimizedMultiTimeframeHma_64f8cf -- whose source is "
        "//@version=5 and calls ta.wma, so its half really IS the float 27.5 and "
        "needs a cast. Same-looking expression, different implementation. "
        "RESIDUAL RISK: the FMZ host that produced the source is not "
        "TradingView, and whether its interpreter applies v4 integer division "
        "is unpublished; the rounding reading (55/2 -> 28 for the halves, and "
        "for THMA the middle term 13.75 -> 14 and the outer length 27.5 -> 28) "
        "is the alternative and selects a different signal series.",
        "`round(sqrt(_length))` is explicit in the source and reproduced as "
        "such: Pine's round is half away from zero (which _pine_int implements), "
        "giving 7 at length 55.",
        "pyramiding = 1 is the source's declaration. MEASURED on three "
        "synthetic 3000-bar 30m frames (seeds 782/11/42) with the v4 "
        "integer-division lengths: the engine holds at most 2 non-zero same-side "
        "entries at once and closes 413 / 325 / 318 trades. PinePortBase sets "
        "position_adjustment_enable = False, so the Freqtrade side structurally "
        "holds one (PINE_SEMANTICS 2.10). Any engine-vs-framework position "
        "difference here is that boundary, not a translation choice.",
        "The engine's open-entry list length reaches 3 on two of those three "
        "frames (seeds 11 and 42; seed 782 stays at 2). That third record is "
        "dust left when a reverse order's remainder cancels to floating-point "
        "noise -- measured |qty| 9.1e-12 and 1.8e-11 -- and pine_engine.py "
        "admits it because its guard is `opening > 1e-12`. Counting non-zero "
        "entries only, the stack is 2. This is an engine bookkeeping artifact, "
        "not a translation choice, and it never changes a fill price.",
        "md-vs-source: the md's argument table gives v_input_3 / v_input_4 as "
        "`true`; the source says input(1, 'Backtest Start Month') and "
        "input(1, 'Backtest Start Day'). Code followed (1).",
        "md-vs-source: the md says the script adds 'ability to specify a time "
        "periods to backtest over'. testPeriod() returns the literal true, and "
        "testPeriodStart / testPeriodStop are read nowhere else in the source, "
        "so the date inputs cannot affect a trade. Reproduced as written.",
        "strat_dir_input (default 'long') is dead code: the two lines that "
        "would consume it are commented out in the source, and strategy.risk.* "
        "is unmodelled (PINE_SEMANTICS 2.3). Recorded as an input only.",
        "switchColor / candleCol / visualSwitch / thicknesSwitch / "
        "transpSwitch / MHULL / SHULL / hullColor and the plot / fill / "
        "barcolor calls are display-only and place no order; recorded in "
        "source_defaults, otherwise not reproduced.",
        "Mode() is evaluated LAZILY -- only the branch modeSwitch selects is "
        "computed. The three branches write to independent series and share no "
        "state, so an untaken one cannot change HULL; evaluating eagerly could "
        "instead raise on an input the source accepts (length=1 with 'Thma' "
        "asks for wma(src, 0)). Whether the original platform evaluates "
        "untaken ternary branches is unverified.",
        "ta.ema (the 'Ehma' variation only) is pine_ta.pine_ema, seeded with "
        "the first non-na observation; TradingView's seeding rule is "
        "unpublished (PINE_SEMANTICS 3.1).",
        "No exit call exists: a position is only left by the opposite entry, "
        "which the engine models as a reverse, so source_reproduce_stops is "
        "False and a position open at the window end stays open.",
        "No future-data reference and no repainting: HULL[2] is a two-bar "
        "history reference and the entries are market orders filling next "
        "open.",
        "The /*backtest window (2022-04-24 to 2022-05-23) is extraction "
        "metadata, not an input.time filter, so no data is trimmed.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    # ---- Hull family -------------------------------------------------------
    @staticmethod
    def _hma(source: pd.Series, length: int) -> pd.Series:
        # wma(2 * wma(_src, _length / 2) - wma(_src, _length),
        #     round(sqrt(_length)))
        inner = 2.0 * ta.pine_wma(source, _pine_int_div(length, 2)) - ta.pine_wma(
            source, int(length)
        )
        return ta.pine_wma(inner, _pine_int(math.sqrt(float(length))))

    @staticmethod
    def _ehma(source: pd.Series, length: int) -> pd.Series:
        # ema(2 * ema(_src, _length / 2) - ema(_src, _length),
        #     round(sqrt(_length)))
        inner = 2.0 * ta.pine_ema(source, _pine_int_div(length, 2)) - ta.pine_ema(
            source, int(length)
        )
        return ta.pine_ema(inner, _pine_int(math.sqrt(float(length))))

    @staticmethod
    def _thma(source: pd.Series, length: int) -> pd.Series:
        # wma(wma(_src, _length / 3) * 3 - wma(_src, _length / 2)
        #     - wma(_src, _length), _length)
        inner = (
            ta.pine_wma(source, _pine_int_div(length, 3)) * 3.0
            - ta.pine_wma(source, _pine_int_div(length, 2))
            - ta.pine_wma(source, int(length))
        )
        return ta.pine_wma(inner, int(length))

    def _mode(self, mode_switch: str, source: pd.Series, length: int) -> pd.Series:
        # Mode(modeSwitch, src, len) => ... : na
        if mode_switch == "Hma":
            return self._hma(source, int(length))
        if mode_switch == "Ehma":
            return self._ehma(source, int(length))
        if mode_switch == "Thma":
            return self._thma(source, _pine_int_div(int(length), 2))
        return pd.Series(np.nan, index=source.index, dtype=float)

    def pine_indicators(self, dataframe, params):
        # src = input(close, title="Source")
        source = ta.pine_source(dataframe, str(params["src"]))
        # HULL = Mode(modeSwitch, src, length)
        hull = self._mode(
            str(params["modeSwitch"]), source, params["length"]
        )
        dataframe["pine_hull"] = hull
        # MHULL = HULL[0]  (display-only, kept as a column for traceability)
        dataframe["pine_mhull"] = hull
        # SHULL = HULL[2]
        dataframe["pine_shull"] = hull.shift(2)
        # hullColor = switchColor ? (HULL > HULL[2] ? #00ff00 : #ff0000) :
        #     #ff9800 -- display-only.
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        hull = dataframe["pine_hull"]
        shull = dataframe["pine_shull"]
        # na comparisons are false, so the first two bars enter nothing.
        return {
            "long_signal": (hull > shull).fillna(False).to_numpy(dtype=bool),
            "short_signal": (hull < shull).fillna(False).to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # testPeriod() => true, and it is called in both conditions.
        # if HULL[0] > HULL[2] and testPeriod()
        #     strategy.entry("buy", strategy.long)
        if ctx["long_signal"][i]:
            broker.entry("buy", "long")
        # if HULL[0] < HULL[2] and testPeriod()
        #     strategy.entry("sell", strategy.short)
        if ctx["short_signal"][i]:
            broker.entry("sell", "short")
