"""Port of sources/SM_0deaa05ebdfcd54b.pine
(batch_001/Bollinger带震荡型突破策略Bollinger-Bands-Oscillation-Breakthrough-Strategy.md).

Pine v4, long only, 1-minute. Bollinger basis cross filtered by the Aroon Up
line, with a market close:

    basis = sma(src, lengthBB)
    dev   = mult * stdev(src, lengthBB)          # population stdev (ddof=0)
    upper = basis + dev
    lower = basis - dev                          # computed, never read

    AroonUP   = 100 * (highestbars(high, lengthAr + 1) + lengthAr) / lengthAr
    AroonDown = 100 * (lowestbars(low,  lengthAr + 1) + lengthAr) / lengthAr

    Bullish = crossunder(close, basis)
    Bearish = crossunder(close, upper)

    strategy.entry(id="long", long=true,
                   when = Bullish and AroonUP > Confirmation and window())
    strategy.close("long", when = Bearish or AroonUP < Stop and window())

ONE ORDER PER SIDE, nothing more: one long entry and one market close of that
same entry id. There is no short entry, no stop, no limit and no trail, so
`can_short` is False and `source_reproduce_stops` is False.

`timeframe` is "1m" from the `/*backtest` header (`period: 1m`); its
`basePeriod: 1m` is the FMZ backtester's own fill granularity.

`strategy()` IS COMMENTED OUT. The only strategy declaration in the file is
line 13, `// strategy(shorttitle='Bollinger bands And Aroon Scalping', ...,
initial_capital = 1000, process_orders_on_close=true, default_qty_type =
strategy.percent_of_equity, default_qty_value = 30, commission_type=...percent,
commission_value=0.1)`, and it is inert -- a commented line places no
declaration, exactly as a commented-out `strategy.exit` places no exit
(PINE_SEMANTICS.md 1.17). The port therefore runs on Pine's documented defaults
-- `strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
`pyramiding = 0`, `process_orders_on_close = false` -- and NOT on the commented
values. The commented line is recorded in source_fidelity_notes because it is
the author's stated configuration and because its `process_orders_on_close=true`
would, if it were live, move every fill from the next bar's open to the signal
bar's own close, which this engine does not model at all.

The source is NOT a converter-appended order block either: both of its order
calls (the entry at line 54 and the close at line 58) are the author's own
active code, and the file declares no indicator() or study(). Its tier_reason's
"declares indicator()/study(), tool appended strategy.entry pair; NO exits" is
false on both counts, and the port follows the source.

`offset` is declared as an input (default 0) and never applied to `basis`,
`upper` or `lower`; `lower` and `AroonDown` are computed and never read by any
condition. Every one of them is reproduced (dead code kept, not deleted) and
kept as a ledger column.

FIDELITY -- translation choices and source/md mismatches:

1. `window()` IS IN BOTH CONDITIONS and is reproduced as a real comparison
   against the six date inputs. Unlike the usual 2016..2112 window it is
   MEANINGFUL here: it opens 2020-01-01 00:00 and closes 2112-01-01 23:59, so
   every bar of synthetic/test data that starts before 2020 is outside it and the
   entry can never fire there. That is the source's behaviour, not a defect of
   the port; see source_fidelity_notes.
2. `highestbars` / `lowestbars` are not in pine_ta and are implemented here from
   the Pine definition: the offset, as a NEGATIVE number, to the extreme value
   inside the last `length` bars (0 = this bar, -length+1 = the oldest one in the
   window). They are na until the window is full. Ties resolve to the MOST
   RECENT occurrence, which is what Pine's own reference implementation (scan
   from the current bar backwards, stop at the first match) yields; TradingView
   does not document the tie-break, so this is recorded as a parity risk.
3. Operator precedence in the close: Pine binds `and` tighter than `or`, so the
   condition is `Bearish or (AroonUP < Stop and window())`. The `and window()`
   does NOT gate `Bearish`.
4. MD/SOURCE MISMATCH (exit): the md's prose says the position is closed when
   the Aroon Down line signals a downtrend. The source never tests AroonDown at
   all -- the exit is `AroonUP < Stop` (Aroon Stop = 70), i.e. the Aroon UP line
   falling below its stop level. The source is followed; AroonDown is still
   computed, because the source computes it.
5. MD/SOURCE MISMATCH (entry/exit trigger): the md describes both signals as
   "breakouts" (突破) of the middle band. The entry is `crossunder(close, basis)`
   -- a downward cross of the basis, not an upward breakout -- and the exit is
   `crossunder(close, upper)`, a downward cross of the UPPER band. The source is
   followed.
6. MD/SOURCE MISMATCH (stop loss / take profit): the md says a stop loss and the
   Aroon Down line control downside risk, and that the strategy sets stop-loss AND
   take-profit conditions. There is no stop order and no take-profit in the
   source and no AroonDown test; the only exit in the code is the Aroon Up level
   test.
7. MD/SOURCE MISMATCH (short side): the md says "a downward breakthrough of the
   middle band from the upper band signals short entry". The source has NO short
   entry, no short branch and no `strategy.entry(..., strategy.short)` at all --
   it is long only. The source is followed; this is why `can_short` is False.
8. MD/SOURCE MISMATCH (position sizing): the md says partial position sizing
   limits per-trade loss. Sizing comes from the (commented) strategy()
   declaration; with that line inert, Pine's default is a single contract.
9. `stdev` is Pine's population standard deviation (`biased = true`, ddof 0),
   which is what pine_ta.pine_stdev computes; `mult` is applied to it, then
   added to the basis.
10. `src` is `input(close)`, i.e. Pine's source selector on its default, `close`.
11. All six date inputs are integers in the md's table rendered as `true`
    (FMZ's bool column showing the integer 1); the source's real defaults are
    declared here.
12. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled.
"""
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# A year of 1m bars is ~525k rows and this source's Aroon window is 289 bars, so
# the sliding window is materialised in chunks of a couple of million cells
# instead of all 152M at once.
_WINDOW_CELLS = 2_000_000


def _extreme_offset(values, length, highest: bool) -> np.ndarray:
    """Pine `highestbars` / `lowestbars`: offset (<= 0) to the window extreme.

    Pine returns the offset as a negative number -- 0 for the current bar,
    -(length-1) for the oldest bar in the window -- and na until `length` bars
    have elapsed or when the window holds an na. Ties resolve to the MOST RECENT
    occurrence: Pine's reference implementation walks from the current bar
    backwards and stops at the first match, and TradingView does not document
    the tie-break, so this is recorded as an equivalence risk rather than a
    certified rule.
    """
    values = np.asarray(values, dtype=float)
    length = int(length)
    out = np.full(values.shape[0], np.nan)
    if length < 1 or values.shape[0] < length:
        return out
    usable = values.shape[0] - length + 1
    chunk = max(1, _WINDOW_CELLS // length)
    for start in range(0, usable, chunk):
        stop = min(start + chunk, usable)
        windows = sliding_window_view(values[start : stop + length - 1], length)
        finite = ~np.isnan(windows)
        complete = finite.all(axis=1)
        filled = np.where(finite, windows, -np.inf if highest else np.inf)
        extreme = filled.max(axis=1) if highest else filled.min(axis=1)
        equal = (windows == extreme[:, None]) & complete[:, None]
        # Reversing makes argmax return the SMALLEST reversed index `r`, i.e. the
        # newest matching bar; the Pine offset is `j - (length - 1)` for a
        # forward in-window index `j`, and `j = length - 1 - r`, so the offset is
        # simply `-r`.
        block = -np.argmax(equal[:, ::-1], axis=1).astype(float)
        block[~complete] = np.nan
        # The window opening at row `start` ENDS at row `start + length - 1`, so
        # its results belong at those rows, not at `start`.
        out[start + length - 1 : stop + length - 1] = block
    return out


class SMBollingerBandsOscillationBreakthrough_0deaa0(PinePortBase, IStrategy):
    source_id = "SM_0deaa05ebdfcd54b"
    source_file = "Bollinger带震荡型突破策略Bollinger-Bands-Oscillation-Breakthrough-Strategy.md"
    timeframe = "1m"
    # Only `strategy.entry(id="long", long = true, ...)` and its close exist.
    can_short = False
    source_defaults: dict = {
        # input(close, title="Source") -- Pine's source selector, default close.
        "src": "close",
        # input(defval = 1, title = "From Month", type = input.integer, minval = 1, maxval = 12)
        "fromMonth": 1,
        # input(defval = 1, title = "From Day", type = input.integer, minval = 1, maxval = 31)
        "fromDay": 1,
        # input(defval = 2020, title = "From Year", type = input.integer, minval = 1970)
        "fromYear": 2020,
        # input(defval = 1, title = "Thru Month", ...)
        "thruMonth": 1,
        # input(defval = 1, title = "Thru Day", ...)
        "thruDay": 1,
        # input(defval = 2112, title = "Thru Year", ...)
        "thruYear": 2112,
        # input(defval = true, title = "Show Date Range", type = input.bool)
        "showDate": True,
        # input(20, minval=1)
        "lengthBB": 20,
        # input(2.0, minval=0.001, maxval=50, title="StdDev")
        "mult": 2.0,
        # input(0, "Offset", type = input.integer, minval = -500, maxval = 500)
        "offset": 0,
        # input(288, minval=1)
        "lengthAr": 288,
        # input(90, "Aroon Confirmation")
        "Confirmation": 90,
        # input(70, "Aroon Stop")
        "Stop": 70,
    }
    # The ONLY strategy() declaration in the file is line 13 and it is commented
    # out, so nothing is declared: Pine's documented defaults apply --
    # `strategy.fixed` / 1 contract, initial capital 1000000, commission 0%,
    # pyramiding 0, process_orders_on_close false. The commented line asks for
    # percent_of_equity / 30, initial capital 1000, commission 0.1% and
    # process_orders_on_close=true; none of it is in force (see fidelity notes).
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # The exit is `strategy.close`, a market order; no stop / limit / trail leg
    # exists anywhere in the file.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "NOT a converter-appended order block: the file declares nothing active "
        "(no indicator(), no study(), and its only strategy() line is COMMENTED "
        "OUT), and both of its order calls -- strategy.entry at line 54 and "
        "strategy.close at line 58 -- are the author's own active code. Its "
        "tier_reason's 'declares indicator()/study(), tool appended "
        "strategy.entry pair; NO exits' is false on both counts.",
        "The file's only strategy() declaration is COMMENTED OUT (line 13), so "
        "it declares nothing and Pine's documented defaults apply: fixed / 1 "
        "contract, initial capital 1000000, commission 0%, pyramiding 0, "
        "process_orders_on_close false. A commented-out line is not in force, "
        "the same rule PINE_SEMANTICS.md 1.17 applies to commented-out exit "
        "lines.",
        "RECORDED BUT NOT APPLIED (commented out): the declaration asks for "
        "default_qty_type=strategy.percent_of_equity with default_qty_value=30, "
        "initial_capital=1000, commission_value=0.1 percent, and "
        "process_orders_on_close=true. Were it live, the last of those would "
        "fill market orders at the signal bar's OWN CLOSE instead of the next "
        "bar's open -- a timing the classic engine does not model at all "
        "(PINE_SEMANTICS.md section 一). It is not applied because the line is "
        "inert in the source. FMZ's inventory also flags the source as "
        "`close_execution` on the strength of that commented text.",
        "window() IS MEANINGFUL HERE and is reproduced from the six date "
        "inputs: it opens 2020-01-01 00:00 and closes 2112-01-01 23:59. Both "
        "conditions carry it (`Bullish and AroonUP > Confirmation and window()` "
        "for the entry, `Bearish or AroonUP < Stop and window()` for the "
        "close), so no entry at all can fire on data older than 2020 -- "
        "including validate_pine's synthetic frame, which starts 2019-01-01. "
        "That is the source's behaviour, kept deliberately rather than dropped.",
        "Operator precedence: `and` binds tighter than `or` in Pine, so the "
        "close is `Bearish or (AroonUP < Stop and window())`. `Bearish` is NOT "
        "gated by window().",
        "highestbars / lowestbars are not in pine_ta and are implemented here "
        "from the Pine definition (negative offset to the window extreme, na "
        "until the window is full). Ties resolve to the MOST RECENT occurrence "
        "-- Pine's reference implementation scans backwards and stops at the "
        "first match -- which TradingView does not document, so it is an "
        "equivalence risk (cf. PINE_SEMANTICS.md section 三).",
        "MD/SOURCE MISMATCH (exit): the md says the Aroon DOWN line decides the "
        "exit; the source never reads AroonDown and exits on `AroonUP < Stop`. "
        "The source is followed, and AroonDown is still computed because the "
        "source computes it.",
        "MD/SOURCE MISMATCH (triggers): the md describes the entry and exit as "
        "breakouts (突破) of the middle band; the source uses "
        "`crossunder(close, basis)` for the entry and `crossunder(close, upper)` "
        "-- the UPPER band -- for the exit. The source is followed.",
        "MD/SOURCE MISMATCH (short side): the md says a downward breakthrough of "
        "the middle band from the upper band 'signals short entry'. The source "
        "has no short entry, no short branch and no strategy.short call anywhere "
        "-- it is long only, which is why can_short is False. Source followed.",
        "MD/SOURCE MISMATCH (stop loss / take profit): the md says the strategy "
        "sets stop-loss AND take-profit conditions and that a stop loss plus the "
        "Aroon Down line control downside risk. The source has no stop order, no "
        "stop-loss parameter, no take-profit and no AroonDown test; its only "
        "exit is the `AroonUP < Stop` level test. Source followed.",
        "MD/SOURCE MISMATCH (risk): the md also claims partial position sizing "
        "limits per-trade loss. Sizing comes from the (commented) strategy() "
        "declaration; with that line inert, Pine's default is one contract.",
        "MD/SOURCE MISMATCH (arguments): the md renders v_input_9_close as 0 for "
        "a source selector whose options are close/high/low/open/hl2/hlc3/hlcc4/"
        "ohlc4, and v_input_11 (Offset) as false for the integer 0. The source's "
        "real defaults (close, 0) are declared here.",
        "`lower` is computed by the source and never read by any condition; it "
        "is reproduced as a column. `AroonDown` and `offset` are the same: "
        "computed/declared and unused. Dead code is kept, not deleted.",
        "`stdev` is Pine's population standard deviation (biased=true, ddof=0), "
        "as pine_ta.pine_stdev implements it; `mult` scales it onto the basis.",
        "The md's argument table renders the six date inputs as `true` (FMZ's "
        "bool column showing the integer 1); the source's real integer defaults "
        "are declared here.",
        "`sma` is na until its window is full and na propagates through the "
        "window, so basis/upper are na for the first lengthBB-1 bars and no "
        "cross can be true there; AroonUP needs lengthAr+1 = 289 bars.",
        "plot / hline / fill are display-only and are not reproduced (the "
        "source has no plot calls at all).",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step "
        "rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        length_bb = int(params["lengthBB"])
        mult = float(params["mult"])
        length_ar = int(params["lengthAr"])

        # basis = sma(src, lengthBB)
        # dev   = mult * stdev(src, lengthBB)
        # upper = basis + dev ; lower = basis - dev
        basis = ta.pine_sma(src, length_bb)
        dev = mult * ta.pine_stdev(src, length_bb)
        upper = basis + dev
        lower = basis - dev

        # AroonUP   = 100 * (highestbars(high, lengthAr+1) + lengthAr) / lengthAr
        # AroonDown = 100 * (lowestbars(low,  lengthAr+1) + lengthAr) / lengthAr
        high = dataframe["high"].to_numpy(dtype=float)
        low = dataframe["low"].to_numpy(dtype=float)
        aroon_up = 100.0 * (
            _extreme_offset(high, length_ar + 1, True) + length_ar
        ) / length_ar
        aroon_down = 100.0 * (
            _extreme_offset(low, length_ar + 1, False) + length_ar
        ) / length_ar

        # window() => time >= start and time <= finish ? true : false
        # `time` is the bar's OPEN time, which is the frame's index here.
        index = dataframe.index
        tz = getattr(index, "tz", None)
        start = pd.Timestamp(
            f"{int(params['fromYear']):04d}-{int(params['fromMonth']):02d}-"
            f"{int(params['fromDay']):02d} 00:00:00",
            tz=tz,
        )
        finish = pd.Timestamp(
            f"{int(params['thruYear']):04d}-{int(params['thruMonth']):02d}-"
            f"{int(params['thruDay']):02d} 23:59:00",
            tz=tz,
        )
        in_window = (index >= start) & (index <= finish)

        dataframe["pine_basis"] = basis
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_aroon_up"] = aroon_up
        dataframe["pine_aroon_down"] = aroon_down
        dataframe["pine_offset"] = float(params["offset"])

        # Bullish = crossunder(close, basis)
        # Bearish = crossunder(close, upper)
        bullish = ta.pine_crossunder(dataframe["close"], basis)
        bearish = ta.pine_crossunder(dataframe["close"], upper)
        # strategy.entry(id="long", long=true,
        #                when = Bullish and AroonUP > Confirmation and window())
        dataframe["pine_enter"] = (
            bullish
            & (aroon_up > float(params["Confirmation"]))
            & in_window
        )
        # strategy.close("long", when = Bearish or AroonUP < Stop and window())
        dataframe["pine_exit"] = bearish | (
            (aroon_up < float(params["Stop"])) & in_window
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "enter": dataframe["pine_enter"].to_numpy(dtype=bool),
            "exit": dataframe["pine_exit"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry(id="long", long = true,
        #                when = Bullish and AroonUP > Confirmation and window())
        if ctx["enter"][i]:
            broker.entry("long", "long")

        # strategy.close("long", when = Bearish or AroonUP < Stop and window())
        # `strategy.close` on an entry that is not open closes nothing; the
        # engine matches on the entry id, so no position test is added here.
        if ctx["exit"][i]:
            broker.close("long")
