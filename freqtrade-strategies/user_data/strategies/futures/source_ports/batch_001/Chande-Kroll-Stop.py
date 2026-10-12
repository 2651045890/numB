"""Port of sources/SM_fb38d1b5b4edeea3.pine (batch_001/Chande-Kroll-Stop.md).

ChaoZhang's strategy version of the Chande Kroll Stop, gated by an ADX filter.

Bands (p = ATR lookback and stop width period, x = ATR multiple, q = the
lookback that produces the final trailing stop):

    first_high_stop = ta.highest(high, p) - x * ta.atr(p)
    first_low_stop  = ta.lowest(low,  p) + x * ta.atr(p)
    stop_short      = ta.highest(first_high_stop, q)
    stop_long       = ta.lowest(first_low_stop,   q)

ADX filter, transcribed from the source's own `dirmov` / `adx` functions:

    up      = ta.change(high)
    down    = -ta.change(low)
    plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
    minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
    truerange = ta.rma(ta.tr, dilen)
    plus  = fixnan(100 * ta.rma(plusDM,  dilen) / truerange)
    minus = fixnan(100 * ta.rma(minusDM, dilen) / truerange)
    sum   = plus + minus
    sig   = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)

Orders, in the source's order:

    if ta.crossunder(close, stop_long)  and sig > ADX_sig -> entry("long",  long)
    if ta.crossover(close,  stop_short) and sig > ADX_sig -> entry("short", short)

The entry sides are counter-intuitive but are what the source says: the LONG is
triggered by the close crossing UNDER the lower band, and the SHORT by the close
crossing ABOVE the upper band. The md's prose describes the opposite mapping
(short on a cross under the orange line, long on a cross of the blue line); the
source code is the authority and the port follows it -- see FIDELITY.

`strategy()` declares only title / overlay, so every order property is Pine's
default: fixed quantity of 1 contract, 0% commission, pyramiding 0, initial
capital 1000000. There is no exit call, so a position goes flat only when the
opposite entry reverses it: `source_reproduce_stops` is False and a position
open at the end of the window stays open.

FIDELITY:

* The source carries no `/*backtest` header at all, so it declares no period;
  the port uses the repository's mandated 1h fallback for headerless sources
  (compare batch_001/Exit-from-specific-entries.py). The bars are therefore
  hourly even though the strategy may have been authored for another period.
* md vs source: the md's Strategy Description says "Short signal is when the
  close crosses under the orange line and a long signal is generated upon a
  crossover of a close candle of the blue line", which is the REVERSE of the
  source's `crossunder(close, stop_long) -> long` / `crossover(close,
  stop_short) -> short`. Source wins (rule 2); the prose is recorded, not
  followed.
* md vs source: the md's argument table renders the `x` default as `true`
  (`v_input_int_2|true|x`), the exporter's rendering of the integer 1; the
  source reads `input.int(1, minval=1)` and the port uses 1.
* `fixnan()` is not part of `pine_ta`; it is Pine's "replace na with the latest
  non-na value" and is reproduced here as a forward fill.
* Division by zero: the source guards exactly one of the three divisions
  (`sum == 0 ? 1 : sum`) and leaves the two `100 * ta.rma(...) / truerange`
  divisions unguarded, then wraps both of those in `fixnan`. The port reads
  that as "the result is na when the denominator is zero, and fixnan carries
  the previous value" -- which is what makes the fixnan meaningful. Pine's
  exact float-division-by-zero result is not published, so this is a modelling
  choice; it is only reachable on a window whose true range is exactly zero.
* `truerange = ta.rma(ta.tr, dilen)` calls ta.tr WITHOUT handle_na, so Pine
  returns na on bar 0 while `pine_ta.pine_tr` returns high-low there
  (PINE_SEMANTICS.md 3.7). `ta.atr(p)` is Pine's `ta.rma(ta.tr(true), p)`,
  which is `pine_ta.pine_atr` and does handle the first bar. The one-bar
  seeding difference in the DI/ADX chain is a public-layer boundary, recorded
  and not modified.
* `math.abs` is `pine_ta.pine_abs`; `ta.change`, `ta.rma`, `ta.highest`,
  `ta.lowest`, `ta.crossover` and `ta.crossunder` are the `pine_ta` functions
  of the same names.
* The two `plot` calls are display-only and are not reproduced.
* Leverage, margin, liquidation and funding are not modelled, and neither is
  the venue's contract-step rounding -- the chain verifier measures that
  separately rather than treating it as a signal difference.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _fixnan(series: pd.Series) -> pd.Series:
    """Pine `fixnan(source)`: replace na with the latest non-na value."""
    return series.ffill()


def _guarded_ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    """`numerator / denominator` with a zero denominator left undefined (na).

    The source leaves these two divisions unguarded and wraps the result in
    `fixnan`, which only has a purpose if a zero denominator yields na. Pine's
    published result for a float division by zero is not specified, so this is
    a modelling choice rather than a transcription -- see FIDELITY.
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = numerator / denominator
    return ratio.where(denominator != 0.0)


class SMChandeKrollStop_fb38d1(PinePortBase, IStrategy):
    source_id = "SM_fb38d1b5b4edeea3"
    source_file = "Chande-Kroll-Stop.md"
    # The source has no /*backtest header, so it declares no period; the
    # repository's fallback for headerless sources is 1h.
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {
        "p": 10,
        "x": 1,
        "q": 9,
        "adxlen": 14,
        "dilen": 14,
        "ADX_sig": 20,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source carries no /*backtest header, so it declares no period; the "
        "port uses the repository's mandated 1h fallback for headerless "
        "sources, so the bars verified are hourly even though the strategy may "
        "have been authored for another timeframe. The manifest's period for "
        "this source is null.",
        "md vs source: the md's prose maps the signals the other way round "
        "(short on a cross under the orange line, long on a cross of the blue "
        "line) while the source is `crossunder(close, stop_long) -> long` and "
        "`crossover(close, stop_short) -> short`. The source is reproduced; "
        "the prose is recorded but not followed (rule 2).",
        "md vs source: the md's argument table renders the x default as `true` "
        "(v_input_int_2|true|x), the exporter's rendering of the integer 1; the "
        "source reads input.int(1, minval=1) and the port uses 1.",
        "fixnan() is not in pine_ta; reproduced as a forward fill of the last "
        "non-na value.",
        "Division by zero: only the ADX division is guarded by the source "
        "(`sum == 0 ? 1 : sum`); the two `100 * ta.rma(...) / truerange` "
        "divisions are unguarded and wrapped in fixnan, which the port reads as "
        "'na on a zero denominator, then carried forward'. Pine's float "
        "division-by-zero result is not published, so this is a modelling "
        "choice, reachable only on an exactly-zero true range window.",
        "truerange uses ta.tr WITHOUT handle_na, so Pine returns na on bar 0 "
        "where pine_ta.pine_tr returns high-low (PINE_SEMANTICS.md 3.7); this "
        "shifts the DI/ADX warmup by one bar. ta.atr(p) is Pine's "
        "ta.rma(ta.tr(true), p) and is pine_ta.pine_atr. Public-layer "
        "boundary, recorded not modified.",
        "strategy() declares only title/overlay, so qty_type=fixed, qty_value=1, "
        "commission=0%, pyramiding=0 and initial_capital=1000000 are Pine's "
        "documented defaults.",
        "There is no exit call: a position is closed only by the opposite "
        "entry reversing it, so source_reproduce_stops is False and a position "
        "open at the end of the window stays open.",
        "The two plot() calls are display-only and are not reproduced.",
    ]

    def pine_indicators(self, dataframe, params):
        p = int(params["p"])
        x = float(params["x"])
        q = int(params["q"])
        adxlen = int(params["adxlen"])
        dilen = int(params["dilen"])
        adx_sig = float(params["ADX_sig"])

        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]

        # first_high_stop = ta.highest(high, p) - x * ta.atr(p)
        # first_low_stop  = ta.lowest(low,  p) + x * ta.atr(p)
        atr_p = ta.pine_atr(dataframe, p)
        first_high_stop = ta.pine_highest(high, p) - x * atr_p
        first_low_stop = ta.pine_lowest(low, p) + x * atr_p
        # stop_short = ta.highest(first_high_stop, q)
        # stop_long  = ta.lowest(first_low_stop,   q)
        stop_short = ta.pine_highest(first_high_stop, q)
        stop_long = ta.pine_lowest(first_low_stop, q)

        # ---- dirmov(dilen) ---------------------------------------------------
        up = ta.pine_change(high)
        down = -ta.pine_change(low)
        # plusDM  = na(up)   ? na : (up   > down and up   > 0 ? up   : 0)
        # Each guard names only its OWN series, as the source does: Pine's
        # `and` short-circuits an na operand to false, so a hypothetical bar
        # with `up` defined and `down` na would yield 0, not na. (On a
        # gap-free frame both change() calls are na together anyway.)
        plus_dm = pd.Series(
            np.where(
                up.isna(),
                np.nan,
                np.where((up > down) & (up > 0.0), up, 0.0),
            ),
            index=dataframe.index,
            dtype=float,
        )
        # minusDM = na(down) ? na : (down > up   and down > 0 ? down : 0)
        minus_dm = pd.Series(
            np.where(
                down.isna(),
                np.nan,
                np.where((down > up) & (down > 0.0), down, 0.0),
            ),
            index=dataframe.index,
            dtype=float,
        )
        truerange = ta.pine_rma(ta.pine_tr(dataframe), dilen)
        # plus  = fixnan(100 * ta.rma(plusDM,  dilen) / truerange)
        # minus = fixnan(100 * ta.rma(minusDM, dilen) / truerange)
        plus = _fixnan(_guarded_ratio(100.0 * ta.pine_rma(plus_dm, dilen), truerange))
        minus = _fixnan(_guarded_ratio(100.0 * ta.pine_rma(minus_dm, dilen), truerange))

        # ---- adx(dilen, adxlen) ---------------------------------------------
        total = plus + minus
        denominator = pd.Series(
            np.where(total == 0.0, 1.0, total.to_numpy(dtype=float)),
            index=dataframe.index,
            dtype=float,
        )
        sig = 100.0 * ta.pine_rma(ta.pine_abs(plus - minus) / denominator, adxlen)

        dataframe["pine_stop_long"] = stop_long
        dataframe["pine_stop_short"] = stop_short
        dataframe["pine_adx"] = sig
        dataframe["pine_long_condition"] = (
            ta.pine_crossunder(close, stop_long) & (sig > adx_sig)
        )
        dataframe["pine_short_condition"] = (
            ta.pine_crossover(close, stop_short) & (sig > adx_sig)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "stop_long": dataframe["pine_stop_long"].to_numpy(),
            "stop_short": dataframe["pine_stop_short"].to_numpy(),
            "adx": dataframe["pine_adx"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if ta.crossunder(close, stop_long) and sig>ADX_sig
        #     strategy.entry("long", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("long", "long")
        # if ta.crossover(close, stop_short) and sig>ADX_sig
        #     strategy.entry("short", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("short", "short")
