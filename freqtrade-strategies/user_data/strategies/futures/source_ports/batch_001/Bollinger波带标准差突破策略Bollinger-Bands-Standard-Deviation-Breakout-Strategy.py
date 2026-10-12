"""Port of sources/SM_24a1d486ca18a1fb.pine
(batch_001/Bollinger波带标准差突破策略Bollinger-Bands-Standard-Deviation-Breakout-Strategy.md).

Pine v4, TradeChartist's "Bollinger Bands Filter" with an FMZ backtest window
bolted on. A 55-period SMA basis with a ONE-standard-deviation envelope (not
the classic two), plus a `barssince` race between the two breakout conditions:

    src   = input(close, title = "Source")
    length= input(55, minval=1, title = "SMA length")
    mult  = input(1., minval=0.236, maxval=2, title = "Standard Deviation")
    basis = sma(src, length)
    dev   = mult * stdev(src, length)
    upper = basis + dev
    lower = basis - dev
    short = src < lower
    long  = src > upper
    L1    = barssince(long)
    S1    = barssince(short)
    longSignal  = L1 < S1 and not (L1 < S1)[1]
    shortSignal = S1 < L1 and not (S1 < L1)[1]

    start = timestamp(FromYear, FromMonth, FromDay, 00, 00)
    finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
    window() => time >= start and time <= finish ? true : false

    if window()
        strategy.entry("Long",  long = true,  when = longSignal)
    if window()
        strategy.entry("Short", long = false, when = shortSignal)

`longSignal` is not "the price broke the upper band": it is the EDGE of the
`barssince(long) < barssince(short)` state, i.e. the bar on which the long
side becomes the more recent of the two breakouts.

`strategy(title=..., shorttitle="BB Breakout Strategy", overlay=true,
pyramiding=1, currency=currency.NONE, initial_capital=10000,
default_qty_type=strategy.percent_of_equity, default_qty_value=100,
calc_on_every_tick=true, process_orders_on_close=false)` names no
commission_type/commission_value and no slippage, so Pine's defaults apply:
commission 0%, slippage 0.

The `/*backtest` header declares `period: 1m` on Futures_Binance BTC_USDT, so
`timeframe` is "1m"; `basePeriod: 1m` is the FMZ backtester's own filling
granularity. There is no local 1m BTC history, so `verify_chain` reports
`skipped_no_local_data` for this port -- see source_fidelity_notes.

DEAD CODE, KEPT: `bcol` is computed and read only by `barcolor` (a plot), and
`Notestart1` is a declared input that is never read (measured: the name occurs
only on its own `input()` line). `bcol` is display-only and is not reproduced,
following this batch's precedent; `Notestart1` stays in `source_defaults`.

FIDELITY: see source_fidelity_notes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _na_shift(values: np.ndarray) -> np.ndarray:
    """`x[1]` for a float array that may hold na, seeded with na on bar 0."""
    out = np.full(len(values), np.nan)
    if len(values) > 1:
        out[1:] = values[:-1]
    return out


class SMBollingerBandsStdDevBreakout_24a1d4(PinePortBase, IStrategy):
    source_id = "SM_24a1d486ca18a1fb"
    source_file = "Bollinger波带标准差突破策略Bollinger-Bands-Standard-Deviation-Breakout-Strategy.md"
    timeframe = "1m"
    can_short = True
    source_defaults: dict = {
        "src": "close",
        "length": 55,
        "mult": 1.0,
        "CC": True,
        "Notestart1": True,
        "FromMonth": 1,
        "FromDay": 1,
        "FromYear": 2018,
        "ToMonth": 1,
        "ToDay": 1,
        "ToYear": 9999,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 1
    source_initial_capital = 10_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`timeframe` is taken from the source's `/*backtest` header (`period: "
        "1m`, Futures_Binance BTC_USDT). The header's `basePeriod: 1m` is the "
        "FMZ backtester's own fill granularity. There is no 1m BTC/USDT:USDT "
        "series in the local OKX store, and `verify_chain.py` only loads from "
        "its LOCAL_TIMEFRAMES set, so this port cannot be chain-verified here. "
        "The timeframe is the source's; it is not changed to make the check "
        "runnable.",
        "`strategy(...)` declares no commission_type/commission_value and no "
        "slippage, so commission is Pine's default 0% and slippage 0. "
        "`initial_capital = 10000`, `default_qty_type = "
        "strategy.percent_of_equity`, `default_qty_value = 100`, `pyramiding = "
        "1`, `calc_on_every_tick = true`, `process_orders_on_close = false`.",
        "`calc_on_every_tick = true` is NOT modelled: the shared engine "
        "evaluates the script once per bar at the bar's close and fills market "
        "orders at the next bar's open (PINE_SEMANTICS.md section 一). On a "
        "real-time chart `calc_on_every_tick` makes the script re-evaluate "
        "within the bar, which can change when an order is placed and at what "
        "price. The offline engine has no ticks; this is recorded, not "
        "reproduced.",
        "`stdev(src, length)` is `pine_ta.pine_stdev`, the POPULATION standard "
        "deviation (ddof = 0) over the last `length` bars, which is what Pine's "
        "ta.stdev computes -- not the sample deviation a same-named library "
        "function would give.",
        "`barssince` is `pine_ta.pine_barssince`: the number of bars since the "
        "condition was last true, na until it has ever been true. The source's "
        "`long` / `short` conditions are na during warmup (the basis is na) "
        "rather than false; na is not true, so it neither resets nor advances "
        "the count differently from false, and the shared function's "
        "`fillna(False)` cast is equivalent here.",
        "THREE-VALUED na LOGIC IS MODELLED EXPLICITLY. `longSignal` is `L1 < S1 "
        "and not (L1 < S1)[1]`, and Pine's `not`/`and` propagate na (an na "
        "operand yields na, and na is a FALSE condition). The second term is "
        "therefore true only on a bar whose PREVIOUS bar had a defined, false "
        "`L1 < S1`; treating na as false and then negating it would make the "
        "signal fire one bar earlier in exactly the cases where the previous "
        "bar was undefined, which is the silent-inversion shape "
        "PINE_SEMANTICS.md 1.16 warns about. MEASURED on the validate_pine "
        "synthetic frame (3000 bars): `L1 < S1` is true on 1471 bars and its "
        "previous-bar value is na on 0 of them, so this port's reading and the "
        "na-as-false reading produce the same signal series there (24 long "
        "signals either way, bitwise identical); the distinction is still "
        "modelled the Pine way, because the synthetic frame is not the source's "
        "instrument.",
        "`window()` is `time >= start and time <= finish` with `start = "
        "timestamp(2018, 1, 1, 00, 00)` and `finish = timestamp(9999, 1, 1, 23, "
        "59)`. Pine's `timestamp()` reads its arguments in the EXCHANGE's "
        "timezone (UTC for Binance) and `time` is the bar's opening time, so "
        "the port compares the bar's own opening time against those two "
        "instants -- no offset and no interval-overlap. MEASURED: the "
        "predicate is true on every bar of the validate_pine synthetic frame "
        "(which starts 2019-01-01) and of the local 4h and 1d BTC series, so "
        "the window never gates an order away on any data this project can "
        "load. `finish` in year 9999 exceeds what this pandas version can "
        "convert to nanoseconds (`Timestamp.value` overflows), but the "
        "comparison itself is legal and was measured, not assumed.",
        "`barssince` warm-up is na propagation and nothing else: with length = "
        "55 the basis is na on bars 0..54, so both conditions are false there, "
        "both counts stay na, and `L1 < S1` is na (a false condition) until "
        "one of the two breakouts has actually happened. MEASURED on the "
        "validate_pine synthetic frame (3000 bars): `L1` is first defined on "
        "bar 54 and `S1` on bar 116 (the first bar at which `src < lower` is "
        "true), the first `longSignal` is on bar 294 and the first "
        "`shortSignal` on bar 387, and there are 24 of each over the frame.",
        "MEASURED on local BTC/USDT:USDT series (NOT the source's timeframe -- "
        "the source's 1m history is absent locally, so this is a smoke test "
        "that the signal path runs, not a reproduction): on 4h (14815 bars) "
        "132 `longSignal` / 131 `shortSignal`, `L1` first defined on bar 80; "
        "on 1d (2453 bars) 21 / 21, `L1` first defined on bar 119.",
        "`strategy.entry` is passed no `qty`, so the order size is the "
        "strategy's default (`percent_of_equity`, 100). No `strategy.exit` / "
        "`close` / stop / limit / trail call exists anywhere, so a position "
        "ends only when an opposing entry reverses it, and `source_reproduce_"
        "stops` is False.",
        "`pyramiding = 1`: entries in the same direction stack rather than "
        "replace (the engine's `_can_add` allows `open_same <= pyramiding`, "
        "i.e. two entries in one direction; PINE_SEMANTICS.md 2.10 records "
        "pyramiding as an area that needs `position_adjustment` and is not "
        "modelled by the framework side).",
        "`bcol = src > upper ? ... : src < lower ? ... : na` is computed and "
        "read only by `barcolor(CC ? bcol : na, ...)`, and `CC` is read only "
        "there: display only, not reproduced. `Notestart1 = input(true, ...)` "
        "is a divider in the inputs dialog and is never read (measured: the "
        "name occurs only on its own line).",
        "md vs source, PROSE, recorded not followed: the md's Strategy "
        "Description says the strategy 'goes long when the price closes above "
        "the upper band and goes short when the price closes below the lower "
        "band'. The SOURCE's condition is not that. `src > upper` is only the "
        "`long` state variable; the entry condition is the EDGE of the "
        "`barssince(long) < barssince(short)` race, which is a narrower and "
        "different set of bars (measured: on the synthetic frame the race "
        "holds on 1471 bars but only 24 of them are signal edges; on local 4h, "
        "132 signal edges over 14815 bars). The prose also never mentions "
        "the backtest time window, which the code does have as a filter (it "
        "is simply always true, given the declared dates). The code is the "
        "authority; the port follows it.",
        "md vs source, recorded not followed. The md's argument table disagrees "
        "with the SOURCE at exactly three places, all of them its exporter "
        "flattening a literal to `true` or `0`: (a) `v_input_1_close` shows "
        "default `0` where the source writes `input(close, ...)`; (b) "
        "`v_input_3` (Standard Deviation) shows `true` where the source writes "
        "`input(1., ...)`, the float literal `1.`; (c) `v_input_6` (From "
        "Month), `v_input_7` (From Day), `v_input_9` (To Month) and "
        "`v_input_10` (To Day) show `true` where the source writes "
        "`input(defval=1, ...)`. Everything else in the table agrees "
        "(`v_input_2` 55, `v_input_4` true, `v_input_8` 2018, `v_input_11` "
        "9999, `v_input_5` the divider `Notestart1` true). The port takes the "
        "SOURCE's values: `close`, 1.0, 1, 1, 1, 1. Cross-checked mechanically: "
        "check_source_defaults reports 11 source inputs, 11 port defaults, 0 "
        "mismatched, 0 missing, 0 extra, and lists only `src` as unparsed (its "
        "default is the identifier `close`, which is not a literal).",
        "CHAIN VERDICT, MEASURED: the chain verifier returns exactly "
        "`{\"status\": \"skipped_no_local_data\", \"timeframe\": \"1m\"}` for "
        "this port -- there is no 1m BTC/USDT:USDT series in the local store "
        "and the verifier loads only its LOCAL_TIMEFRAMES, so this port has NO "
        "chain verdict on its own timeframe. `validate_pine` does run it "
        "(load / synthetic run / causal-prefix recompute all pass) and books "
        "47 engine trades with 1 entry still open on the synthetic frame; "
        "that is a load-and-run check, not a fidelity check.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 2.4 / 1.6), so the "
        "framework and the engine can differ by a rounded quantity. That is "
        "measured separately by the chain verifier.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        src = ta.pine_source(dataframe, str(params["src"]))
        length = int(params["length"])
        mult = float(params["mult"])

        basis = ta.pine_sma(src, length)
        # stdev(src, length): Pine's population standard deviation.
        dev = mult * ta.pine_stdev(src, length)
        upper = basis + dev
        lower = basis - dev

        # short = src < lower ; long = src > upper. na comparisons are false.
        short_cond = src < lower
        long_cond = src > upper

        l1 = ta.pine_barssince(long_cond).to_numpy(dtype=float)
        s1 = ta.pine_barssince(short_cond).to_numpy(dtype=float)

        # L1 < S1, carried as a three-valued quantity: na when either side is
        # na, exactly as Pine's comparison is.
        undefined = np.isnan(l1) | np.isnan(s1)
        less = np.where(undefined, np.nan, (l1 < s1).astype(float))
        greater = np.where(undefined, np.nan, (s1 < l1).astype(float))

        less_prev = _na_shift(less)
        greater_prev = _na_shift(greater)

        # `not x` is na when x is na, and na is a false condition, so the
        # negated history term is true only where the previous bar's value was
        # DEFINED and false. `and` is true only when both operands are true.
        long_signal = (less == 1.0) & (less_prev == 0.0)
        short_signal = (greater == 1.0) & (greater_prev == 0.0)

        # === INPUT BACKTEST RANGE ===
        # start = timestamp(FromYear, FromMonth, FromDay, 00, 00)
        # finish = timestamp(ToYear, ToMonth, ToDay, 23, 59)
        # window() => time >= start and time <= finish ? true : false
        # `time` is the bar's OPENING time, in the exchange's timezone (UTC for
        # Binance); the frame's index is that same instant.
        index = dataframe.index
        tz = getattr(index, "tz", None)
        start = pd.Timestamp(
            int(params["FromYear"]), int(params["FromMonth"]), int(params["FromDay"]),
            0, 0, tz="UTC" if tz is not None else None,
        )
        finish = pd.Timestamp(
            int(params["ToYear"]), int(params["ToMonth"]), int(params["ToDay"]),
            23, 59, tz="UTC" if tz is not None else None,
        )
        in_window = (index >= start) & (index <= finish)

        # bcol = src > upper ? ... : src < lower ? ... : src > basis ? ... : na
        # is read only by barcolor(CC ? bcol : na, ...): display only.

        dataframe["pine_basis"] = basis
        dataframe["pine_dev"] = dev
        dataframe["pine_upper"] = upper
        dataframe["pine_lower"] = lower
        dataframe["pine_long"] = long_cond
        dataframe["pine_short"] = short_cond
        dataframe["pine_l1"] = l1
        dataframe["pine_s1"] = s1
        dataframe["pine_long_signal"] = long_signal
        dataframe["pine_short_signal"] = short_signal
        dataframe["pine_in_window"] = in_window
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "in_window": dataframe["pine_in_window"].to_numpy(dtype=bool),
            "long_signal": dataframe["pine_long_signal"].to_numpy(dtype=bool),
            "short_signal": dataframe["pine_short_signal"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if (window())
        #     strategy.entry("Long", long = true, when = longSignal)
        if ctx["in_window"][i]:
            broker.entry("Long", "long", when=bool(ctx["long_signal"][i]))
        # if (window())
        #     strategy.entry("Short", long = false, when = shortSignal)
        if ctx["in_window"][i]:
            broker.entry("Short", "short", when=bool(ctx["short_signal"][i]))
