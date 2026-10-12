"""Port of sources/SM_b86cf0a4488865e3.pine (batch_001/ATR-Smoothed.md).

Pine v3 (`//@version=3`, `study(...)`), 2h. dysrupt's ATR trailing stop, modified
by @guikroth and then by the fmz.com uploader ("ATR Smoothed ... _BuySell
version"). The file declares an INDICATOR, not a strategy, and a conversion tool
has appended an order block at the end (PINE_SEMANTICS.md 1.17):

    if LONG
        strategy.entry("Enter Long", strategy.long)
    else if SHORT
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside a `study()`, so the "original strategy" IS
the indicator plus that appended block, and its trading behaviour is "enter when
the signal fires, and NEVER exit". There is no `strategy.close`, no
`strategy.exit`, not even a commented-out exit line, so `source_reproduce_stops`
is False: the ATR trailing stop here is a PLOT, not an exit order. A position is
only ended by the opposite entry reversing it.

The indicator, transcribed:

    xATR = atr(21)                                   // = rma(tr(true), 21)
    nLoss = 6.3 * xATR
    xATRTrailingStop = na
    xATRTrailingStop :=
        iff(close > nz(xATRTrailingStop[1], 0) and close[1] > nz(xATRTrailingStop[1], 0),
              max(nz(xATRTrailingStop[1]), close - nLoss),
        iff(close < nz(xATRTrailingStop[1], 0) and close[1] < nz(xATRTrailingStop[1], 0),
              min(nz(xATRTrailingStop[1]), close + nLoss),
        iff(close > nz(xATRTrailingStop[1], 0), close - nLoss, close + nLoss)))

    pos = na
    pos :=
        iff(close[1] < nz(xATRTrailingStop[1], 0) and close > nz(xATRTrailingStop[1], 0), 1,
        iff(close[1] > nz(xATRTrailingStop[1], 0) and close < nz(xATRTrailingStop[1], 0), -1,
            nz(pos[1], 0)))

    isLong = false
    isLong := nz(isLong[1], false)          // carries the previous bar's flag
    isShort = false
    isShort := nz(isShort[1], false)
    LONG = not isLong and pos == 1
    SHORT = not isShort and pos == -1
    if (LONG)
        isLong := true
        isShort := false
    if (SHORT)
        isLong := false
        isShort := true

The trailing stop (a ratchet) and `pos` (a state machine) are both walked bar by
bar: each bar reads the value the previous bar assigned, which is what
`xATRTrailingStop[1]` / `pos[1]` mean, and `nz(..., 0)` collapses the first bar's
na to 0.

THE `isLong` / `isShort` FLAGS ARE LOAD-BEARING, NOT DECORATION. They are carried
across bars and flipped by the two `if` blocks, so `LONG` is true only on the bar
`pos` FLIPS to +1 and `SHORT` only on the bar it flips to -1. They are written
BEFORE `LONG`/`SHORT` are computed, so the test uses the previous bar's state.
Dropping them and testing `pos == 1` alone would re-enter on every bar of a trend
instead of once per flip.

`pos` IS AN INTEGER AND KEEPS ITS -1: the source compares it explicitly
(`pos == 1`, `pos == -1`) and the port does the same on an int array, so the
PINE_SEMANTICS.md 1.17 trap -- rewriting a bare `-1` condition into `== 1` or
`> 0`, which silently kills every short -- cannot arise here. The value is never
bool()-ised: 0 means "no fresh cross", -1 means a downward cross.

`strategy()` is never declared, so every strategy property is Pine's documented
default: `fixed` sizing of 1 contract, initial capital 1000000, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false`.

FIDELITY -- translation choices and source/md mismatches:

1. MD/SOURCE MISMATCH: the md's detail link (fmz.com/strategy/365078) and the
   "Orignal Version By dysrupt / Modifyed by me" line describe an ATR trailing
   stop, but the source's own exit is only a PLOT -- the commented-out
   `//patr=plot(xATRTrailingStop, ...)` and the live `plot(avg1, ...)`. Nothing
   in the file calls `strategy.exit`, so no stop is reproduced as an order and
   `source_reproduce_stops` is False. The md gives no exit rules either.
2. MD/SOURCE MISMATCH: the md's argument table lists four inputs (Period 21,
   Multiplier 6.3, Smooth 100, Source close) exactly as the source declares
   them; no numeric default differs. The table does not mention that `Smooth`
   and `Source` feed only the display-only `vwma`/`plot`.
3. MD/SOURCE MISMATCH: the md has no description of the entry logic at all --
   not the trailing stop's ratchet, not the `pos` state machine, not the
   `isLong`/`isShort` flip guard, and not the appended order block. The block is
   therefore read from the source alone.
4. `atr(21)` is Pine's `rma(tr(true), 21)`: the true range with
   `handle_na = true`, so bar 0 contributes `high - low` rather than na, and the
   rma is seeded with the SMA of the first 21 true ranges. `pine_ta.pine_atr` is
   exactly that (PINE_SEMANTICS.md 3.7 concerns the bare `ta.tr`, not `ta.atr`,
   which is why this port is not affected by it).
5. `nz(xATRTrailingStop[1], 0)` is 0 on the first bar (and on any bar whose
   predecessor was undefined), so the two `>` / `<` comparisons there are against
   0 -- reproduced literally rather than special-cased, which also means the
   first `max(nz(prev), close - nLoss)` can legitimately take the 0 floor.
6. Pine's `iff(c, a, b)` with an na condition takes the `b` arm, and `max` / `min`
   with an na argument return na. The port reproduces both: while `nLoss` is na
   (the ATR warm-up) the trailing stop stays na, and the na comparisons are false
   so the third `iff` arm is the one taken.
7. In v3 the flag declarations `isLong = false` followed by
   `isLong := nz(isLong[1], false)` carry the previous bar's value forward; the
   port keeps a two-variable state machine with that same order (carry, then
   test, then the two flips), and keeps the source's independent `if (LONG)` /
   `if (SHORT)` pair rather than merging them into if/else.
8. `vwma(src, len2)`, `avg1 = avg(out, xATRTrailingStop)`, `plot(avg1, ...)`,
   `barcolor`, `plotshape`, `color` and the three duplicated `alertcondition`
   lines are display-only and are not reproduced; the plotted ATR line is not an
   order either (see note 1).
9. `len2` (Smooth, 100) and `src` (Source, close) are declared inputs that feed
   ONLY the display-only `vwma`/`avg1` plot. They are carried in
   `source_defaults` for provenance and enter no calculation the port performs.
10. No `request.security()`, no `barstate.isrealtime` branch, no repainting.
11. The `/*backtest` header declares `period: 2h` on Futures_Binance BTC_USDT,
    hence `timeframe = "2h"`; its `basePeriod: 15m` is the FMZ backtester's own
    intrabar fill granularity, not the strategy's period.
12. Leverage, margin, liquidation, funding and the venue's contract-step rounding
    of order quantities are not modelled (PINE_SEMANTICS.md section 2).
"""
import numpy as np

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAtrSmoothed_b86cf0(PinePortBase, IStrategy):
    source_id = "SM_b86cf0a4488865e3"
    source_file = "ATR-Smoothed.md"
    timeframe = "2h"
    # The appended block has both arms: entry("Enter Long") and
    # entry("Enter Short").
    can_short = True
    source_defaults: dict = {
        # nATRPeriod = input(21, "Period")
        "nATRPeriod": 21,
        # nATRMultip = input(6.3, "Multiplier", type=float, minval=0.5, maxval=1000, step=0.1)
        "nATRMultip": 6.3,
        # len2 = input(100, minval=1, title="Smooth")  -- display-only
        "len2": 100,
        # src = input(close, title="Source")           -- display-only
        "src": "close",
    }
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: `fixed` / 1 contract, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The trailing stop exists only as a PLOT: no strategy.exit / strategy.close
    # anywhere in the file, so there is no stop leg to reproduce as an order.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source is a Pine v3 study(): the trailing "
        "`if LONG / else if SHORT` order pair is the conversion tool's appended "
        "block (PINE_SEMANTICS.md 1.17). `strategy.entry` cannot compile inside "
        "study(), so the original strategy IS the indicator plus that block.",
        "THE ATR TRAILING STOP IS A PLOT, NOT AN EXIT ORDER. The file has no "
        "strategy.exit / strategy.close, and the trailing-stop line is drawn "
        "with plot() (its sibling plot is even commented out). "
        "source_reproduce_stops is therefore False -- reproducing the trail as "
        "a framework stop would invent an exit the source never places.",
        "NO EXIT CALL EXISTS at all, so a position is only ended by the opposite "
        "entry reversing it, and one still open at the end of the window stays "
        "open.",
        "pos is an INTEGER and keeps its -1: the source compares it explicitly "
        "(pos == 1 / pos == -1). The port does the same on an int array and "
        "never bool()-ises it, so the PINE_SEMANTICS.md 1.17 trap (rewriting a "
        "bare -1 into == 1 / > 0 and silently killing every short) cannot arise; "
        "0 means 'no fresh cross', not 'false short'.",
        "The isLong / isShort flags are load-bearing: carried across bars and "
        "flipped by the source's two `if` blocks, they make LONG true only on "
        "the bar pos FLIPS to +1 (and SHORT only on the flip to -1). Testing "
        "pos == 1 alone would re-enter on every bar of a trend.",
        "In v3 `isLong = false` followed by `isLong := nz(isLong[1], false)` "
        "carries the previous bar's value; the port keeps that carry-then-test-"
        "then-flip order, and keeps the source's two INDEPENDENT if blocks "
        "rather than merging them into if/else.",
        "nz(xATRTrailingStop[1], 0) collapses the first bar's (and any "
        "preceding bar's) na to 0, so the > / < comparisons there are against "
        "0. Reproduced literally, which also means the first "
        "max(nz(prev), close - nLoss) can legitimately take the 0 floor.",
        "Pine's iff(c, a, b) takes the b arm when c is na, and max/min with an "
        "na argument return na; while nLoss is na (the ATR warm-up, first 20 "
        "bars) the trailing stop stays na and the na comparisons are false, so "
        "the third iff arm is taken.",
        "atr(21) is rma(tr(true), 21): bar 0 contributes high - low, not na, "
        "and the rma is seeded with the SMA of the first 21 true ranges -- "
        "pine_ta.pine_atr is exactly that. PINE_SEMANTICS.md 3.7 applies to the "
        "bare ta.tr, not to ta.atr, so this port is not exposed to it.",
        "vwma(src, len2), avg1 = avg(out, xATRTrailingStop), plot(), barcolor, "
        "plotshape, color and the three duplicated alertcondition lines are "
        "display-only and are not reproduced.",
        "len2 / src feed ONLY the display-only vwma plot; they are carried in "
        "source_defaults for provenance and enter no calculation the port uses.",
        "MD/SOURCE MISMATCH: the md describes the file as an ATR trailing stop "
        "but documents no exit rule and no entry logic -- it omits the ratchet, "
        "the pos state machine and the isLong/isShort flip guard. Read from the "
        "source alone.",
        "MD/SOURCE MISMATCH: the md's argument table matches the source's four "
        "input defaults (21 / 6.3 / 100 / close) but does not note that Smooth "
        "and Source feed only a display-only plot.",
        "No `? -1 : 0` bare-condition construct exists (the -1 is always "
        "compared explicitly), and no `input(type=bool)` is used numerically, "
        "so neither PINE_SEMANTICS.md 1.17 nor 1.16 applies.",
        "/*backtest declares period: 2h on Futures_Binance BTC_USDT; "
        "basePeriod: 15m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No security() call, no barstate.isrealtime branch, no repainting.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        period = int(params["nATRPeriod"])
        multiple = float(params["nATRMultip"])

        close = dataframe["close"].to_numpy(dtype=float)
        size = len(dataframe)

        # xATR = atr(nATRPeriod)  ->  rma(tr(true), nATRPeriod)
        atr = ta.pine_atr(dataframe, period).to_numpy(dtype=float)
        # nLoss = nATRMultip * xATR
        n_loss = multiple * atr

        # xATRTrailingStop: a two-sided ratchet. Each bar reads the value the
        # previous bar assigned (`xATRTrailingStop[1]`), so it is walked.
        trailing = np.full(size, np.nan, dtype=float)
        for t in range(size):
            previous = trailing[t - 1] if t >= 1 else np.nan
            # nz(xATRTrailingStop[1], 0)
            reference = previous if np.isfinite(previous) else 0.0
            price = close[t]
            previous_close = close[t - 1] if t >= 1 else np.nan
            loss = n_loss[t]
            # `close > nz(prev, 0)` etc. -- an na comparison is false in Pine.
            above = price > reference
            above_previous = previous_close > reference
            below = price < reference
            below_previous = previous_close < reference
            if above and above_previous:
                # max(nz(prev), close - nLoss): max with an na argument is na.
                trailing[t] = max(reference, price - loss) if np.isfinite(loss) else np.nan
            elif below and below_previous:
                # min(nz(prev), close + nLoss)
                trailing[t] = min(reference, price + loss) if np.isfinite(loss) else np.nan
            else:
                # iff(close > nz(prev, 0), close - nLoss, close + nLoss)
                trailing[t] = price - loss if above else price + loss

        # pos := iff(close[1] < nz(prev_stop, 0) and close > nz(prev_stop, 0), 1,
        #         iff(close[1] > nz(prev_stop, 0) and close < nz(prev_stop, 0), -1,
        #             nz(pos[1], 0)))
        # Integers are kept as integers: 1 / -1 / 0, NOT booleans.
        pos = np.zeros(size, dtype=np.int64)
        for t in range(size):
            previous = trailing[t - 1] if t >= 1 else np.nan
            reference = previous if np.isfinite(previous) else 0.0
            price = close[t]
            previous_close = close[t - 1] if t >= 1 else np.nan
            if previous_close < reference and price > reference:
                pos[t] = 1
            elif previous_close > reference and price < reference:
                pos[t] = -1
            else:
                # nz(pos[1], 0)
                pos[t] = pos[t - 1] if t >= 1 else 0

        # isLong / isShort: carried across bars, then tested, then flipped by the
        # source's two `if` blocks.
        long_flags = np.zeros(size, dtype=bool)
        short_flags = np.zeros(size, dtype=bool)
        carry_long = False
        carry_short = False
        for t in range(size):
            # isLong := nz(isLong[1], false) ; isShort := nz(isShort[1], false)
            is_long = carry_long
            is_short = carry_short
            # LONG = not isLong and pos == 1 ; SHORT = not isShort and pos == -1
            is_long_condition = (not is_long) and bool(pos[t] == 1)
            is_short_condition = (not is_short) and bool(pos[t] == -1)
            long_flags[t] = is_long_condition
            short_flags[t] = is_short_condition
            # if (LONG) isLong := true, isShort := false
            if is_long_condition:
                carry_long, carry_short = True, False
            # if (SHORT) isLong := false, isShort := true
            if is_short_condition:
                carry_long, carry_short = False, True

        dataframe["pine_atr_trailing_stop"] = trailing
        dataframe["pine_pos"] = pos
        dataframe["pine_long_condition"] = long_flags
        dataframe["pine_short_condition"] = short_flags
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "position_state": dataframe["pine_pos"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(dtype=bool),
            "short_condition": dataframe["pine_short_condition"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if LONG
        #     strategy.entry("Enter Long", strategy.long)
        # else if SHORT
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
