"""Port of sources/SM_5378740f236b8386.pine (batch_001/Eleven-Moving-Averages-Crossover-Strategy十一条移动平均线组合交叉策略.md).

Pine v3. `strategy(title = "[STRATEGY] MA Cross Eleven", overlay = true)`
declares no sizing, no commission and no pyramiding, so all three stay at Pine's
documented defaults (fixed / 1 contract, 0%, pyramiding 0).

The indicator is a crossover of two moving averages whose FORMULA is selected by
an input string (default "ZEMA"):

    ma_1 = variant(type, close, len1)      len1 = 8
    ma_2 = variant(type, close, len2)      len2 = 21
    longCond  = crossover(ma_1, ma_2)
    shortCond = crossunder(ma_1, ma_2)

`variant` implements eleven formulas; `_ma_variant` below reproduces every one
of them (SMA / EMA / WMA / VWMA / SMMA / DEMA / TEMA / Hull / TMA / SSMA / ZEMA)
so that overriding `type` stays faithful. Pine evaluates all eleven `vN` each
bar and returns exactly one of them; they are pure and cannot affect each other,
so evaluating only the selected one returns the identical series while skipping
the other ten.

ZEMA (the default) is `v10 = v2 + (v2 - ema(v2, len))` with `v2 = ema(src, len)`
-- a zero-lag EMA. That is NOT `ta.ema`, so it is written out explicitly rather
than mapped onto a same-named library function (iron rule 3).

A pyramiding counter gates the signals:

    sectionLongs  = 0 ; sectionLongs  := nz(sectionLongs[1])
    sectionShorts = 0 ; sectionShorts := nz(sectionShorts[1])
    if longCond:  sectionLongs += 1 ; sectionShorts = 0
    if shortCond: sectionLongs  = 0 ; sectionShorts += 1
    longCondition  = longCond  and sectionLongs  <= pyrl      pyrl = 1
    shortCondition = shortCond and sectionShorts <= pyrl

The counters carry across bars (a bare global in Pine is re-seeded to 0 and then
immediately overwritten with its own previous value), so they are rebuilt here
as series with an explicit loop -- they depend only on the two cross series, not
on broker state.

The exits are gated off by their own input defaults:

    isTPl = false, isTPs = false, isSLl = false, isSLs = false
    long_tp  = isTPl and ...      long_sl  = isSLl and ...
    strategy.close("long",  when = long_sl  or long_tp)    -> never fires
    strategy.close("short", when = short_sl or short_tp)   -> never fires

The conditions themselves are still computed faithfully from `tpl`, `tps` and
`sl` (percentages -- `(1 + pct/100)`, not ticks, so PINE_SEMANTICS.md 3.5 does
not apply), together with `last_open_longCondition` / `last_open_shortCondition`
(carried forward from `high[1]` / `low[1]` at each signal) and
`in_longCondition` / `in_shortCondition` (which of the two signal timestamps is
later). With the default booleans all four products are false on every bar.

The entry oddity of this source is kept verbatim: the long entry is a STOP
order, and its stop price is the PREVIOUS bar's open --

    strategy.entry("long",  strategy.long,  when = longCondition, stop = open[1])
    strategy.entry("short", strategy.short, when = shortCondition)

`strategy.entry` with `stop = na` places no order in Pine, so bar 0 (whose
`open[1]` is na) is skipped rather than handed a NaN stop.

FIDELITY:

* The long entry is a RESTING STOP order, and a stop entry is precisely the
  shape PINE_SEMANTICS.md section 2 item 11 records as unreachable through the
  Freqtrade interface: the engine fills it on whatever later bar first touches
  the level, while the signal projection can only emit an `enter_long` on the
  bar the order was placed, which the framework fills at the next open. The
  engine side is faithful; the framework side is a documented framework
  boundary, not a defect this port can close.
* PINE_SEMANTICS.md 1.12 (still open) notes that the engine REPLACES a resting
  `exit` order with the same id but ACCUMULATES `stop` / `limit` ENTRY orders
  with the same id, where Pine would replace them. This source re-issues its
  `"long"` stop entry on every signal, so it sits on that open question. Not
  worked around: changing it would change the resting order set.
* `strategy.entry("short", ...)` is a market entry and behaves as usual.
* `HullMA` uses `len / 2`; for the two lengths this source feeds it (8 and 21)
  integer and float division agree (4 and 10), so the ambiguity between Pine v3
  integer division and a float-to-int cast cannot bite here. `round(sqrt(len))`
  uses Pine's half-away-from-zero rounding.
* `SMMA` (`v5`) is `na(v5[1]) ? sma(src,len) : (v5[1]*(len-1)+src)/len`, which is
  Wilder's smoothing seeded from the first full SMA window -- byte for byte what
  `pine_ta.pine_rma` computes, so the shared helper is used and the formula is
  restated here.
* `SSMA` (`v9`) is Ehlers' SuperSmoother recurrence with `nz` on both history
  terms, so bar 0 is `c1 * src / 2`; reproduced as an explicit recurrence.
* `last_open_*Condition` / `last_*Condition` use `nz(...)`, i.e. they start at
  0.0 before the first signal rather than at na.
* No stop / limit / trail EXIT exists (`strategy.close` never fires and there is
  no `strategy.exit`), so `source_reproduce_stops` is False. A position is only
  ever closed by an opposite entry reversing it, and one still open at the end
  of the window stays open.
* `type` is named after the source's own variable even though it shadows a
  builtin; it is only ever read as a dict key.
* md/source divergence recorded, not acted on: the md's `v_input_*` table
  renders `Pyramiding` as `true`, while the source declares
  `pyrl = input(1, "Pyramiding")`. The source is authoritative and the port
  carries 1. The md's pinescript block is byte-identical to the extracted
  source, and so is every one of the four mds here.
* plot / hline / the `alertcondition`-free display calls are not reproduced.
  Leverage, margin, liquidation, funding and the venue's contract-step rounding
  are unmodelled (PINE_SEMANTICS.md section 2).
"""
import math

import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMElevenMaCross_537874(PinePortBase, IStrategy):
    source_id = "SM_5378740f236b8386"
    source_file = (
        "Eleven-Moving-Averages-Crossover-Strategy十一条移动平均线组合交叉策略.md"
    )
    timeframe = "1h"
    can_short = True
    # Every input() in the source, with its defval. `srcclose1` / `srcclose2`
    # are source inputs defaulting to close; they are carried as source names.
    source_defaults: dict = {
        "type": "ZEMA",
        "len1": 8,
        "srcclose1": "close",
        "len2": 21,
        "srcclose2": "close",
        "pyrl": 1,
        "isTPl": False,
        "isTPs": False,
        "tpl": 3,
        "tps": 30,
        "isSLl": False,
        "isSLs": False,
        "sl": 3,
    }
    # strategy(title=..., overlay=true) states nothing, so Pine's documented
    # defaults apply: fixed / 1 contract, commission 0%, pyramiding 0, initial
    # capital 1000000, process_orders_on_close=false. NOTE: the source's `pyrl`
    # input is titled "Pyramiding" but is an ordinary variable that gates the
    # cross counter -- it is NOT the strategy function's `pyramiding` parameter,
    # which is unset and therefore 0.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The long entry is a resting STOP order (stop = open[1]), the shape "
        "PINE_SEMANTICS.md section 2 item 11 records as inexpressible through "
        "the Freqtrade interface: the engine fills it on the bar that touches "
        "the level, the framework can only fill the next open after the signal "
        "bar. Engine side is faithful; the framework side is a framework "
        "boundary. `strategy.entry` with a na stop places no order in Pine, so "
        "bar 0 (open[1] = na) is skipped instead of being given a NaN stop.",
        "PINE_SEMANTICS.md 1.12 (open): the engine replaces a same-id resting "
        "`exit` order but ACCUMULATES same-id stop/limit ENTRY orders where Pine "
        "would replace. This source re-issues its `\"long\"` stop entry on every "
        "signal, so it lies on that open question. Recorded, not worked around.",
        "The source's `pyrl` input is titled \"Pyramiding\" but is an ordinary "
        "variable gating the sectionLongs/sectionShorts counter; the strategy "
        "function's own `pyramiding` is unset and therefore 0. The port carries "
        "the SOURCE's `input(1, \"Pyramiding\")` default, 1.",
        "md/source divergence recorded, not acted on: the md's v_input table "
        "renders `Pyramiding` as `true`, where the source declares "
        "`pyrl = input(1, \"Pyramiding\")`. The md's pinescript block is "
        "otherwise byte-identical to the extracted source.",
        "`variant` has eleven branches; only the selected one is evaluated. Pine "
        "evaluates all of them every bar and returns exactly one, and they are "
        "pure, so evaluating the selected branch alone cannot change the series.",
        "ZEMA (default) is `v2 + (v2 - ema(v2, len))` with v2 = ema(src, len) -- "
        "a zero-lag EMA, written out explicitly rather than mapped onto ta.ema "
        "(iron rule 3).",
        "SMMA restated to match pine_ta.pine_rma exactly (Wilder smoothing "
        "seeded from the first full SMA window); SSMA is Ehlers' SuperSmoother "
        "recurrence with nz() on both history terms, reproduced as a recurrence.",
        "All four exit conditions are computed and then gated off by their own "
        "input defaults (isTPl/isTPs/isSLl/isSLs = false), so both "
        "`strategy.close` calls never fire. They are kept in source order.",
        "`tpl`/`tps`/`sl` are PERCENTAGES (`1 + pct/100`), so the tick-unit rule "
        "of PINE_SEMANTICS.md 3.5 does not apply to them.",
        "`last_open_*`/`last_*` use nz(), i.e. they hold 0.0 (not na) before the "
        "first signal of their side.",
        "No stop/limit/trail EXIT exists, so source_reproduce_stops is False; a "
        "position only closes when an opposite entry reverses it.",
        "plot/hline and the display calls are not reproduced. Leverage/margin/"
        "liquidation/funding and the venue's contract-step rounding are "
        "unmodelled (PINE_SEMANTICS.md section 2).",
    ]

    # ---- the source's `variant()` ----------------------------------------
    @staticmethod
    def _supersmoother(src: pd.Series, length: int) -> pd.Series:
        """`v9`: Ehlers' SuperSmoother, v3 recurrence with nz on both histories."""
        a1 = math.exp(-1.414 * 3.14159 / length)
        b1 = 2 * a1 * math.cos(1.414 * 3.14159 / length)
        c2 = b1
        c3 = (-a1) * a1
        c1 = 1 - c2 - c3
        values = src.to_numpy(dtype=float)
        out = np.zeros(len(values), dtype=float)
        for i in range(len(values)):
            prev_src = values[i - 1] if i >= 1 else 0.0   # nz(src[1])
            prev1 = out[i - 1] if i >= 1 else 0.0         # nz(v9[1])
            prev2 = out[i - 2] if i >= 2 else 0.0         # nz(v9[2])
            out[i] = c1 * (values[i] + prev_src) / 2 + c2 * prev1 + c3 * prev2
        return pd.Series(out, index=src.index, dtype=float)

    @classmethod
    def _ma_variant(cls, kind, src: pd.Series, length: int,
                    volume: pd.Series) -> pd.Series:
        """The source's `variant(type, src, len)`, one branch per MA type."""
        length = int(length)
        simple = ta.pine_sma(src, length)                      # v1  SMA
        exponential = ta.pine_ema(src, length)                 # v2  EMA
        if kind == "EMA":
            return exponential
        if kind == "WMA":
            return ta.pine_wma(src, length)                    # v3  WMA
        if kind == "VWMA":
            weighted = src.copy()
            weighted.attrs["volume"] = volume
            return ta.pine_vwma(weighted, length)              # v4  VWMA
        if kind == "SMMA":
            return ta.pine_rma(src, length)                    # v5  SMMA
        if kind == "DEMA":
            return 2 * exponential - ta.pine_ema(exponential, length)   # v6
        if kind == "TEMA":
            double = ta.pine_ema(exponential, length)          # v7
            return 3 * (exponential - double) + ta.pine_ema(double, length)
        if kind == "HullMA":
            half = ta.pine_wma(src, int(length / 2))           # v8  Hull
            full = ta.pine_wma(src, length)
            return ta.pine_wma(2 * half - full, ta.pine_round(np.sqrt(length)))
        if kind == "TMA":
            return ta.pine_sma(simple, length)                 # v11 Triangular
        if kind == "SSMA":
            return cls._supersmoother(src, length)             # v9
        if kind == "ZEMA":
            return exponential + (exponential - ta.pine_ema(exponential, length))
        return simple                                          # v1  fallback

    def pine_indicators(self, dataframe, params):
        kind = params["type"]
        close = dataframe["close"]
        volume = dataframe["volume"]
        len1 = int(params["len1"])
        len2 = int(params["len2"])
        pyrl = float(params["pyrl"])

        ma_1 = self._ma_variant(kind, ta.pine_source(dataframe, params["srcclose1"]),
                                len1, volume)
        ma_2 = self._ma_variant(kind, ta.pine_source(dataframe, params["srcclose2"]),
                                len2, volume)

        long_cond = ta.pine_crossover(ma_1, ma_2)
        short_cond = ta.pine_crossunder(ma_1, ma_2)
        long_cond = long_cond.fillna(False)
        short_cond = short_cond.fillna(False)

        # sectionLongs / sectionShorts: a bare Pine global is re-seeded to 0 each
        # bar and then immediately overwritten with its own previous value, so
        # the counters carry; they are rebuilt here as series.
        n = len(dataframe)
        long_flag = long_cond.to_numpy()
        short_flag = short_cond.to_numpy()
        section_longs = np.zeros(n, dtype=float)
        section_shorts = np.zeros(n, dtype=float)
        sl = ss = 0.0
        for i in range(n):
            if long_flag[i]:
                sl += 1.0
                ss = 0.0
            if short_flag[i]:
                sl = 0.0
                ss += 1.0
            section_longs[i] = sl
            section_shorts[i] = ss

        long_condition = long_cond & (section_longs <= pyrl)
        short_condition = short_cond & (section_shorts <= pyrl)

        # last_open_*: carried forward from high[1] / low[1] at each signal, with
        # nz() turning the pre-first-signal na into 0.0.
        prev_high = dataframe["high"].shift(1)
        prev_low = dataframe["low"].shift(1)
        last_open_long = prev_high.where(long_condition).ffill().fillna(0.0)
        last_open_short = prev_low.where(short_condition).ffill().fillna(0.0)

        # last_*: the signal's own timestamp, again nz()-carried. Pine's `time`
        # is the bar's open time; the frame's index carries the same ordering.
        bar_time = pd.Series(
            np.arange(n, dtype=float) if not isinstance(dataframe.index, pd.DatetimeIndex)
            else dataframe.index.astype("int64").to_numpy(dtype=float),
            index=dataframe.index,
        )
        last_long = bar_time.where(long_condition).ffill().fillna(0.0)
        last_short = bar_time.where(short_condition).ffill().fillna(0.0)
        in_long = last_long > last_short
        in_short = last_short > last_long

        is_tpl = bool(params["isTPl"])
        is_tps = bool(params["isTPs"])
        is_sll = bool(params["isSLl"])
        is_sls = bool(params["isSLs"])
        tpl = float(params["tpl"])
        tps = float(params["tps"])
        sl_pct = float(params["sl"])

        high = dataframe["high"]
        low = dataframe["low"]

        # `isTPl and ...` short-circuits in Pine: with the default `false` the
        # condition is false whatever the rest evaluates to, so the port short
        # circuits the same way rather than building the unused series.
        none_true = pd.Series(False, index=dataframe.index)
        long_tp = (
            (ta.pine_crossover(high, (1 + tpl / 100.0) * last_open_long) & in_long)
            if is_tpl else none_true
        )
        short_tp = (
            (ta.pine_crossunder(low, (1 - tps / 100.0) * last_open_short) & in_short)
            if is_tps else none_true
        )
        # `longCondition == 0` / `in_longCondition == 1` are bool-in-numeric
        # tests; for `== 0` / `== 1` Python and numpy agree with Pine (the
        # reversal trap of PINE_SEMANTICS.md 1.16 is the `!= 0` form), so the
        # plain boolean complements are used.
        long_sl = (
            (
                ta.pine_crossunder(low, (1 - sl_pct / 100.0) * last_open_long)
                & (~long_condition) & in_long
            )
            if is_sll else none_true
        )
        short_sl = (
            (
                ta.pine_crossover(high, (1 + sl_pct / 100.0) * last_open_short)
                & (~short_condition) & in_short
            )
            if is_sls else none_true
        )

        long_close = (long_tp | long_sl).fillna(False)
        short_close = (short_tp | short_sl).fillna(False)

        dataframe["pine_ma_fast"] = ma_1
        dataframe["pine_ma_slow"] = ma_2
        dataframe["pine_long_condition"] = long_condition.fillna(False)
        dataframe["pine_short_condition"] = short_condition.fillna(False)
        dataframe["pine_long_close"] = long_close
        dataframe["pine_short_close"] = short_close
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "long_close": dataframe["pine_long_close"].to_numpy(),
            "short_close": dataframe["pine_short_close"].to_numpy(),
            # `stop = open[1]`; na on bar 0.
            "prev_open": dataframe["open"].shift(1).to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("long", strategy.long, when=longCondition == true,
        #                 stop = open[1])
        if ctx["long_condition"][i]:
            stop = ctx["prev_open"][i]
            if np.isfinite(stop):
                broker.entry("long", "long", stop=float(stop))
        # strategy.entry("short", strategy.short, when=shortCondition == true)
        if ctx["short_condition"][i]:
            broker.entry("short", "short")
        # strategy.close("long", when = long_sl or long_tp)
        if ctx["long_close"][i]:
            broker.close("long")
        # strategy.close("short", when = short_sl or short_tp)
        if ctx["short_close"][i]:
            broker.close("short")
