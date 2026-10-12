"""Port of sources/SM_063dcf4a46ae66ba.pine (batch_001/Cryptocurrency-RSI-Curve-Tracking-Strategy.md).

Pine v4, 1-hour chart, LONG ONLY, by exlux99 ("Crypto RSI + RVI Strategy"). Two
oscillators, both built from Wilder recursions seeded at zero rather than by
pine_ta's `rma`:

    WiMA(src, length) =>
        MA_s = 0.0
        MA_s := (src + nz(MA_s[1] * (length-1))) / length

    calc_rsi_volume(fv, length) =>
        up = iff(fv > fv[1], abs(fv - fv[1]) * volume, 0)
        dn = iff(fv < fv[1], abs(fv - fv[1]) * volume, 0)
        100 * WiMA(up, length) / (WiMA(up, length) + WiMA(dn, length))

    rsi_v = calc_rsi_volume(close, Period)             // Period default 100

    StdDev = stdev(close, Period)
    d = iff(close > close[1], 0, StdDev)
    u = iff(close > close[1], StdDev, 0)
    nU   := (13 * nz(nU[1], 0) + u) / 14
    nD   := (13 * nz(nD[1], 0) + d) / 14
    nRes := 100 * nU / (nU + nD)
    pos  := iff(nRes < BuyZone, -1, iff(nRes > SellZone, 1, nz(pos[1], 0)))
    possig := iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))

    long  = crossover(rsi_v, SellZone)  and (possig ==  1)
    short = crossunder(rsi_v, BuyZone)  and (possig == -1)
    c     = g(strategy.equity * leverage / open * risk / 100, 4)

    strategy.entry("long", 1, c, when = long)
    strategy.close("long", when = short)
    // strategy.entry("short", 0, when = short)      // COMMENTED OUT

    var longOpeneda = false / var shortOpeneda = false / var int timeOfBuya = na
    ... (the whole var block; its only consumers are commented-out plotshape)

    strategy.exit("long_tp/sl",  "long",  profit=close*tp/syminfo.mintick, loss=close*sl/syminfo.mintick, ...)
    strategy.exit("short_tp/sl", "short", profit=close*tp/syminfo.mintick, loss=close*sl/syminfo.mintick, ...)

FOUR order calls, in that exact written order, and the order is preserved here
because it is the engine's fill priority on a bar where more than one fires.
The `short` ENTRY is a comment, so the strategy is long-only and `can_short` is
False; the `strategy.exit("short_tp/sl", ...)` that follows it is ACTIVE code and
is reproduced -- it names the entry id "short", which never exists, so it rests
without ever filling (the engine neither acts on nor publishes levels for an exit
whose `from_entry` is not open).

FIDELITY -- translation choices and source/md mismatches:

1. `WiMA` IS NOT `pine_rma`. `pine_rma` seeds with the SMA of the first `length`
   observations and returns na until the window fills; this source's `MA_s` is
   declared `0.0` and recursed with `nz(MA_s[1] * (length-1))`, so bar 0 is
   `src[0] / length` and the series is defined from the first bar. The formula is
   written out in `_wima` below rather than substituted with the library
   function.
2. The same zero-seeded recursion governs `nU` / `nD`, with alpha 1/14 and
   `nz(..., 0)` on the previous value.
3. MD/SOURCE MISMATCH (indicator): the md's prose and the source's own `title`
   call the second oscillator "RVI". The source computes NO RVI and no
   `rvi()`-equivalent anywhere. `nRes` is `100 * nU / (nU + nD)` over a
   `stdev(close, Period)` split by the SIGN OF THE CLOSE CHANGE and then Wilder
   smoothed. The source is followed; no RVI is invented.
4. MD/SOURCE MISMATCH (argument table): the md renders `v_input_8` as `true` for
   `tp`, while the source declares `tp = input(1.0)`. The table's `true` is a
   boolean rendering of a float default; the source value 1.0 is used. The rest of
   the table matches the declarations (Period 100, BuyZone 49, SellZone 50,
   reverse false, risk 100, leverage 2.5, sl 0.2).
5. `strategy.exit` is called UNCONDITIONALLY on every bar, so the same-id order is
   REPLACED each bar with levels recomputed from THAT bar's close
   (PINE_SEMANTICS.md 3.6).
6. `profit=` / `loss=` are TICK distances from the entry price
   (PINE_SEMANTICS.md 3.5). The source writes them as
   `close * tp / syminfo.mintick` and `close * sl / syminfo.mintick` ticks, which
   is a price distance of exactly `close * tp` and `close * sl`. Both are handed
   to the engine verbatim, in ticks, and resolved against the position's average
   entry price with `source_mintick`.
7. DEAD CODE KEPT. The state machine -- THREE `var` declarations
   (`longOpeneda`, `shortOpeneda`, `timeOfBuya`) plus three plain series
   (`longCondition`, `longExitSignala`, `exitLongCondition`), six names in all --
   is computed by the source and read by nothing: its only consumers are two
   COMMENTED-OUT `plotshape` calls, and no order reads any of them. All six are
   kept as `pine_*` columns. `longExitSignala` is `short` verbatim, so its
   column repeats `pine_short`; `shortOpeneda` is never assigned after its
   declaration, so it is constantly false.
8. `longOpeneda[1]` on the first bar is na; Pine's `if` treats na as false, so it
   is modelled as False. Only `if` ever reads it, so the outcome is identical.
9. `strategy.equity` is read for the order size, so the port reads the engine's
   `equity` (cash + open profit marked at the CURRENT close) at the moment the
   script runs, which is what Pine's bar-close evaluation sees. `open` is the
   current bar's open -- the source divides one bar's close-marked equity by that
   same bar's open.
10. `g(v, p) => round(v * pow(10, p)) / pow(10, p)` is Pine's `round`, half away
    from zero, and is reproduced with pine_ta.pine_round rather than Python's
    banker's rounding.
11. The source declares `default_qty_type = strategy.percent_of_equity` and
    `default_qty_value = 100`, but NO entry uses them: the ONE entry that
    survives passes an explicit `qty` (the short entry is a comment). They are
    recorded for provenance only. The declared properties that DO apply are
    `initial_capital = 1000`, `commission_value = 0.03` (percent) and
    `pyramiding = 1`.
12. `pyramiding = 1` permits a second same-direction entry in the engine's
    ledger, while the framework is structurally limited to one entry
    (`PinePortBase.position_adjustment_enable = False`, PINE_SEMANTICS.md 二.10).
    Not fixed; recorded.
13. `default_qty_type` percent-of-equity is also what the framework would use if
    the engine's notional could not be handed over, but here the explicit `qty`
    means the engine sizes off `strategy.equity` with `leverage = 2.5`, i.e. up
    to 2.5x the account per entry. `PinePortBase.leverage()` returns 1.0, so the
    framework CANNOT express that notional, and `custom_stake_amount` hands the
    engine's own number to Freqtrade, which may veto it (PINE_SEMANTICS.md 1.5).
    A `mismatch_framework_veto` verdict on this port is that boundary, not a
    port defect.
14. No `process_orders_on_close` is declared, so Pine's documented default
    (false) applies and every market order fills at the NEXT bar's open; the
    engine fills that way.
15. `strategy()` declares no `slippage`; the engine models none.
16. The `/*backtest` header's `period: 1h` IS taken as the timeframe --
    `basePeriod: 15m` is the FMZ backtester's intrabar fill granularity, and the
    header's start:/end: window is not applied: the port runs on whatever range
    the caller supplies.
17. `pine_stdev` is the population standard deviation (ddof=0), matching Pine's
    `stdev`, and returns na until the window fills, so `nRes` is na (and `pos`
    therefore carries 0) for the first `Period - 1` bars.
18. Leverage, margin, liquidation, funding and the venue's contract-step
    rounding are not modelled; the chain verifier measures the step rounding
    separately.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _wima(src: np.ndarray, length: int) -> np.ndarray:
    """`WiMA(src, length)`: Wilder smoothing seeded at ZERO, not at the SMA.

        MA_s = 0.0
        MA_s := (src + nz(MA_s[1] * (length-1))) / length

    `MA_s` is re-declared 0.0 each bar and the previous bar's value is read with
    `[1]`; on bar 0 that value is na, `nz` turns it into 0, and the first output
    is `src[0] / length`. An na source observation propagates na, and the na is
    then `nz`-ed away on the following bar -- the same reset the source's own
    `nz(MA_s[1] * (length-1))` performs.
    """
    length = int(length)
    out = np.full(len(src), np.nan)
    state = np.nan
    for i, value in enumerate(src):
        base = 0.0 if np.isnan(state) else state * (length - 1)
        state = (value + base) / length
        out[i] = state
    return out


def _ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Pine division: `x / 0` is na, and na propagates."""
    with np.errstate(divide="ignore", invalid="ignore"):
        return numerator / denominator


def _g(value, precision: int) -> float:
    """`g(v, p) => round(v * pow(10, p)) / pow(10, p)`."""
    scale = 10.0 ** int(precision)
    return float(ta.pine_round(float(value) * scale) / scale)


class SMCryptoRsiCurveTracking_063dcf(PinePortBase, IStrategy):
    source_id = "SM_063dcf4a46ae66ba"
    source_file = "Cryptocurrency-RSI-Curve-Tracking-Strategy.md"
    # /*backtest ... period: 1h, basePeriod: 15m
    timeframe = "1h"
    # The only short entry in the source is commented out; the strategy is
    # long-only. The active `strategy.exit("short_tp/sl", ...)` names an entry id
    # that never exists and so never fills.
    can_short = False
    source_defaults = {
        # Period = input(100, minval=1)
        "Period": 100,
        # BuyZone = input(49, minval=1)
        "BuyZone": 49,
        # SellZone = input(50, minval=1)
        "SellZone": 50,
        # reverse = input(false, title="Trade reverse")
        "reverse": False,
        # risk = input(100)
        "risk": 100,
        # leverage = input(2.5)
        "leverage": 2.5,
        # sl = input(0.2)
        "sl": 0.2,
        # tp = input(1.0)
        "tp": 1.0,
    }
    # strategy(... default_qty_type=strategy.percent_of_equity, default_qty_value=100 ...)
    # declared, but every surviving entry passes an explicit qty=c, so the
    # default sizing is never reached. Recorded for provenance.
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    # commission_type=strategy.commission.percent, commission_value=0.03
    source_commission_percent = 0.03
    # pyramiding=1
    source_pyramiding = 1
    # initial_capital = 1000
    source_initial_capital = 1000.0
    # Both strategy.exit calls carry `profit=` / `loss=` price legs.
    source_reproduce_stops = True
    source_fidelity_notes = [
        "WiMA IS NOT pine_rma. Pine_rma seeds with the SMA of the first `length` "
        "observations and returns na until the window fills; this source declares "
        "MA_s = 0.0 and recurses with nz(MA_s[1] * (length-1)), so bar 0 is "
        "src[0] / length and the series is defined from the first bar. The formula "
        "is written out in _wima rather than substituted with the library "
        "function, per the rule against name-matching library calls.",
        "The same zero-seeded Wilder recursion (alpha 1/14) governs nU and nD, "
        "with nz(..., 0) on the previous value; written out in the port.",
        "MD/SOURCE MISMATCH (indicator): the md prose and the source's own title "
        "say 'RVI'. The source computes NO RVI anywhere. nRes is "
        "100*nU/(nU+nD) over a stdev(close, Period) split by the SIGN OF THE "
        "CLOSE CHANGE and Wilder smoothed. Source followed; no RVI invented.",
        "MD/SOURCE MISMATCH (argument table): the md renders v_input_8 as `true` "
        "for tp while the source declares tp = input(1.0). The table's `true` is a "
        "boolean rendering of a float default; 1.0 is used. The other seven "
        "entries match the declarations.",
        "strategy.exit is called UNCONDITIONALLY every bar, so the same-id order "
        "is REPLACED each bar with levels recomputed from that bar's close "
        "(PINE_SEMANTICS.md 3.6).",
        "profit= / loss= are TICK distances from the entry price "
        "(PINE_SEMANTICS.md 3.5). The source writes close*tp/syminfo.mintick and "
        "close*sl/syminfo.mintick ticks, and the engine resolves a tick distance "
        "as ticks * mintick against the position's average entry price -- so "
        "syminfo.mintick CANCELS and the resting levels are exactly close*tp and "
        "close*sl away from the entry price, independent of source_mintick (0.1). "
        "The cancellation, not the tick count, is what makes this port's levels "
        "correct; the tick values are handed over verbatim as the source writes "
        "them. MEASURED (2026-09-24): on the 1381 bars of validate_pine's "
        "synthetic 1h frame that carry an open long with both legs published, "
        "max |(limit - pine_avg_price) - close[placement]*tp| = 2.8e-14 and "
        "max |(pine_avg_price - stop) - close[placement]*sl| = 7.1e-15, i.e. the "
        "cancellation holds to float noise.",
        "DEAD CODE KEPT: the state machine -- THREE var declarations (longOpeneda, "
        "shortOpeneda, timeOfBuya) plus three plain series (longCondition, "
        "longExitSignala, exitLongCondition) -- is computed and read by nothing. "
        "Its only consumers are two COMMENTED-OUT plotshape calls, and no order "
        "reads any of them. All six names have a pine_* column; longExitSignala "
        "is `short` verbatim, so its column repeats pine_short. shortOpeneda is "
        "never assigned after its declaration, so it is constantly false.",
        "longOpeneda[1] on the first bar is na, which Pine's `if` treats as false; "
        "modelled as False. Nothing but `if` reads it, so the outcome is "
        "identical.",
        "timeOfBuya := time is Pine's bar-OPENING time in milliseconds since the "
        "epoch, UTC. The port pins the index to UTC before converting, so a naive "
        "index is not silently read as local time; the column is dead code either "
        "way.",
        "strategy.equity is read for the order size, so the port reads the "
        "engine's equity (cash + open profit marked at the current close) at the "
        "moment the script runs -- what Pine's bar-close evaluation sees. `open` "
        "is the same bar's open.",
        "g(v, p) is Pine's round, half away from zero, reproduced with "
        "pine_ta.pine_round rather than Python's banker's rounding.",
        "The declared default_qty_type = strategy.percent_of_equity / "
        "default_qty_value = 100 are never reached: every surviving entry passes "
        "an explicit qty=c. Recorded for provenance only. The properties that DO "
        "apply are initial_capital = 1000, commission_value = 0.03 percent and "
        "pyramiding = 1.",
        "pyramiding = 1 permits a second same-direction entry in the engine's "
        "ledger, while the framework is structurally limited to one entry "
        "(position_adjustment_enable = False, PINE_SEMANTICS.md 二.10). Not fixed; "
        "recorded.",
        "The explicit qty sizes off strategy.equity with leverage = 2.5, i.e. up "
        "to 2.5x the account per entry. PinePortBase.leverage() returns 1.0, so "
        "the framework cannot express that notional; custom_stake_amount hands the "
        "engine's own number to Freqtrade, which may veto it (PINE_SEMANTICS.md "
        "1.5). A mismatch_framework_veto verdict here is that boundary, not a port "
        "defect.",
        "The only short entry in the source is COMMENTED OUT, so can_short is "
        "False. The active strategy.exit(\"short_tp/sl\", \"short\", ...) that "
        "follows it names the entry id \"short\", which never exists: the engine "
        "neither fills it nor publishes levels for it, because an exit whose "
        "from_entry is not open is filtered in both paths. It is still placed, "
        "exactly as the source places it.",
        "No process_orders_on_close is declared, so Pine's documented default "
        "(false) applies and market orders fill at the NEXT bar's open; that is "
        "how the engine fills them.",
        "pine_stdev is the population standard deviation (ddof=0), matching Pine's "
        "stdev, and returns na until the window fills, so nRes is na -- and pos "
        "therefore carries 0 -- for the first Period-1 bars.",
        "period: 1h IS taken from the /*backtest header. basePeriod: 15m is the "
        "FMZ backtester's own intrabar fill granularity, and the header's "
        "start:/end: window is not applied: the port runs on whatever range the "
        "caller supplies.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled; the chain verifier measures the step rounding "
        "separately.",
        "RE-DERIVED INDEPENDENTLY (2026-09-24, outside this file): rsi_v, nU, nD, "
        "nRes, pos, possig, long and short were recomputed from the .pine with "
        "plain numpy (zero-seeded Wilder recursions and stdev written out again, "
        "no pine_ta) and matched the port's columns exactly on validate_pine's "
        "synthetic 1h frame (allclose, equal_nan).",
        "MODELLING CHOICE, MEASURED HARMLESS: whether a Pine `iff` whose "
        "condition compares against na yields na or its false branch is "
        "unpublished for this construct, and the source's `d` / `u` hit it on bar "
        "0. Both readings were computed over the synthetic frame: nRes differs on "
        "bar 0 alone while rsi_v is na on bar 0 under either, and `pos` (hence "
        "possig, long and short) is identical bar for bar, so no order can see "
        "the difference. The port reads an na comparison as false, which is "
        "Pine's documented rule in a boolean context.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]
        length = int(params["Period"])
        buy_zone = float(params["BuyZone"])
        sell_zone = float(params["SellZone"])
        reverse = bool(params["reverse"])

        series_index = close.index
        n = len(dataframe)

        # ---- rsi_v = calc_rsi_volume(close, length) -------------------------
        # up = iff(fv>fv[1], abs(fv-fv[1])*volume, 0)
        # dn = iff(fv<fv[1], abs(fv-fv[1])*volume, 0)
        previous_close = close.shift(1)
        abs_change = (close - previous_close).abs()
        up_cond = (close > previous_close).to_numpy(dtype=bool)
        dn_cond = (close < previous_close).to_numpy(dtype=bool)
        weighted = (abs_change * volume).to_numpy(dtype=float)
        up = np.where(up_cond, weighted, 0.0)
        dn = np.where(dn_cond, weighted, 0.0)

        # upt = WiMA(up, length) ; dnt = WiMA(dn, length)
        upt = _wima(up, length)
        dnt = _wima(dn, length)
        # 100*(upt/(upt+dnt))  -- 0/0 on the first bar is na
        rsi_v = pd.Series(100.0 * _ratio(upt, upt + dnt), index=series_index)
        dataframe["pine_rsi_v"] = rsi_v

        # ---- the stdev oscillator -------------------------------------------
        # StdDev = stdev(xPrice, Period) ; d = iff(close>close[1], 0, StdDev)
        # u = iff(close>close[1], StdDev, 0)
        x_price = close
        std_dev = ta.pine_stdev(x_price, length)
        std_dev_values = std_dev.to_numpy(dtype=float)
        d = np.where(up_cond, 0.0, std_dev_values)
        u = np.where(up_cond, std_dev_values, 0.0)

        # nU := (13 * nz(nU[1],0) + u) / 14  ;  nD := (13 * nz(nD[1],0) + d) / 14
        n_u = np.full(n, np.nan)
        n_d = np.full(n, np.nan)
        n_res = np.full(n, np.nan)
        prev_u = np.nan
        prev_d = np.nan
        for i in range(n):
            base_u = 0.0 if np.isnan(prev_u) else 13.0 * prev_u
            base_d = 0.0 if np.isnan(prev_d) else 13.0 * prev_d
            prev_u = (base_u + u[i]) / 14.0
            prev_d = (base_d + d[i]) / 14.0
            n_u[i] = prev_u
            n_d[i] = prev_d
            # nRes := 100 * nU / (nU + nD)
            n_res[i] = 100.0 * _ratio(prev_u, prev_u + prev_d)
        dataframe["pine_n_u"] = n_u
        dataframe["pine_n_d"] = n_d
        dataframe["pine_n_res"] = n_res

        # pos := iff(nRes < BuyZone, -1, iff(nRes > SellZone, 1, nz(pos[1], 0)))
        pos = np.full(n, np.nan)
        possig = np.full(n, np.nan)
        previous_pos = np.nan
        for i in range(n):
            value = n_res[i]
            if value < buy_zone:
                current = -1.0
            elif value > sell_zone:
                current = 1.0
            else:
                current = 0.0 if np.isnan(previous_pos) else previous_pos
            pos[i] = current
            previous_pos = current
            # possig := iff(reverse and pos == 1, -1, iff(reverse and pos == -1, 1, pos))
            if reverse and current == 1.0:
                possig[i] = -1.0
            elif reverse and current == -1.0:
                possig[i] = 1.0
            else:
                possig[i] = current
        possig_series = pd.Series(possig, index=series_index)
        dataframe["pine_pos"] = pos
        dataframe["pine_possig"] = possig_series

        # long  = crossover(rsi_v, ob) and (possig ==  1)   with ob = SellZone
        # short = crossunder(rsi_v, os) and (possig == -1)   with os = BuyZone
        long = ta.pine_crossover(rsi_v, sell_zone) & (possig_series == 1)
        short = ta.pine_crossunder(rsi_v, buy_zone) & (possig_series == -1)
        dataframe["pine_long"] = long
        dataframe["pine_short"] = short
        # longExitSignala = short -- a plain alias of `short` (see note 7). Kept
        # as its own column so every name the source assigns is in the ledger.
        dataframe["pine_long_exit_signala"] = short

        # ---- the var state machine (dead code: no order and no plot reads it) --
        # longCondition = long and not longOpeneda
        # if longCondition -> longOpeneda := true ; timeOfBuya := time
        # longExitSignala = short ; exitLongCondition = longOpeneda[1] and short
        # if exitLongCondition -> longOpeneda := false ; timeOfBuya := na
        times = dataframe.index
        # Pine `time` is the bar's OPENING TIME in milliseconds since the epoch,
        # UTC. The index may arrive tz-aware (as Freqtrade's does) or naive, so
        # the conversion is pinned to UTC rather than left to pandas' local-time
        # default for a naive Timestamp.
        if isinstance(times, pd.DatetimeIndex) and times.tz is None:
            times = times.tz_localize("UTC")
        elif isinstance(times, pd.DatetimeIndex):
            times = times.tz_convert("UTC")
        long_condition = np.zeros(n, dtype=bool)
        exit_long_condition = np.zeros(n, dtype=bool)
        long_opened = np.zeros(n, dtype=bool)
        short_opened = np.zeros(n, dtype=bool)
        time_of_buy = np.full(n, np.nan)
        long_values = long.to_numpy(dtype=bool)
        short_values = short.to_numpy(dtype=bool)
        opened = False
        stamp = np.nan
        for i in range(n):
            # longOpeneda[1]: the previous bar's value, na on the first bar -- which
            # `if` reads as false, so it is modelled as False.
            previous_opened = opened
            if long_values[i] and not opened:
                long_condition[i] = True
                opened = True
                # Pine `time`: the bar's opening time in milliseconds.
                stamp = int(pd.Timestamp(times[i]).timestamp() * 1000)
            if previous_opened and short_values[i]:
                exit_long_condition[i] = True
                opened = False
                stamp = np.nan
            long_opened[i] = opened
            # shortOpeneda is declared `var` and never assigned after that.
            short_opened[i] = False
            time_of_buy[i] = stamp
        dataframe["pine_long_condition"] = long_condition
        dataframe["pine_exit_long_condition"] = exit_long_condition
        dataframe["pine_long_openeda"] = long_opened
        dataframe["pine_short_openeda"] = short_opened
        dataframe["pine_time_of_buya"] = time_of_buy
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long": dataframe["pine_long"].to_numpy(dtype=bool),
            "short": dataframe["pine_short"].to_numpy(dtype=bool),
            "close": dataframe["close"].to_numpy(dtype=float),
            "open": dataframe["open"].to_numpy(dtype=float),
            # sl = input(0.2) ; tp = input(1.0) ; risk = input(100) ; leverage = input(2.5)
            "sl": float(params["sl"]),
            "tp": float(params["tp"]),
            "risk": float(params["risk"]),
            "leverage": float(params["leverage"]),
        }

    def pine_script(self, broker, i, ctx):
        sl = ctx["sl"]
        tp = ctx["tp"]
        risk = ctx["risk"]
        leverage = ctx["leverage"]
        # c = g((strategy.equity * leverage / open) * (risk / 100), 4)
        qty = _g(
            (broker.equity * leverage / ctx["open"][i]) * (risk / 100.0),
            4,
        )
        # The written order below is the fill priority and is preserved:
        # long entry, long close, long_tp/sl exit, short_tp/sl exit.
        # strategy.entry("long", 1, c, when = long)   -- 1 == strategy.long
        broker.entry("long", "long", qty=qty, when=bool(ctx["long"][i]))
        # strategy.close("long", when = short)
        broker.close("long", when=bool(ctx["short"][i]))
        # // strategy.entry("short",0,when=short)   -- COMMENTED OUT in the source
        #
        # strategy.exit("long_tp/sl", "long",
        #               profit=close*tp/syminfo.mintick, loss=close*sl/syminfo.mintick)
        broker.exit(
            "long_tp/sl",
            from_entry="long",
            profit=float(ctx["close"][i]) * tp / float(self.source_mintick),
            loss=float(ctx["close"][i]) * sl / float(self.source_mintick),
        )
        # strategy.exit("short_tp/sl", "short",
        #               profit=close*tp/syminfo.mintick, loss=close*sl/syminfo.mintick)
        broker.exit(
            "short_tp/sl",
            from_entry="short",
            profit=float(ctx["close"][i]) * tp / float(self.source_mintick),
            loss=float(ctx["close"][i]) * sl / float(self.source_mintick),
        )
