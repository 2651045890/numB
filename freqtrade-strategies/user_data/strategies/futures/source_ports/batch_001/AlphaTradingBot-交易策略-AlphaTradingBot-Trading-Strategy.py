"""Port of sources/SM_537003b549989c9a.pine (batch_001/AlphaTradingBot-交易策略-AlphaTradingBot-Trading-Strategy.md).

Pine v5, "Augusto Bot v1.2" by javierfish, on the `/*backtest` header's
`period: 1h`. A Zigzag + Fibonacci retracement strategy driven by a nine-state
machine (`status` 0..8). The trading-relevant spine, in source order:

    lb = input.int(5, 'Pivot Bars Count', minval=1)
    rb = lb
    ph = ta.pivothigh(lb, rb)
    pl = ta.pivotlow(lb, rb)

    iff_1 = pl ? -1 : na
    hl = ph ? 1 : iff_1
    iff_2 = pl ? pl : na
    zz = ph ? ph : iff_2
    valuewhen_1 = ta.valuewhen(hl, hl, 1)
    valuewhen_2 = ta.valuewhen(zz, zz, 1)
    zz := pl and hl == -1 and valuewhen_1 == -1 and pl > valuewhen_2 ? na : zz
    valuewhen_3 = ta.valuewhen(hl, hl, 1)
    valuewhen_4 = ta.valuewhen(zz, zz, 1)
    zz := ph and hl == 1 and valuewhen_3 == 1 and ph < valuewhen_4 ? na : zz
    valuewhen_5 = ta.valuewhen(hl, hl, 1)
    valuewhen_6 = ta.valuewhen(zz, zz, 1)
    hl := hl == -1 and valuewhen_5 == 1 and zz > valuewhen_6 ? na : hl
    valuewhen_7 = ta.valuewhen(hl, hl, 1)
    valuewhen_8 = ta.valuewhen(zz, zz, 1)
    hl := hl == 1 and valuewhen_7 == -1 and zz < valuewhen_8 ? na : hl
    zz := na(hl) ? na : zz

    [loc1, loc2, loc3, loc4] = findprevious()   // four 1000-bar back-scans
    a = fixnan(zz) ; b, c, d, e = loc1..loc4

    _hh = zz and a > b and a > c and c > b and c > d
    _ll = zz and a < b and a < c and c < b and c < d
    _hl = zz and (a >= c and b > c and b > d and d > c and d > e
                  or a < b and a > c and b < d)
    _lh = zz and (a <= c and b < c and b < d and d < c and d < e
                  or a > b and a < c and b > d)

The five `ta.valuewhen` pairs are FIVE SEPARATE CALL SITES and the assignments
between them change what each one is fed. `hl` is rewritten at line 60, so
`valuewhen_5` (fed the pre-line-60 `hl`) and `valuewhen_7` (fed the post-line-60
`hl`) are NOT the same series; `zz` is rewritten at line 53 and line 56, so
`valuewhen_2` (fed the line-50 `zz`), `valuewhen_4` (fed the post-line-53 `zz`)
and `valuewhen_6`/`valuewhen_8` (both fed the post-line-56 `zz`) are three
different series. `valuewhen_1`/`_3`/`_5` all see an unchanged `hl` and are one
series; `valuewhen_6` and `valuewhen_8` are one series. The port keeps all eight
call sites distinct in the source's own order rather than collapsing the pairs,
so a later correction to one of them cannot silently move another.

`findprevious()` is a pure function of the current bar's `hl` / `zz` history --
it holds no state across bars (`xx` is re-initialised to 0 on every call) -- so
the four 1000-bar scans are precomputed here exactly as written: `ehl` alternates
opposite / same / opposite / same relative to the current bar's `hl`, each scan
starts at the previous scan's `x + 1`, and `xx` CAN BE 0, which lets the second
scan start on the current bar and match itself. loc1..loc4 stay at their 0.0
initialiser when a scan finds nothing, and all four stay na when `hl` is na.
A scan is over `x = start to 1000`, and an out-of-range `hl[x]` is na (Pine
answers na for history beyond the first bar), which never equals `ehl`.

The state machine (statuses 0, 1, 3, 5, 7 for longs; 0, 2, 4, 6, 8 for shorts)
is translated statement by statement, in order, including `strategy.cancel_all()`
placement and the `if` / `else if` chain shape, and including the trailing
`[fib50, fibUP, fibDW] = fibo(highest, lowest)` + `entryPrice := fib50` that
runs AFTER the inner if/else in statuses 1 and 2 -- which overwrites the
`entryPrice := close` set inside the `if` branch, so that assignment only ever
reaches `diff`, `longTP` / `shortTP` and `lotSize`.

ORDER TIMING. All six entries are LIMIT entries with their stop/take-profit
placed in the same branch:

    strategy.entry('? 1', strategy.long, limit = entryPrice, qty = lotSize, ...)
    strategy.exit('lx', '? 1', limit = longTP, stop = longSL, ...)

The engine rests the limit and fills it intrabar (a gap through the level fills
at the open); the framework projection can only emit `enter_long` on the
placement bar and fill at the next open. PINE_SEMANTICS.md 2.11 records that
limit ENTRY orders are not projectable, and this source is made of nothing else
-- every one of its six entries is a limit. The engine side of the chain check
is faithful; the framework side is structurally mistimed, and any engine /
framework disagreement here is that boundary rather than a translation choice.
RECORDED from the default `verify_chain` window (BTC/USDT:USDT 1h,
20240101-20250101): the engine closes 51 trades, the framework 36, and the
verdict is `mismatch_framework_veto` -- the projection gap is the dominant term
there, not a masked one. All 36 framework close dates fall inside the engine's
51 (0 framework-only, 15 engine-only); the first trade alone shows the timing
offset (engine opens at 44100.28 on its resting limit, the framework at 44058.1
at the next open) and 29 of the 36 shared close dates have differing entry
rates. The framework's exit reasons are 34 `exit_signal` (the projected
`close_all`) plus 2 `stop_loss` (the mirrored stop leg). 25 of its 36 trades are
sized at the declared fixed 1.0 rather than the source's `qty = lotSize`,
because the engine freezes that quantity on the PLACEMENT bar and the
per-candle stake schedule misses whenever the framework's entry candle differs
(a 2.11 consequence). A further 27 orders were refused by the framework's
`max_stake` (sample: required=139784.96 > max_stake=98841.67, and
required=732718.15 > max_stake=99334.47).

PROVENANCE OF THOSE NUMBERS. They are the run recorded in
`strategy_migration/chain_verdicts/SMAlphaTradingBot_537003.json` against
port_sha256 e85464139ebf5697a8129be16339ccaaaedbe4f26bb7880c8b44985249a60509.
This file's hash is now 681fee327b747cc7fddb362a96e57a1d2dcd919ed6a494f329a28696d1ae21be
(the docstring was extended after that run), so the ENGINE side was re-measured
on the current revision and reproduces it exactly: 51 closed trades and a final
position of 0.0 on BTC/USDT:USDT 1h 20240101-20250101, signals 130 `enter_long`
/ 0 `enter_short` / 47 `exit_long`, and 21 / 25 / 22 closed trades with a final
position of exactly 0 on the three synthetic seeds below. The FRAMEWORK side
(36 trades, 29 of 36 shared close dates with differing entry rates, 34
`exit_signal` + 2 `stop_loss`) was NOT re-measured in this wave -- the chain
tool is the verification wave's job -- so it is reported as a recorded run of
the earlier revision, not as a measurement of the bytes on disk here.

`buy`/`sell` sizing: every entry passes an explicit `qty=lotSize` where
`lotSize = usdRisk / diff`, `usdRisk = max(strategy.equity * pctRisk/100, 0)` and
`diff` is the entry-to-stop distance. Because `qty` is explicit, the engine
freezes the quantity at the PLACEMENT bar from the equity it read there, which
is what Pine does; the declared `default_qty_value = 1` is never used. `diff` is
always positive at every call site (each entry is guarded by
`entryPrice > longSL` / `entryPrice < shortSL`), so `lotSize` is always positive.

DATA-RANGE COLUMN. `intDesde` is never read (dead). `intHasta` is read only by
`exitLong` / `exitShort`, which force a full close once the bar's time reaches
it. With the source's own default `intHasta = timestamp('2023-12-31T23:59:59')`
every bar from 2024 on satisfies it, so a position cannot survive: it is
force-closed on the bar after it opens. MEASURED on synthetic 1h frames
starting in 2024 (seeds 782/11/42): the gate is true on all 3000/3000 bars,
21 / 25 / 22 trades close, and the final position is exactly 0. On the same
frames shifted to start in 2019 the gate is true on 0/3000 bars, nothing is
force-closed, and the runs end holding 483.17 / 680.41 / 384.40 units. So on
any post-2023 window this default trades bar-to-bar, and the window's dates
decide whether the strategy can hold a position at all. Pine's
`timestamp(dateString)`
is documented as interpreting the string in the exchange's timezone; the layer's
timezone is UTC (PINE_SEMANTICS.md 3.4) and that is the model used here -- for
this default value the choice cannot change a 2024 backtest, but a custom
`intHasta` near a date boundary would be off by the exchange offset.
`barstate.isconfirmed` is modelled as True: the engine evaluates the script at
bar close, which is exactly the state that flag describes.

FIDELITY:

* All six entries are `limit=` orders -- see ORDER TIMING above.
* The md's argument table records `v_input_float_1 = true` for "Riesgo %"; the
  SOURCE says `input.float(1, 'Riesgo %', 0.1, 100, step=.1)`. The code is
  followed (1).
* md-vs-source: the md's principle 2 says "When an HH appears, it is regarded as
  the beginning of an uptrend and the strategy starts looking for long
  opportunities; when an LL appears ... short opportunities". The code is the
  other way round: status 0 starts a LONG setup on `_ll` and a SHORT setup on
  `_hh`. Code followed, prose recorded.
* md-vs-source: the md's principle 5 says "If the loss of a single trade reaches
  X% of the total account balance, the strategy stops running". No such check
  exists in the code. `pctRisk` is used only to size the order
  (`usdRisk / diff`); nothing inspects a realised loss and nothing halts. Code
  followed.
* md-vs-source: the md's principles 3 and 4 describe the entry zone as
  23.6%-38.2% / 61.8%-76.4% retracements. The code's defaults are `retro = 40`
  and `fibSL = 72`, and the long entry sits at `1 - retro/100` = 60% of the
  range. The formulas are reproduced as written; the md's numbers are design
  intent, not the defaults.
* md-vs-source: the md says the strategy "only runs within a specified date
  range". `intDesde` is dead and `intHasta` only forces a close -- new setups
  continue to form after it. Code followed.
* md-vs-source: the md says the strategy "can go both long and short". Both
  paths are implemented, but `blnShorts` defaults to false, so with the
  published defaults only statuses 1/3/5/7 can ever be reached.
* DEAD CODE, computed as the source computes it: `intDesde`; `blnEnTrade`;
  `blnOrder` (assigned at 153 and again in statuses 7/8, never read);
  `prevSignal`; `rechange` / `suchange`; the whole `res` / `sup` / `trend` block
  (lines 119-131), whose only consumers are the `showsupres` display lines; and
  `iff_1`..`iff_4`. They are computed here and kept as columns or state, never
  read for trading.
* DEAD-BRANCH CONDITION: `blnFechas` is the literal `true` (line 27, NOT an
  input), so `status == 0 and blnFechas` is `status == 0`, and the `blnDebug and
  status == N and blnFechas` plotchars are unreachable because `blnDebug`
  defaults to false.
* na handling: `na` comparisons are false (the repository convention). Every
  expression built from `a`, `b`..`e` and `zz` is consumed only as an `if` or
  ternary CONDITION, so a three-valued na model and the false model agree on
  every value the port acts on.
* `a = fixnan(zz)` is modelled as a forward fill, which is what fixnan is; it
  stays na until the first non-na `zz`, and every condition that reads it is
  then false.
* Display-only and not reproduced: the `line.new` supremacy lines, `barcolor`,
  the nine `plotchar`s, `plotshape`, `plot(...)` and the `fill(...)` pairs of
  the zigzag and the long/short risk boxes. `strategy.risk.*` is not used.
* `strategy()` declares `pyramiding=0`, `initial_capital=100000` and
  `default_qty_value=1`; `default_qty_type` is not declared, so Pine's
  documented default `strategy.fixed` is recorded, and commission is not
  declared (Pine's 0%). Every entry overrides the quantity, so the fixed/1
  sizing is inert.
* SAME-ID ENTRY ORDERS: the engine appends a second order when `strategy.entry`
  is called twice with an id that is already resting, while Pine's own rule for
  an entry whose id already rests is not published here. `pyramiding=0` blocks a
  second order from filling while the first entry is held, so this cannot open a
  doubled position; it could in principle leave two same-id limit orders
  resting. MEASURED on three synthetic 1h 3000-bar frames (seeds 782/11/42),
  counting the broker's own resting-order queue: at most ONE order per id was
  ever resting at once, so the doubling did not occur in those runs. The port
  does not "fix" it -- it calls `strategy.entry` exactly where the source
  does -- and the residual risk is recorded rather than resolved.
* No future-data reference and no repainting: every input is the current bar's
  own OHLC, pivots are reported `rb` bars after the fact, and entries fill at
  the limit or on the next bar.
* The `/*backtest` window (2024-04-20 to 2024-04-27) is the host's extraction
  metadata, not an input time filter applied by the port.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are not modelled.
"""
from __future__ import annotations

import bisect

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMAlphaTradingBot_537003(PinePortBase, IStrategy):
    source_id = "SM_537003b549989c9a"
    source_file = "AlphaTradingBot-交易策略-AlphaTradingBot-Trading-Strategy.md"
    # /*backtest ... period: 1h, basePeriod: 15m
    timeframe = "1h"
    # The short half of the state machine is reachable with blnShorts = true.
    can_short = True
    source_defaults: dict = {
        "lb": 5,
        "intDesde": "2023-01-01T00:00:00",
        "intHasta": "2023-12-31T23:59:59",
        "blnShorts": False,
        "pctRisk": 1.0,
        "RR": 2.0,
        "retro": 40.0,
        "fibSL": 72.0,
        "blnDebug": False,
    }
    # strategy(...) does not declare default_qty_type, so Pine's documented
    # default `strategy.fixed` stands; every entry overrides qty anyway.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    # strategy.exit(..., limit=..., stop=...) arms a real stop leg.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "All six entries are LIMIT entries (strategy.entry(..., limit = "
        "entryPrice, qty = lotSize)), with strategy.exit(..., limit = longTP, "
        "stop = longSL) placed in the same branch. The engine rests the limit "
        "and fills it intrabar; the framework projection can only emit "
        "enter_long on the placement bar and fill at the next open. "
        "PINE_SEMANTICS.md 2.11 records that limit ENTRY orders cannot be "
        "projected, and this source consists of nothing else. The engine side "
        "of the chain is faithful; the framework side is structurally "
        "mistimed. RECORDED run (see the module docstring's PROVENANCE "
        "paragraph: the engine number below was re-measured on THIS revision, "
        "the framework numbers come from the recorded verdict of the revision "
        "whose port_sha256 is e8546413...) on the default verify_chain window "
        "(BTC/USDT:USDT 1h, 20240101-20250101): engine 51 closed trades, "
        "framework 36, verdict "
        "mismatch_framework_veto. All 36 framework close dates are inside the "
        "engine's 51 (0 framework-only, 15 engine-only); 29 of the 36 shared "
        "close dates have different entry rates (first trade: engine 44100.28 "
        "on the resting limit, framework 44058.1 at the next open); framework "
        "exit reasons are 34 exit_signal and 2 stop_loss; and 27 orders were "
        "refused by the framework's max_stake (required=139784.96 > "
        "max_stake=98841.67). The gap is the dominant term of the default "
        "comparison, not a masked one.",
        "Sizing schedules: 25 of the framework's 36 trades are sized at the "
        "declared fixed 1.0 instead of the source's qty = lotSize, because the "
        "engine freezes lotSize on the PLACEMENT bar and the framework's entry "
        "candle differs (the 2.11 timing gap above), so the per-candle stake "
        "schedule misses and the port falls back to its derived stake.",
        "Sizing: lotSize = usdRisk / diff with usdRisk = max(strategy.equity * "
        "pctRisk/100, 0) and diff the entry-to-stop distance. Because qty is "
        "explicit, the engine freezes the quantity at the PLACEMENT bar from "
        "the equity read there, which is what Pine does. The declared "
        "default_qty_value = 1 is never used. diff is positive at every call "
        "site (each entry is guarded by entryPrice > longSL / entryPrice < "
        "shortSL), so lotSize is always positive.",
        "PARAMETER EDGE, not guarded and not reachable from the declared "
        "defaults: `lotSize = usdRisk / diff` is evaluated BEFORE the "
        "`entryPrice > longSL` / `entryPrice < shortSL` guard, exactly as the "
        "source writes it. With retro = 40 and fibSL = 72 the long-side diff is "
        "32% of the range and the short-side diff the same, so it is never 0; "
        "an override that sets retro == fibSL makes entryPrice and the stop "
        "level exactly equal, and this port would then raise ZeroDivisionError "
        "where the platform's float division would not (the platform's exact "
        "0/0 and x/0 results are NOT verified here). Recorded rather than "
        "special-cased, since the guard order is the source's.",
        "intHasta is read only by exitLong/exitShort, which force a full close "
        "once the bar's time reaches it; intDesde is never read at all (dead). "
        "MEASURED with the source's own default intHasta = "
        "timestamp('2023-12-31T23:59:59') on synthetic 1h frames starting in "
        "2024: the gate is true on all 3000/3000 bars, so each position is "
        "force-closed the bar after it opens -- 21 / 25 / 22 closed trades and "
        "a final position of exactly 0 (seeds 782/11/42). Shifted to start in "
        "2019 the gate is true on 0/3000 bars, nothing is force-closed, and the "
        "runs end holding 483.17 / 680.41 / 384.40 units. So on a post-2023 "
        "window this default trades bar-to-bar and the window's dates decide "
        "whether a position can be held at all. Pine interprets "
        "timestamp(dateString) in the EXCHANGE's timezone; the layer's timezone "
        "is UTC (PINE_SEMANTICS.md 3.4) and that is the model used -- "
        "immaterial for this default, but a custom intHasta near a boundary "
        "would be off by the exchange offset.",
        "barstate.isconfirmed is modelled as True: the engine evaluates the "
        "script at bar close, which is the state that flag describes.",
        "md-vs-source: the md's table gives v_input_float_1 as `true` for "
        "'Riesgo %'; the source says input.float(1, 'Riesgo %', 0.1, 100, "
        "step=.1). Code followed (1).",
        "md-vs-source: the md says an HH starts the search for LONGS and an LL "
        "for SHORTS. The code is the reverse: status 0 starts a long setup on "
        "_ll and a short setup on _hh. Code followed.",
        "md-vs-source: the md says 'If the loss of a single trade reaches X% of "
        "the total account balance, the strategy stops running'. No such check "
        "exists -- pctRisk only sizes the order (usdRisk / diff) and nothing "
        "halts. Code followed.",
        "md-vs-source: the md describes the entry zone as 23.6%-38.2% (long) "
        "and 61.8%-76.4% (short) retracements. The code's defaults are retro = "
        "40 and fibSL = 72, and the long entry sits at 1 - retro/100 = 60% of "
        "the range. Formulas reproduced as written; the md's numbers are "
        "design intent.",
        "md-vs-source: the md says the strategy 'only runs within a specified "
        "date range'. intDesde is dead and intHasta only forces a close -- new "
        "setups keep forming after it. Code followed.",
        "md-vs-source: the md says the strategy 'can go both long and short'. "
        "Both paths are implemented, but blnShorts defaults to false, so with "
        "the published defaults only statuses 1/3/5/7 are reachable.",
        "DEAD CODE, computed but never read for trading: intDesde; blnEnTrade; "
        "blnOrder (assigned at line 153 and again in statuses 7/8); prevSignal; "
        "rechange / suchange; the whole res / sup / trend block (lines "
        "119-131), whose only consumers are the showsupres display lines; and "
        "iff_1..iff_4. Computed here and kept as columns or state.",
        "blnFechas is the literal `true` (line 27, not an input), so "
        "`status == 0 and blnFechas` is `status == 0` and the blnDebug "
        "plotchars are unreachable at the default blnDebug = false.",
        "findprevious() is precomputed because it holds no state across bars "
        "(xx is re-initialised to 0 on every call): it is a pure function of "
        "the current bar's hl/zz history. The four scans start at 1, xx, xx, xx "
        "with ehl alternating opposite / same / opposite / same, xx can be 0 "
        "(so the second scan can match the current bar itself), loc1..loc4 keep "
        "their 0.0 initialiser when a scan finds nothing, and all four stay na "
        "when hl is na. History beyond the first bar is na and never equals "
        "ehl, which is what bounds each `for x = start to 1000` scan.",
        "The five ta.valuewhen pairs are five separate call sites fed different "
        "series -- hl is rewritten at line 60 and zz at lines 53 and 56 -- so "
        "the port keeps all eight distinct in the source's order rather than "
        "collapsing valuewhen_1/_3/_5 and valuewhen_6/_8, which happen to be "
        "equal.",
        "na handling: na comparisons are false (repository convention). Every "
        "expression built from a, b..e and zz is consumed only as an if or "
        "ternary CONDITION, so a three-valued na model and the false model "
        "agree on every value the port acts on. a = fixnan(zz) is modelled as a "
        "forward fill and stays na until the first non-na zz.",
        "The trailing `[fib50, fibUP, fibDW] = fibo(highest, lowest)` + "
        "`entryPrice := fib50` inside statuses 1 and 2 runs AFTER the inner "
        "if/else, so it overwrites the `entryPrice := close` set inside the "
        "`if` branch -- that assignment only ever reaches diff, longTP and "
        "lotSize. Reproduced.",
        "SAME-ID ENTRY ORDERS: the engine appends a second order when "
        "strategy.entry is called again with an id that is already resting. "
        "Pine's own rule for an already-resting entry id is not published here. "
        "pyramiding = 0 blocks a second fill while the first entry is held, so "
        "no doubled position can open; two same-id limit orders could still "
        "rest together. MEASURED by tracing PineBroker._place and counting the "
        "live (uncancelled) resting orders per id: the peak is 1 for every id "
        "on BTC/USDT:USDT 1h 20240101-20250101 (307 orders placed) and on the "
        "three synthetic 1h seeds, so the doubling did not occur in these runs. "
        "An uncancelled count instead reports a peak of 2 for '? 5', which is "
        "the same-bar cancel_all() + re-place pair, not two live orders. The "
        "port calls strategy.entry exactly where the source does and records "
        "the risk rather than resolving it (PINE_SEMANTICS.md 1.12, unfixed in "
        "the shared layer).",
        "Display-only and not reproduced: the line.new supremacy lines, "
        "barcolor, the nine plotchars, plotshape, plot(...) and the fill(...) "
        "pairs. strategy.risk.* is not used.",
        "default_qty_type is not declared, so Pine's documented default "
        "strategy.fixed and default_qty_value = 1 are recorded; both are inert "
        "because every entry passes an explicit qty.",
        "No future-data reference and no repainting: pivots are reported rb "
        "bars after the fact and entries fill at the limit or on the next bar.",
        "The /*backtest window (2024-04-20 to 2024-04-27) is extraction "
        "metadata; the port applies no such filter itself.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled.",
    ]

    # ---- zigzag scaffolding ------------------------------------------------
    @staticmethod
    def _findprevious(hl: np.ndarray, zz: np.ndarray):
        """findprevious(): the previous three points (b, c, d, e).

        Translated from the source's four `for x = start to 1000` scans. `ehl`
        alternates opposite / same / opposite / same relative to the current
        bar's `hl`, and each scan starts at the previous scan's `x + 1` -- which
        can be 0, letting the second scan match the current bar itself. A
        matching bar needs `hl[x] == ehl` AND a non-na `zz[x]`. The scans are
        bounded by `1000` and by the available history (an out-of-range `hl[x]`
        is na and never equals `ehl`).

        Precomputed as a vectorised scan over the two eligible-index lists, with
        `bisect_right` giving the LARGEST matching index -- i.e. the SMALLEST
        `x`, which is the first hit the ascending-`x` loop would take.
        """
        n = len(hl)
        locs = [np.full(n, np.nan) for _ in range(4)]
        up: list[int] = []    # bars where hl == 1 and zz is not na
        down: list[int] = []  # bars where hl == -1 and zz is not na
        for i in range(n):
            h = hl[i]
            # `if not na(hl)`: everything below runs only on such a bar, and
            # loc1..loc4 then start at their 0.0 initialiser rather than na.
            if np.isnan(h):
                continue
            z = zz[i]
            if not np.isnan(z):
                # A candidate needs hl[x] == ehl AND a non-na zz[x]; bar `i`
                # itself is a candidate for the second scan, which starts at
                # x = 0 when the first scan found nothing.
                (up if h == 1 else down).append(i)
            found = [0.0, 0.0, 0.0, 0.0]
            xx = 0
            for slot, ehl in enumerate((-h, h, -h, h)):
                if xx > 1000:
                    continue
                candidates = down if ehl == -1 else up
                lo_j = i - 1000
                if lo_j < 0:
                    lo_j = 0
                hi_j = i - xx
                if hi_j < lo_j:
                    continue
                k = bisect.bisect_right(candidates, hi_j) - 1
                if k < 0:
                    continue
                j = candidates[k]
                if j >= lo_j:
                    found[slot] = zz[j]
                    xx = (i - j) + 1
            for slot in range(4):
                locs[slot][i] = found[slot]
        return locs

    @staticmethod
    def _time_ge(dataframe: pd.DataFrame, cutoff_ms: int) -> np.ndarray:
        """Pine `time >= intHasta`, on the bar's OPENING time."""
        index = dataframe.index
        if isinstance(index, pd.DatetimeIndex):
            stamps = index
        elif "date" in dataframe.columns:
            stamps = pd.DatetimeIndex(pd.to_datetime(dataframe["date"]))
        else:
            # No calendar to read: the comparison cannot be true. Recorded in
            # the notes rather than guessed at.
            return np.zeros(len(dataframe), dtype=bool)
        if stamps.tz is not None:
            stamps = stamps.tz_convert("UTC")
        # pandas 3 indexes are datetime64[us], not [ns], and `asi8` carries
        # WHATEVER resolution the index holds -- dividing it by 10**6 as if it
        # were ns turns every 2024 bar into the year 1970 (measured: this
        # silently disarmed intHasta entirely). Pin the resolution first.
        if hasattr(stamps, "as_unit"):
            stamps = stamps.as_unit("ns")
        return (stamps.asi8 // 10**6) >= cutoff_ms

    def pine_indicators(self, dataframe, params):
        high = dataframe["high"]
        low = dataframe["low"]
        close = dataframe["close"]
        length = int(params["lb"])
        # ph = ta.pivothigh(lb, rb) ; pl = ta.pivotlow(lb, rb)   (rb = lb)
        ph = ta.pine_pivothigh(high, length, length)
        pl = ta.pine_pivotlow(low, length, length)

        # iff_1 = pl ? -1 : na ; hl = ph ? 1 : iff_1
        hl_a = pd.Series(
            np.where(ph.notna(), 1.0, np.where(pl.notna(), -1.0, np.nan)),
            index=dataframe.index,
        )
        # iff_2 = pl ? pl : na ; zz = ph ? ph : iff_2
        zz_a = ph.combine_first(pl)

        # valuewhen_1 / valuewhen_3 / valuewhen_5 are all ta.valuewhen(hl, hl, 1)
        # with an unchanged `hl`; kept as one series with the source's call
        # sites named so the aliasing is visible.
        valuewhen_1 = ta.pine_valuewhen(hl_a, hl_a, 1)
        valuewhen_3 = valuewhen_1
        valuewhen_5 = valuewhen_1
        valuewhen_2 = ta.pine_valuewhen(zz_a, zz_a, 1)
        zz_b = zz_a.mask(
            (pl.notna() & (hl_a == -1) & (valuewhen_1 == -1) & (pl > valuewhen_2)
             ).fillna(False)
        )
        valuewhen_4 = ta.pine_valuewhen(zz_b, zz_b, 1)
        zz_c = zz_b.mask(
            (ph.notna() & (hl_a == 1) & (valuewhen_3 == 1) & (ph < valuewhen_4)
             ).fillna(False)
        )
        # valuewhen_6 and valuewhen_8 are both ta.valuewhen(zz, zz, 1) with the
        # same (post-line-56) `zz`.
        valuewhen_6 = ta.pine_valuewhen(zz_c, zz_c, 1)
        valuewhen_8 = valuewhen_6
        hl_b = hl_a.mask(
            ((hl_a == -1) & (valuewhen_5 == 1) & (zz_c > valuewhen_6)).fillna(False)
        )
        valuewhen_7 = ta.pine_valuewhen(hl_b, hl_b, 1)
        hl_c = hl_b.mask(
            ((hl_b == 1) & (valuewhen_7 == -1) & (zz_c < valuewhen_8)).fillna(False)
        )
        zz_d = zz_c.mask(hl_c.isna())

        loc1, loc2, loc3, loc4 = self._findprevious(
            hl_c.to_numpy(dtype=float), zz_d.to_numpy(dtype=float)
        )
        b = pd.Series(loc1, index=dataframe.index)
        c = pd.Series(loc2, index=dataframe.index)
        d = pd.Series(loc3, index=dataframe.index)
        e = pd.Series(loc4, index=dataframe.index)
        # a = fixnan(zz)
        a = zz_d.ffill()

        zz_ok = zz_d.notna()
        _hh = zz_ok & (a > b) & (a > c) & (c > b) & (c > d)
        _ll = zz_ok & (a < b) & (a < c) & (c < b) & (c < d)
        _hl = zz_ok & (
            ((a >= c) & (b > c) & (b > d) & (d > c) & (d > e))
            | ((a < b) & (a > c) & (b < d))
        )
        _lh = zz_ok & (
            ((a <= c) & (b < c) & (b < d) & (d < c) & (d < e))
            | ((a > b) & (a < c) & (b > d))
        )

        dataframe["pine_hl"] = hl_c
        dataframe["pine_zz"] = zz_d
        dataframe["pine_a"] = a
        dataframe["pine_loc1"] = b
        dataframe["pine_loc2"] = c
        dataframe["pine_loc3"] = d
        dataframe["pine_loc4"] = e
        dataframe["pine_hh"] = _hh.fillna(False)
        dataframe["pine_ll"] = _ll.fillna(False)
        dataframe["pine_hl_signal"] = _hl.fillna(False)
        dataframe["pine_lh"] = _lh.fillna(False)

        # currLowest = ta.lowest(low, lb + 1) ; currHighest = ta.highest(high, lb + 1)
        dataframe["pine_curr_lowest"] = ta.pine_lowest(low, length + 1)
        dataframe["pine_curr_highest"] = ta.pine_highest(high, length + 1)

        # ---- dead for trading, computed as the source computes it ----------
        # res := _lh ? zz : res[1] ; sup := _hl ? zz : sup[1]
        # iff_3 = close < sup ? -1 : nz(trend[1]) ; trend := close > res ? 1 :
        # iff_3 ; then res/sup are re-assigned from trend and the signals, and
        # rechange / suchange are read only by the showsupres display block.
        n = len(dataframe)
        res_out = np.full(n, np.nan)
        sup_out = np.full(n, np.nan)
        trend_out = np.full(n, np.nan)
        rechange_out = np.zeros(n, dtype=bool)
        suchange_out = np.zeros(n, dtype=bool)
        lh_arr = _lh.fillna(False).to_numpy()
        hl_arr = _hl.fillna(False).to_numpy()
        hh_arr = _hh.fillna(False).to_numpy()
        ll_arr = _ll.fillna(False).to_numpy()
        zz_arr = zz_d.to_numpy(dtype=float)
        close_arr = close.to_numpy(dtype=float)
        res_prev = np.nan
        sup_prev = np.nan
        trend_prev = np.nan
        for i in range(n):
            res = zz_arr[i] if lh_arr[i] else res_prev
            sup = zz_arr[i] if hl_arr[i] else sup_prev
            if close_arr[i] < sup:
                iff_3 = -1.0
            else:
                iff_3 = 0.0 if np.isnan(trend_prev) else trend_prev
            trend = 1.0 if close_arr[i] > res else iff_3
            if (trend == 1.0 and hh_arr[i]) or (trend == -1.0 and lh_arr[i]):
                res = zz_arr[i]
            if (trend == 1.0 and hl_arr[i]) or (trend == -1.0 and ll_arr[i]):
                sup = zz_arr[i]
            # res != res[1]: na in either operand makes the comparison na, and
            # na is falsy; the variable is display-only.
            if not np.isnan(res) and not np.isnan(res_prev) and res != res_prev:
                rechange_out[i] = True
            if not np.isnan(sup) and not np.isnan(sup_prev) and sup != sup_prev:
                suchange_out[i] = True
            res_out[i], sup_out[i], trend_out[i] = res, sup, trend
            res_prev, sup_prev, trend_prev = res, sup, trend
        dataframe["pine_res"] = res_out
        dataframe["pine_sup"] = sup_out
        dataframe["pine_trend"] = trend_out
        dataframe["pine_rechange"] = rechange_out
        dataframe["pine_suchange"] = suchange_out

        cutoff_ms = int(pd.Timestamp(str(params["intHasta"]), tz="UTC").value // 10**6)
        dataframe["pine_time_ge_hasta"] = self._time_ge(dataframe, cutoff_ms)
        return dataframe

    def pine_context(self, dataframe, params):
        close_series = dataframe["close"]
        ll_val0 = float(dataframe["low"].iloc[0])
        hh_val0 = float(dataframe["high"].iloc[0])
        return {
            "open": dataframe["open"].to_numpy(dtype=float),
            "high": dataframe["high"].to_numpy(dtype=float),
            "low": dataframe["low"].to_numpy(dtype=float),
            "close": close_series.to_numpy(dtype=float),
            "hh": dataframe["pine_hh"].to_numpy(dtype=bool),
            "ll": dataframe["pine_ll"].to_numpy(dtype=bool),
            "hl": dataframe["pine_hl_signal"].to_numpy(dtype=bool),
            "lh": dataframe["pine_lh"].to_numpy(dtype=bool),
            "a": dataframe["pine_a"].to_numpy(dtype=float),
            "curr_lowest": dataframe["pine_curr_lowest"].to_numpy(dtype=float),
            "curr_highest": dataframe["pine_curr_highest"].to_numpy(dtype=float),
            "time_ge_hasta": dataframe["pine_time_ge_hasta"].to_numpy(dtype=bool),
            "blnLongs": not bool(params["blnShorts"]),
            "blnShorts": bool(params["blnShorts"]),
            "pctRisk": float(params["pctRisk"]),
            "RR": float(params["RR"]),
            "retro": float(params["retro"]),
            "fibSL": float(params["fibSL"]),
            # var initialisers: `close` / `high` / `low` of the FIRST bar.
            "state": {
                "status": 0,
                "entryPrice": float(close_series.iloc[0]),
                "hhVal": hh_val0,
                "lhVal": hh_val0,
                "hlVal": ll_val0,
                "llVal": ll_val0,
                "longTP": hh_val0,
                "longSL": ll_val0,
                "shortTP": ll_val0,
                "shortSL": hh_val0,
                "lowest": ll_val0,
                "highest": hh_val0,
                "closedTrades": 0,
                "currSignal": "",
                "prevSignal": "",     # dead: assigned, never read
                "blnOrder": False,    # dead: assigned, never read
            },
        }

    def pine_script(self, broker, i, ctx):
        st = ctx["state"]
        o = ctx["open"][i]
        h = ctx["high"][i]
        l = ctx["low"][i]
        c = ctx["close"][i]
        _hh = bool(ctx["hh"][i])
        _ll = bool(ctx["ll"][i])
        _hl = bool(ctx["hl"][i])
        _lh = bool(ctx["lh"][i])
        a_val = ctx["a"][i]
        curr_lowest = ctx["curr_lowest"][i]
        curr_highest = ctx["curr_highest"][i]
        bln_longs = ctx["blnLongs"]
        bln_shorts = ctx["blnShorts"]
        retro = ctx["retro"]
        fib_sl = ctx["fibSL"]
        rr = ctx["RR"]

        def fibo(fib_top, fib_low):
            # diff = fibTop - fibLow ; fib50 from status parity ; fib70UP/DW
            diff = fib_top - fib_low
            if st["status"] % 2 == 1:
                fib50 = fib_low + diff * (1.0 - retro / 100.0)
            else:
                fib50 = fib_low + diff * (retro / 100.0)
            return (
                fib50,
                fib_low + diff * (1.0 - fib_sl / 100.0),
                fib_low + diff * (fib_sl / 100.0),
            )

        # blnEnLong = strategy.position_size > 0 ; blnEnShort = ... < 0
        # Read once, at the top of the bar: orders placed on this bar fill next.
        bln_en_long = broker.position_size > 0
        bln_en_short = broker.position_size < 0
        # blnEnTrade = blnEnLong or blnEnShort   (dead)
        _bln_en_trade = bln_en_long or bln_en_short

        # usdCalcRisk = strategy.equity * pctRisk / 100
        # usdRisk = usdCalcRisk > 0 ? usdCalcRisk : 0
        usd_calc_risk = broker.equity * ctx["pctRisk"] / 100.0
        usd_risk = usd_calc_risk if usd_calc_risk > 0 else 0.0
        # blnOrder = strategy.opentrades > 0   (dead: re-assigned to false in
        # statuses 7 and 8, never read)
        st["blnOrder"] = broker.open_trades > 0

        # if _hh / _lh / _hl / _ll: record the level and the signal name.
        if _hh:
            st["hhVal"] = a_val
            st["prevSignal"] = st["currSignal"]
            st["currSignal"] = "HH"
        elif _lh:
            st["lhVal"] = a_val
            st["prevSignal"] = st["currSignal"]
            st["currSignal"] = "LH"
        elif _hl:
            st["hlVal"] = a_val
            st["prevSignal"] = st["currSignal"]
            st["currSignal"] = "HL"
        elif _ll:
            st["llVal"] = a_val
            st["prevSignal"] = st["currSignal"]
            st["currSignal"] = "LL"

        status = st["status"]
        # status 0. Waiting for an LL (longs) or an HH (shorts).
        # `blnFechas` is the literal true.
        if status == 0:
            st["closedTrades"] = broker.closed_trades
            if _ll and bln_longs:
                st["status"] = 1
            elif _hh and bln_shorts:
                st["status"] = 2
        # -------- LONGS --------
        # status 1. Longs. Waiting for a new higher level (HH or LH).
        elif status == 1:
            st["closedTrades"] = broker.closed_trades
            if _hh or _lh:
                st["highest"] = curr_highest
            elif _hl:
                st["lowest"] = curr_lowest
                if h > st["highest"]:
                    st["status"] = 5
                    st["highest"] = h
                    fib50, fib_up, _fib_dw = fibo(st["highest"], st["lowest"])
                    st["entryPrice"] = fib50
                    if l <= st["entryPrice"] and c <= o:
                        st["entryPrice"] = c
                    long_sl = fib_up
                    diff = st["entryPrice"] - long_sl
                    long_tp = st["entryPrice"] + diff * rr
                    lot_size = usd_risk / diff
                    st["longSL"] = long_sl
                    st["longTP"] = long_tp
                    if st["entryPrice"] > long_sl:
                        broker.entry(
                            "? 1", "long", limit=st["entryPrice"], qty=lot_size
                        )
                        broker.exit("lx", "? 1", limit=long_tp, stop=long_sl)
                else:
                    st["status"] = 3
                fib50, _fib_up, _fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
            elif l < st["llVal"]:
                st["status"] = 0
        # status 3. Longs. Waiting for an HL.
        elif status == 3:
            if _hl:
                st["lowest"] = curr_lowest
            if _lh or _ll or l < st["hlVal"]:
                broker.cancel_all()
                st["status"] = 1 if _ll else 0
            elif h > st["highest"]:
                st["status"] = 5
                st["highest"] = h
                fib50, fib_up, _fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
                if l <= st["entryPrice"]:
                    st["entryPrice"] = c
                long_sl = fib_up
                diff = st["entryPrice"] - long_sl
                long_tp = st["entryPrice"] + diff * rr
                lot_size = usd_risk / diff
                st["longSL"] = long_sl
                st["longTP"] = long_tp
                if (not bln_en_long) and st["entryPrice"] > long_sl:
                    broker.cancel_all()
                    broker.entry(
                        "? 3", "long", limit=st["entryPrice"], qty=lot_size
                    )
                    broker.exit("lx", "? 3", limit=long_tp, stop=long_sl)
        # status 5. Longs. Fibo growth, waiting for the level to break.
        elif status == 5:
            if broker.closed_trades > st["closedTrades"]:
                st["status"] = 0
            elif bln_en_long:
                st["status"] = 7
            elif _lh or _ll or l < st["llVal"]:
                broker.cancel_all()
                st["status"] = 1 if _ll else 0
            elif h > st["highest"]:
                st["highest"] = h
                fib50, fib_up, _fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
                long_sl = fib_up
                diff = st["entryPrice"] - long_sl
                long_tp = st["entryPrice"] + diff * rr
                lot_size = usd_risk / diff
                st["longSL"] = long_sl
                st["longTP"] = long_tp
                if (not bln_en_long) and st["entryPrice"] > long_sl:
                    broker.cancel_all()
                    broker.entry(
                        "? 5", "long", limit=st["entryPrice"], qty=lot_size
                    )
                    broker.exit("lx", "? 5", limit=long_tp, stop=long_sl)
        # status 7. Longs. Waiting for the trade to finish.
        elif status == 7:
            st["blnOrder"] = False       # dead: never read
            if not bln_en_long:
                broker.cancel_all()
                if st["currSignal"] == "HH" and bln_shorts:
                    st["status"] = 2
                else:
                    st["status"] = 0
        # -------- SHORTS --------
        # status 2. Shorts. Waiting for a new lower level (LL or HL).
        elif status == 2:
            st["closedTrades"] = broker.closed_trades
            if _ll or _hl:
                st["lowest"] = curr_lowest
            elif _lh:
                st["highest"] = curr_highest
                if l < st["lowest"]:
                    st["status"] = 6
                    st["lowest"] = l
                    fib50, _fib_up, fib_dw = fibo(st["highest"], st["lowest"])
                    st["entryPrice"] = fib50
                    if h >= st["entryPrice"] and c > o:
                        st["entryPrice"] = c
                    short_sl = fib_dw
                    diff = short_sl - st["entryPrice"]
                    short_tp = st["entryPrice"] - diff * rr
                    lot_size = usd_risk / diff
                    st["shortSL"] = short_sl
                    st["shortTP"] = short_tp
                    if st["entryPrice"] < short_sl:
                        broker.entry(
                            "? 2", "short", limit=st["entryPrice"], qty=lot_size
                        )
                        broker.exit("sx", "? 2", limit=short_tp, stop=short_sl)
                else:
                    st["status"] = 4
                fib50, _fib_up, _fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
            elif h > st["hhVal"]:
                st["status"] = 0
        # status 4. Shorts. Waiting for an LH.
        elif status == 4:
            if _lh:
                st["highest"] = curr_highest
            if _hl or _hh or h > st["lhVal"]:
                broker.cancel_all()
                st["status"] = 2 if _hh else 0
            elif l < st["lowest"]:
                st["status"] = 6
                st["lowest"] = l
                fib50, _fib_up, fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
                if h >= st["entryPrice"]:
                    st["entryPrice"] = c
                short_sl = fib_dw
                diff = short_sl - st["entryPrice"]
                short_tp = st["entryPrice"] - diff * rr
                lot_size = usd_risk / diff
                st["shortSL"] = short_sl
                st["shortTP"] = short_tp
                if (not bln_en_short) and st["entryPrice"] < short_sl:
                    broker.cancel_all()
                    broker.entry(
                        "? 4", "short", limit=st["entryPrice"], qty=lot_size
                    )
                    broker.exit("sx", "? 4", limit=short_tp, stop=short_sl)
        # status 6. Shorts. Fibo growth, waiting for the level to break.
        elif status == 6:
            if broker.closed_trades > st["closedTrades"]:
                st["status"] = 0
            elif bln_en_short:
                st["status"] = 8
            elif _hl or _hh or h > st["hhVal"]:
                broker.cancel_all()
                st["status"] = 2 if _hh else 0
            elif l < st["lowest"]:
                st["lowest"] = l
                fib50, _fib_up, fib_dw = fibo(st["highest"], st["lowest"])
                st["entryPrice"] = fib50
                short_sl = fib_dw
                diff = short_sl - st["entryPrice"]
                short_tp = st["entryPrice"] - diff * rr
                lot_size = usd_risk / diff
                st["shortSL"] = short_sl
                st["shortTP"] = short_tp
                if st["entryPrice"] < short_sl:
                    broker.cancel_all()
                    broker.entry(
                        "? 6", "short", limit=st["entryPrice"], qty=lot_size
                    )
                    broker.exit("sx", "? 6", limit=short_tp, stop=short_sl)
        # status 8. Shorts. Waiting for the trade to finish.
        elif status == 8:
            st["blnOrder"] = False       # dead: never read
            if not bln_en_short:
                broker.cancel_all()
                if st["currSignal"] == "LL" and bln_longs:
                    st["status"] = 1
                else:
                    st["status"] = 0

        # exitLong = barstate.isconfirmed and blnEnLong and time >= intHasta
        if ctx["time_ge_hasta"][i] and bln_en_long:
            broker.cancel_all()
            broker.close_all()
            st["status"] = 0
        # exitShort = barstate.isconfirmed and blnEnShort and time >= intHasta
        if ctx["time_ge_hasta"][i] and bln_en_short:
            broker.cancel_all()
            broker.close_all()
            st["status"] = 0
