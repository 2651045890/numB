"""Port of sources/SM_113b6a5ac81d3c03.pine (20水平突破策略20-Level-Breakout-Strategy.md).

Pine v5 (see FIDELITY: the file carries a stray `//@version=4`). The "20 level"
is not a 20-period average as the md's prose claims -- it is the close truncated
to two decimals, and the levels are fixed absolute offsets around it:

    baseLevel   = math.floor(close * 100) / 100
    eigthylevel = baseLevel - 0.002      twentyLevel = baseLevel + 0.002
    takeprofitL = baseLevel - 0.01       stoplossL   = baseLevel + 0.02
    takeprofitS = baseLevel + 0.015      stoplossS   = baseLevel - 0.02

    isLong  = close > twentyLevel and close <= baseLevel + 0.01
              and ta.rsi(close, 14) > 40 and ta.ema(close, 50) < close
    isShort = close < eigthylevel and close >= baseLevel - 0.01

Both entries are STOP orders, and both exits are unconditional OCA orders
written for the entry they belong to:

    strategy.entry("Short", strategy.short, when=isLong,  stop=twentyLevel)
    strategy.exit("Stop Loss/Profit", "Short", stop=stoplossL, limit=takeprofitL)
    strategy.entry("Long",  strategy.long,  when=isShort, stop=eigthylevel)
    strategy.exit("Stop loss/Profit", "Long",  stop=stoplossS, limit=takeprofitS)

`isShort` can never be true: it requires `close < baseLevel`, and
`baseLevel = floor(close * 100) / 100` is never greater than `close`. The whole
long side of the script -- `strategy.entry("Long", ...)` and its exit -- is
therefore dead code, and is reproduced as written. The strategy only ever sells.

`isLong` is true exactly when `floor(close * 100)` truncates below the true
value: with prices quoted on a 0.1 grid, `close * 100` is an integer for most
bars, but in binary floating point it lands a hair low often enough (585 of the
8785 1h bars of BTC/USDT:USDT in 2024) to leave `close - baseLevel ~ 0.01`, which
satisfies `close > baseLevel + 0.002 and close <= baseLevel + 0.01`. The
condition is reproduced with the same float64 `floor(close * 100) / 100`, so the
same bars (RSI and EMA permitting) signal here as on the original platform.

The source declares no `input()` and no `strategy()` properties beyond
`overlay=true`, so Pine's documented defaults apply: initial capital 1000000
USD, default_qty_type strategy.fixed, default_qty_value 1, 0% commission,
pyramiding 0.

FIDELITY:

* The entry guards the exit placement with the entry it belongs to
  (`strategy.position_size < 0` / `> 0`) instead of calling both `strategy.exit`
  arms on every bar as the source text does. In Pine the two arms are bound to
  the entries `"Short"` and `"Long"` by `from_entry`, and an exit order whose
  entry does not exist cannot close anything -- so dropping the arm that has no
  entry is behaviour-preserving, while placing it is not: pine_engine records
  the levels of every exit order it evaluates, `used_exit_levels` does not
  filter by `from_entry` (unlike `active_exit_levels`), and the phantom arm's
  levels would then be pooled with the live arm's and exported as this port's
  stop and take-profit. See source_fidelity_notes and PINE_SEMANTICS.md section 2.
* `strategy.entry(..., stop=...)` is a STOP entry, which a Freqtrade strategy
  cannot place: `run_pine` projects the order as a next-open market entry on the
  bar it was PLACED, while pine_engine fills it inside a later bar when the
  price reaches the level. The two agree only when the stop is reached at the
  next bar's open (a gap through it). The engine ledger is the faithful
  reproduction; the framework side is a projection with that known limit.
  Measured on BTC/USDT:USDT 1h 2024: the ledger projects 309 `enter_short`
  bars, but only 57 of them coincide with an engine entry that filled at the
  next bar's open; 247 of the 304 engine entries filled at the resting stop
  level inside a later bar.
* pine_engine keeps more than one pending order for one id where Pine keeps
  exactly one: re-issuing `strategy.entry("Short", ..., stop=...)` on a later
  bar MODIFIES the resting order in Pine, but each call here leaves its own
  resting order (`_place` de-duplicates only `kind == "exit"`). On
  BTC/USDT:USDT 1h 2024, 300 of the 304 filled entries filled on the bar right
  after placement; three of the four later fills had no newer same-id order and
  therefore agree with Pine, and one (2024-07-29) filled at the superseded
  69396.892 while the pending level had already moved to 69548.892, where Pine
  would have filled at the modified level. An engine limit, recorded not
  patched.
* `baseLevel` uses `math.floor(close * 100) / 100` in float64, which is not the
  same as `close`: the difference is what makes `isLong` reachable at all on a
  0.1-tick symbol.
* `ta.rsi` and `ta.ema` are pine_ta.pine_rsi / pine_ta.pine_ema. Pine does not
  publish its EMA seeding rule; pine_ta seeds with the first observation (see
  PINE_SEMANTICS.md 3.1).
* `isPriceAboveLevel(price, level) => price > level` is defined in the source
  and never called; it has no counterpart here.
* The `plot` / `plotshape` calls, the `isLong ? 1 : 0` histogram and the
  `plot(stoplossL)` / `plot(stoplossS)` lines are display-only.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SM20LevelBreakout_113b6a(PinePortBase, IStrategy):
    source_id = "SM_113b6a5ac81d3c03"
    source_file = "20水平突破策略20-Level-Breakout-Strategy.md"
    timeframe = "1h"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "The md's prose describes a 20-day moving average with a MACD filter and "
        "percentage stops; the code uses no moving average and no MACD at all "
        "(`baseLevel = math.floor(close * 100) / 100`, offsets of 0.002/0.01/"
        "0.015/0.02 in price units, filter = ta.rsi(close, 14) > 40 and "
        "ta.ema(close, 50) < close). The code is authoritative and is what this "
        "port reproduces.",
        "`isShort` (`close < baseLevel` with `baseLevel = floor(close*100)/100`) "
        "is never true, so the whole long arm -- `strategy.entry(\"Long\", ...)` "
        "and `strategy.exit(\"Stop loss/Profit\", \"Long\", ...)` -- is dead "
        "code. Both are reproduced as written rather than deleted.",
        "Pine keeps one order per id, so an exit order bound by `from_entry` to "
        "an entry that does not exist can never close a position. This port "
        "therefore places each exit arm only while the entry it names is open. "
        "Placing both arms unconditionally (as the source text does) would make "
        "pine_engine record the phantom arm's levels too: `used_exit_levels` "
        "reduces every evaluated exit order of the bar's side without checking "
        "`from_entry` (`active_exit_levels` does check it), so the exported "
        "`pine_stop_level` / `pine_limit_level` would become `min`/`max` of the "
        "two arms' levels -- the LONG arm's `stoplossS`/`takeprofitS` applied to "
        "a SHORT position. That is an engine gap, not a source behaviour; the "
        "guard keeps the exported levels equal to the ones Pine would act on.",
        "`strategy.entry(..., stop=...)` cannot be reproduced by a Freqtrade "
        "strategy: the framework only market-enters, and run_pine projects the "
        "resting stop entry as `enter_short = 1` on the bar the order was "
        "PLACED, filling it at the NEXT bar's open. pine_engine instead fills it "
        "in whichever later bar first reaches the level. The two coincide only "
        "when the next bar gaps through the stop (fill at the open); every other "
        "case is a framework-side approximation of a stop entry. This is an "
        "engine/framework boundary limit, recorded rather than hidden. Measured "
        "on BTC/USDT:USDT 1h 2024: 309 projected enter_short bars, of which only "
        "57 coincide with an engine entry filled at the next bar's open; 247 of "
        "the 304 engine entries filled at the resting stop level.",
        "pine_engine keeps one pending order per id for exits but not for "
        "entries: re-issuing strategy.entry(\"Short\", ...) modifies the resting "
        "order in Pine, while each call here leaves its own resting order "
        "(_place de-duplicates only kind == \"exit\"). Measured on BTC/USDT:USDT "
        "1h 2024: 300 of 304 filled entries filled on the bar right after "
        "placement; 3 of the 4 later fills had no newer same-id order and match "
        "Pine, and one (2024-07-29) filled at the superseded 69396.892 while the "
        "pending level had already moved to 69548.892. Recorded, not patched.",
        "No future-data reference and no repainting: every condition reads only "
        "the current or an earlier bar, and each order fills on a later bar "
        "under the engine's Pine timing rules.",
        "`baseLevel = math.floor(close * 100) / 100` is kept in float64, "
        "including its rounding behaviour: on a 0.1-tick symbol `close * 100` is "
        "usually exact and the floor is a no-op (`isLong` unreachable), but the "
        "product sometimes lands a hair below the integer, which is what makes "
        "`close - baseLevel ~ 0.01` and `isLong` reachable (585 of 8785 1h bars "
        "for BTC/USDT:USDT in 2024). Reproducing the float arithmetic matters "
        "here; a decimal-rounded `baseLevel` would trade a different set of bars.",
        "`ta.rsi(close, 14)` uses pine_ta.pine_rsi (Wilder's RMA, na until the "
        "average gain/loss window has formed, 100 when there were no losses) and "
        "`ta.ema(close, 50)` uses pine_ta.pine_ema, whose seeding is a documented "
        "parity risk (PINE_SEMANTICS.md 3.1).",
        "The file carries two version annotations, `//@version=5` and a stray "
        "`//@version=4`; the code uses v5 syntax (`ta.rsi`, `ta.ema`, "
        "`math.floor`), so v5 is the effective version and the second annotation "
        "is treated as a copy-paste artifact.",
        "`isPriceAboveLevel(price, level) => price > level` is declared and never "
        "called, so it has no counterpart here.",
        "The `plot` / `plotshape` calls (including the `isLong ? 1 : 0` "
        "histogram and the two stop-level lines) are display-only and are "
        "dropped.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        # baseLevel = math.floor(close * 100) / 100
        base_level = np.floor(close.to_numpy(dtype=float) * 100.0) / 100.0
        base = pd.Series(base_level, index=close.index, dtype=float)
        dataframe["base_level"] = base
        dataframe["eigthylevel"] = base - 0.002
        dataframe["twentyLevel"] = base + 0.002
        dataframe["takeprofitL"] = base - 0.01
        dataframe["stoplossL"] = base + 0.02
        dataframe["takeprofitS"] = base + 0.015
        dataframe["stoplossS"] = base - 0.02

        # breakout = close > twentyLevel and close > baseLevel
        breakout = (close > dataframe["twentyLevel"]) & (close > base)
        # breakoutl = close < eigthylevel and close < baseLevel
        breakoutl = (close < dataframe["eigthylevel"]) & (close < base)
        dataframe["breakout"] = breakout.fillna(False).astype(bool)
        dataframe["breakoutl"] = breakoutl.fillna(False).astype(bool)
        dataframe["pine_isLong"] = (
            dataframe["breakout"]
            & (close > base)
            & (close <= base + 0.01)
            & (ta.pine_rsi(close, 14) > 40)
            & (ta.pine_ema(close, 50) < close)
        ).fillna(False).astype(bool)
        dataframe["pine_isShort"] = (
            dataframe["breakoutl"]
            & (close < base)
            & (close >= base - 0.01)
        ).fillna(False).astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "isLong": dataframe["pine_isLong"].to_numpy(dtype=bool),
            "isShort": dataframe["pine_isShort"].to_numpy(dtype=bool),
            "twentyLevel": dataframe["twentyLevel"].to_numpy(dtype=float),
            "eigthylevel": dataframe["eigthylevel"].to_numpy(dtype=float),
            "stoplossL": dataframe["stoplossL"].to_numpy(dtype=float),
            "takeprofitL": dataframe["takeprofitL"].to_numpy(dtype=float),
            "stoplossS": dataframe["stoplossS"].to_numpy(dtype=float),
            "takeprofitS": dataframe["takeprofitS"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        position = broker.position_size

        # strategy.entry("Short", strategy.short, when=isLong, stop=twentyLevel)
        if ctx["isLong"][i]:
            broker.entry("Short", "short", stop=float(ctx["twentyLevel"][i]))

        # strategy.exit("Stop Loss/Profit", "Short", stop=stoplossL, limit=takeprofitL)
        # Only placed while the "Short" entry is open: an exit bound to a
        # non-existent entry cannot close anything in Pine, and placing it
        # anyway would leak its levels into this bar's exported exit levels.
        if position < 0:
            broker.exit(
                "Stop Loss/Profit",
                from_entry="Short",
                stop=float(ctx["stoplossL"][i]),
                limit=float(ctx["takeprofitL"][i]),
            )

        # strategy.entry("Long", strategy.long, when=isShort, stop=eigthylevel)
        if ctx["isShort"][i]:
            broker.entry("Long", "long", stop=float(ctx["eigthylevel"][i]))

        # strategy.exit("Stop loss/Profit", "Long", stop=stoplossS, limit=takeprofitS)
        if position > 0:
            broker.exit(
                "Stop loss/Profit",
                from_entry="Long",
                stop=float(ctx["stoplossS"][i]),
                limit=float(ctx["takeprofitS"][i]),
            )
