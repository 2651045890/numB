"""Port of sources/SM_1830c9ff4d87ee01.pine
(batch_001/Ichimoku云图量化策略Ichimoku-Clouds-Quant-Strategy.md).

Pine v5, Skyrex's "Advanced Ichimoku Clouds Strategy Long and Short" (v2.1).
A standard Ichimoku is computed with the source's OWN donchian helper, and the
Tenkan/Kijun cross is classified by where the crossing Tenkan sits relative to
the two displaced (leading) cloud lines:

    donchian(len) => math.avg(ta.lowest(len), ta.highest(len))
    tenkan = donchian(tenkanPeriods)                 # 9
    kijun  = donchian(kijunPeriods)                  # 26
    senkouA = math.avg(tenkan, kijun)
    senkouB = donchian(chikouPeriods)                # 52
    displacedSenkouA = senkouA[displacement - 1]     # 25 bars back
    displacedSenkouB = senkouB[displacement - 1]
    bullishSignal = ta.crossover(tenkan, kijun)
    bearishSignal = ta.crossunder(tenkan, kijun)
    bullishSignalValues = bullishSignal ? tenkan : na
    bearishSignalValues = bearishSignal ? tenkan : na

    strongBullish  = bullVals > dSenkouA and bullVals > dSenkouB
    neutralBullish = (bullVals > dSenkouA and bullVals < dSenkouB)
                     or (bullVals < dSenkouA and bullVals > dSenkouB)
    weakBullish    = bullVals < dSenkouA and bullVals < dSenkouB
    (strong/neutral/weak Bearish are the mirror image on bearVals)

`displacedSenkouA` is a HISTORICAL reference, not a future one: Pine's `[n]`
indexes backwards, `displacement - 1` = 25, so the cloud line compared against
today's crossing Tenkan is the one computed 25 bars AGO. The leading span is
merely DRAWN 25 bars to the right (`offset = displacement - 1` on the plots),
which is display only.

The four signal-selection functions (isEntrySignalLong, isExitSignalLong,
isEntrySignalShort, isExitSignalShort) are eight-branch if/elif chains over
string inputs; they are reproduced branch for branch in `_select_signal`.

Order logic (the `if true` block), transcribed verbatim:

    if tradingMode == "Long"
        takeProfitLevelLong = strategy.position_avg_price * (1 + takeProfitPct/100)
        stopLossLevelLong   = strategy.position_avg_price * (1 - stopLossPct/100)
        if isEntrySignalLong()  -> strategy.entry("entry1", strategy.long)
        if (takeProfitPct > 0 and close >= takeProfitLevelLong)
           or (stopLossPct > 0 and close <= stopLossLevelLong)
           or (exitSignalOptionsLong != "None" and isExitSignalLong())
                                -> strategy.close("entry1")
    else if tradingMode == "Short"
        ... the mirror image, with takeProfitLevelShort = avg * (1 - pct/100)
            and stopLossLevelShort = avg * (1 + pct/100)

The TP/SL are conditional MARKET closes (`strategy.close`), not resting stop
orders, so `source_reproduce_stops` is False.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; `basePeriod: 1h` is the FMZ backtester's own fill
granularity. The header's start/end (2023-01-25 .. 2024-01-31) is the FMZ
backtest range, NOT a strategy filter: the two date inputs it corresponds to
(`lookBackPeriodStart` / `lookBackPeriodStop`) are DECLARED AND NEVER READ
(measured: each name occurs only on its own `input()` line), so the port trades
the whole series unfiltered. Same for `pctToPoints` (defined, never called) and
`sourceUuid` / `secretToken` (only ever concatenated into `alert_message`
strings). `show*` inputs only gate `plot(...)`, and `barcolor` / `fill` /
`color*` are display only -- none is reproduced.

FIDELITY: see source_fidelity_notes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _donchian(low: pd.Series, high: pd.Series, length: int) -> pd.Series:
    """Pine `math.avg(ta.lowest(len), ta.highest(len))`.

    The one-argument overloads of `ta.lowest` / `ta.highest` default their
    source to `low` and `high` respectively, so the window is min(low) over
    `len` bars and max(high) over `len` bars. na inside the window propagates
    through the average, exactly as Pine's na arithmetic does.
    """
    lowest = ta.pine_lowest(low, length)
    highest = ta.pine_highest(high, length)
    return (lowest + highest) / 2.0        # math.avg(a, b) = (a + b) / 2


# --- Pine's three-valued boolean logic, on float arrays ---------------------
# Each helper takes float arrays where nan means na, and returns the same:
#   1.0 = true, 0.0 = false, nan = na. These are the exact tables Pine
# documents -- `false and na` is false, `na and na` is na, `true or na` is
# true, `na or na` is na -- so a condition that is later consumed by an `if`
# collapses na to false in both the source and this port.
def _pine_gt(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """`a > b`, na where either side is na."""
    return np.where(np.isnan(a) | np.isnan(b), np.nan, (a > b).astype(float))


def _pine_lt(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """`a < b`, na where either side is na."""
    return np.where(np.isnan(a) | np.isnan(b), np.nan, (a < b).astype(float))


def _pine_and(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pine `and`: false if either operand is false, else na if any is na."""
    out = np.where((a == 0.0) | (b == 0.0), 0.0,
                   np.where(np.isnan(a) | np.isnan(b), np.nan, 1.0))
    return out


def _pine_or(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pine `or`: true if either operand is true, else na if any is na."""
    out = np.where((a == 1.0) | (b == 1.0), 1.0,
                   np.where(np.isnan(a) | np.isnan(b), np.nan, 0.0))
    return out


# The source's four `is*Signal*()` functions are one and the same eight-branch
# if/elif chain over an `input.string(options = [...])`. The option labels are
# the source's own; the chain order below is the source's order. A label that
# matches no branch leaves `entryCondition` at its initial `false`.
def _select_signal(option: str, strong: np.ndarray, neutral: np.ndarray,
                   weak: np.ndarray, flavour: str) -> np.ndarray:
    """One `is*Signal*()` chain. `flavour` is "Bullish" or "Bearish"."""
    s = f"{flavour} Strong"
    n = f"{flavour} Neutral"
    w = f"{flavour} Weak"
    table = [
        (s, lambda: strong),
        (n, lambda: neutral),
        (w, lambda: weak),
        (f"{flavour} Strong and Neutral", lambda: _pine_or(strong, neutral)),
        (f"{flavour} Neutral and Weak", lambda: _pine_or(neutral, weak)),
        (f"{flavour} Strong and Weak", lambda: _pine_or(strong, weak)),
        (f"{flavour} All", lambda: _pine_or(_pine_or(strong, neutral), weak)),
    ]
    for label, build in table:
        if option == label:
            return build()
    # "None", and (unreachably, since the input is constrained to the options
    # list) any label the chain does not cover: the initial `false`.
    return np.zeros(len(strong), dtype=float)


class SMIchimokuCloudsQuant_1830c9(PinePortBase, IStrategy):
    source_id = "SM_1830c9ff4d87ee01"
    source_file = "Ichimoku云图量化策略Ichimoku-Clouds-Quant-Strategy.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "sourceUuid": "yourBotSourceUuid",
        "secretToken": "yourBotSecretToken",
        "lookBackPeriodStart": 1672531200000,   # timestamp('2023-01-01T00:00:00')
        "lookBackPeriodStop": 1735689600000,    # timestamp('2025-01-01T00:00:00')
        "tradingMode": "Long",
        "entrySignalOptionsLong": "Bullish All",
        "exitSignalOptionsLong": "Bearish Weak",
        "entrySignalOptionsShort": "None",
        "exitSignalOptionsShort": "None",
        "takeProfitPct": 0.0,
        "stopLossPct": 0.0,
        "tenkanPeriods": 9,
        "kijunPeriods": 26,
        "chikouPeriods": 52,
        "displacement": 26,
        "showTenkan": False,
        "showKijun": False,
        "showSenkouA": True,
        "showSenkouB": True,
        "showChikou": False,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.1
    source_pyramiding = 1
    source_initial_capital = 10_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`timeframe` is taken from the source's `/*backtest` header (`period: "
        "1d`, Futures_Binance BTC_USDT). The header's `basePeriod: 1h` is the "
        "FMZ backtester's own fill granularity, not the strategy period, and "
        "the header's start/end (2023-01-25 .. 2024-01-31) is the FMZ backtest "
        "range, not a strategy filter.",
        "`strategy(...)` declares `commission_type = strategy.commission.percent` "
        "with `commission_value = 0.1`, `initial_capital = 10000`, "
        "`default_qty_type = strategy.percent_of_equity`, `default_qty_value = "
        "100`, `pyramiding = 1`, `calc_on_order_fills = false`, "
        "`calc_on_every_tick = true`, `slippage = 5`.",
        "`slippage = 5` is NOT modelled. The shared engine fills market orders "
        "at the next bar's open with no slippage, and `PinePortBase` has no "
        "slippage channel, so this port fills at the open where the source's "
        "platform would fill 5 ticks away from it (the tick size is a property "
        "of the symbol, which the engine does not model either). Recorded as a "
        "known difference, not reproduced -- the framework cannot express it.",
        "`calc_on_every_tick = true` is NOT modelled: the shared engine "
        "evaluates the script once per bar at the bar's close and fills market "
        "orders at the next bar's open (PINE_SEMANTICS.md section 一). "
        "`calc_on_order_fills = false` IS what the engine models -- an order "
        "filled mid-bar does not re-run the script.",
        "`lookBackPeriodStart` and `lookBackPeriodStop` are DECLARED AND NEVER "
        "READ (measured: each name occurs only on its own `input()` line, "
        "lines 38-39). They are therefore not a trading window: the port trades "
        "every bar. They are kept in `source_defaults` (the timestamp values "
        "are the millisecond instants Pine's `timestamp()` yields) so the "
        "declared defaults are complete.",
        "`donchian(len) => math.avg(ta.lowest(len), ta.highest(len))` is "
        "transcribed verbatim, including the ONE-argument overloads: Pine "
        "documents `ta.lowest(length)` as taking `low` and `ta.highest(length)` "
        "as taking `high`, so the Tenkan/Kijun lines here are midpoints of the "
        "low/high window. Substituting a library donchian that defaults to "
        "`close` would change every line of the Ichimoku.",
        "`senkouA = math.avg(tenkan, kijun)` is the average of the two "
        "midpoints -- not a donchian of its own -- and `senkouB = "
        "donchian(chikouPeriods)` uses the 52-period window.",
        "`displacedSenkouA = senkouA[displacement - 1]` is a BACKWARD "
        "reference: with the default displacement = 26 it is `senkouA[25]`, the "
        "value from 25 bars ago. The Ichimoku leading span is drawn 25 bars to "
        "the RIGHT (`offset = displacement - 1` on the plots), but the value "
        "the signal logic compares against is the one shifted back, so there is "
        "no future-data reference here. This is the one place where the "
        "source's `offset` (a plot argument) and its `[displacement - 1]` "
        "(an index) point in opposite directions, and the port follows the "
        "INDEX because that is what the classification reads. MEASURED on the "
        "validate_pine synthetic frame: `senkouA` is first defined on bar 25 "
        "and `displacedSenkouA` on bar 50 -- the 25-bar backward shift, not a "
        "forward one.",
        "`bullishSignalValues = bullishSignal ? tenkan : na` is na on every bar "
        "EXCEPT the crossover bar itself, so all six strong/neutral/weak "
        "classifications are na everywhere off the crossover bar and can only "
        "be true on that single bar. A position's entry therefore can only be "
        "placed on a crossover bar. MEASURED on the synthetic frame: 71 "
        "crossover bars and 76 crossunder bars in 3000, with the six "
        "classification series na on 2929 (resp. 2924/2925) of them; the three "
        "bullish classes are true on 25 / 12 / 34 bars, which sums to exactly "
        "71 with no bar in two classes -- every crossover on that frame falls "
        "into exactly one of strong, neutral and weak.",
        "THREE-VALUED na LOGIC IS MODELLED EXPLICITLY, not folded to false "
        "early. The classification is a tree of `>` / `<` comparisons combined "
        "with `and` / `or`, and Pine's `and` / `or` are not the same as "
        "Python's two-valued ones: `false and na` is false but `na and na` is "
        "na, and `true or na` is true but `na or na` is na. `_pine_gt` / "
        "`_pine_lt` / `_pine_and` / `_pine_or` implement those tables on float "
        "arrays where nan means na. The end use is an `if` condition, where "
        "Pine treats na as false, so the entry/exit predicates are tested as "
        "`== 1.0`. MEASURED on the validate_pine synthetic frame: the "
        "three-valued classification and a plain two-valued one are true on "
        "the same 71 bars (bitwise identical), because no branch negates a "
        "possibly-na operand; the tables are still implemented exactly, since "
        "the synthetic frame is not the source's instrument.",
        "OPERATIONAL, MEASURED under the declared defaults on the "
        "validate_pine synthetic frame: `isEntrySignalLong()` is true on all "
        "71 crossover bars, `isExitSignalLong()` on 33 bars (the \"Bearish "
        "Weak\" subset of the 76 crossunders), and the two Short selections on "
        "0 bars, because `entrySignalOptionsShort` and `exitSignalOptionsShort` "
        "both default to \"None\". `validate_pine` reports 48 projected "
        "`enter_long` signals rather than 71: an entry that the engine's "
        "pyramiding model blocks (see the pyramiding note below) is not "
        "projected, and the same run books 46 engine trades with 2 entries "
        "still open. `exit_short` is 0 there as well.",
        "The comparison is against the DISPLACED cloud lines, and `>` / `<` are "
        "strict, so a crossing Tenkan exactly ON a cloud line is classified "
        "NEITHER strong, nor neutral, nor weak by that pair of branches: "
        "`neutral` requires `> dA and < dB` or `< dA and > dB`, and equality "
        "satisfies neither. That is the source's literal text and is preserved.",
        "The two date inputs being dead means the source has NO exit-by-time "
        "path, and the only exits are (a) a `strategy.close` triggered by the "
        "TP/SL percentages -- disabled by default because both default to 0 -- "
        "or (b) an exit signal, selected by `exitSignalOptionsLong` (default "
        "\"Bearish Weak\") / `exitSignalOptionsShort` (default \"None\").",
        "`takeProfitLevelLong` / `stopLossLevelLong` (and the Short mirror) are "
        "computed from `strategy.position_avg_price` on EVERY bar, before the "
        "entry for that bar is placed. The shared engine fills pending orders "
        "at the bar's open and then runs the script, so `position_avg_price` "
        "inside the script is the price of the position as of the previous "
        "bar's orders -- the same instant Pine's script sees. The engine models "
        "`position_avg_price` as na while flat; whether TradingView v5 returns "
        "na or 0 in that state is UNVERIFIED here. With the default inputs "
        "(takeProfitPct = stopLossPct = 0) the `pct > 0` guard short-circuits "
        "to false on both sides, so the question changes no behaviour under the "
        "declared defaults -- and Pine's `x > 0 and close >= na` is na -> false "
        "anyway, which is what the port's Python `and` produces as well.",
        "`strategy.close(id = \"entry1\")` closes only the entry whose id is "
        "`entry1`, and both branches of the source use that one id. It is a "
        "MARKET order placed on the condition bar and filled at the next bar's "
        "open, so the TP/SL are re-checked on the CLOSE of each bar and are not "
        "resting orders that can trigger intrabar -- recorded because a reader "
        "could otherwise take \"Take Profit, %\" for a stop order. There is no "
        "`strategy.exit` and no resting stop/limit order anywhere, so "
        "`source_reproduce_stops` is False.",
        "`strategy.entry(id = \"entry1\", direction = strategy.long)` is given "
        "no `qty`, so the order takes the strategy default "
        "(percent_of_equity, 100). The entry id is the same for longs and "
        "shorts, but only one of the two branches can run -- `tradingMode` is a "
        "single-valued string input -- so the id never carries both directions "
        "at once. With `pyramiding = 1`, a further entry in the same direction "
        "STACKS rather than retargeting the position (Pine sizes an entry so "
        "the resulting position equals its quantity only when the direction "
        "differs; the engine's `_can_add` allows `open_same <= pyramiding`). "
        "PINE_SEMANTICS.md 2.10 records pyramiding as NOT implemented on the "
        "framework side -- `PinePortBase.position_adjustment_enable` is False, "
        "so Freqtrade can hold only one entry -- which is a measured "
        "bookkeeping difference between the two sides, not a claim that the "
        "port reproduces stacking.",
        "`alert_message = '{\"base\": ... }'` is built from `syminfo."
        "basecurrency`, `syminfo.currency`, `sourceUuid` and `secretToken` and "
        "passed to both `strategy.entry` and `strategy.close`. The shared "
        "engine's `entry` / `close` take no alert-message argument, and an "
        "alert message places no order, so it is not reproduced; the two string "
        "inputs are kept in `source_defaults` but read by nothing.",
        "`pctToPoints(pct) => strategy.position_avg_price * pct / 100` is "
        "defined at lines 70-71 and NEVER CALLED (measured: the name occurs "
        "only on its definition line). Both TP/SL levels are written out "
        "inline instead, so the helper is dead code; it is not reproduced as a "
        "live path.",
        "`showTenkan` / `showKijun` / `showSenkouA` / `showSenkouB` / "
        "`showChikou` are read only by `plot(...)` expressions, `transparency"
        "Level` / `colorGreen` / `colorRed` / `colorTenkanViolet` / `colorKijun` "
        "`/ colorLime` / `colorMaroon` / `colorGreenTransparent` / "
        "`colorRedTransparent` only by `plot` / `fill`, and `barcolor` / `fill` "
        "are display only. None is reproduced. The `show*` defaults are still "
        "carried in `source_defaults`.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`v_input_float_1` (Take Profit, %) and `v_input_float_2` (Stop Loss, "
        "%) as `false` where the source declares `input.float(0, ...)`, and it "
        "renders the six `input.string` defaults as `0` -- the exporter "
        "flattening a string default to its index. It also lists each string "
        "input's `options` in a DIFFERENT ORDER from the source (e.g. entry "
        "signal Long as `Bullish All|Bullish Strong|...|None` against the "
        "source's `None|Bullish Strong|...|Bullish All`). The option SETS are "
        "identical and the source's code tests labels, not positions, so the "
        "order is immaterial; the defaults are taken from the source: 0.0 / "
        "0.0 and \"Long\" / \"Bullish All\" / \"Bearish Weak\" / \"None\" / "
        "\"None\".",
        "CHAIN VERDICT, MEASURED: on BTC/USDT:USDT 20240101-20250101 the chain "
        "verifier reports `mismatch` -- engine 6 trades, framework 4, with 1 "
        "open_date and 1 close_date mismatch -- and both sides end flat. The "
        "engine-side decomposition of those 6, measured by re-running the port "
        "on the same 1d window: 6 = 4 first entries + 2 SECOND entries of a "
        "stack (filled on bars 236 and 349). Three entry orders were placed "
        "while an entry was already open (bars 235, 262, 348); two became the "
        "stack's second entry and the third (bar 262) was blocked because two "
        "entries were already open. This is the pyramiding bookkeeping "
        "difference named above (PINE_SEMANTICS.md 2.10), not a signal-path "
        "difference: the framework is structurally limited to one entry, so it "
        "books 4 trades where the engine books 6. The residue of that -- 1 "
        "price-tick, 1 price-rounding and 4 pnl-step mismatches, max price gap "
        "33989.2 -- follows from the framework averaging one position where "
        "the engine carried two; the alternating `mismatch` and "
        "`backtest_failed: Could not load markets` results across repeated "
        "runs are the documented intermittent network failure, not a port "
        "change (the port_sha256 was unchanged across them).",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 2.4 / 1.6), so the "
        "framework and the engine can differ by a rounded quantity. That is "
        "measured separately by the chain verifier.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        low = dataframe["low"]
        high = dataframe["high"]
        close = dataframe["close"]

        tenkan = _donchian(low, high, int(params["tenkanPeriods"]))
        kijun = _donchian(low, high, int(params["kijunPeriods"]))
        senkou_a = (tenkan + kijun) / 2.0                    # math.avg(tenkan, kijun)
        senkou_b = _donchian(low, high, int(params["chikouPeriods"]))

        # senkouA[displacement - 1] / senkouB[displacement - 1]: a BACKWARD
        # reference. `displacement` has minval=1 in the source, so the offset
        # is >= 0.
        offset = int(params["displacement"]) - 1
        displaced_a = senkou_a.shift(offset)
        displaced_b = senkou_b.shift(offset)

        bullish = ta.pine_crossover(tenkan, kijun)
        bearish = ta.pine_crossunder(tenkan, kijun)
        # `bullishSignal ? tenkan : na` -- na off the crossover bar.
        bull_vals = tenkan.where(bullish.to_numpy(), np.nan).to_numpy(dtype=float)
        bear_vals = tenkan.where(bearish.to_numpy(), np.nan).to_numpy(dtype=float)
        da = displaced_a.to_numpy(dtype=float)
        db = displaced_b.to_numpy(dtype=float)

        strong_bull = _pine_and(_pine_gt(bull_vals, da), _pine_gt(bull_vals, db))
        neutral_bull = _pine_or(
            _pine_and(_pine_gt(bull_vals, da), _pine_lt(bull_vals, db)),
            _pine_and(_pine_lt(bull_vals, da), _pine_gt(bull_vals, db)),
        )
        weak_bull = _pine_and(_pine_lt(bull_vals, da), _pine_lt(bull_vals, db))

        strong_bear = _pine_and(_pine_lt(bear_vals, da), _pine_lt(bear_vals, db))
        neutral_bear = _pine_or(
            _pine_and(_pine_gt(bear_vals, da), _pine_lt(bear_vals, db)),
            _pine_and(_pine_lt(bear_vals, da), _pine_gt(bear_vals, db)),
        )
        weak_bear = _pine_and(_pine_gt(bear_vals, da), _pine_gt(bear_vals, db))

        # --- the four is*Signal*() chains, branch for branch -----------------
        entry_long = _select_signal(str(params["entrySignalOptionsLong"]),
                                    strong_bull, neutral_bull, weak_bull, "Bullish")
        exit_long = _select_signal(str(params["exitSignalOptionsLong"]),
                                   strong_bear, neutral_bear, weak_bear, "Bearish")
        entry_short = _select_signal(str(params["entrySignalOptionsShort"]),
                                     strong_bear, neutral_bear, weak_bear, "Bearish")
        exit_short = _select_signal(str(params["exitSignalOptionsShort"]),
                                    strong_bull, neutral_bull, weak_bull, "Bullish")

        dataframe["pine_tenkan"] = tenkan
        dataframe["pine_kijun"] = kijun
        dataframe["pine_senkou_a"] = senkou_a
        dataframe["pine_senkou_b"] = senkou_b
        dataframe["pine_displaced_senkou_a"] = displaced_a
        dataframe["pine_displaced_senkou_b"] = displaced_b
        dataframe["pine_bullish_signal"] = bullish
        dataframe["pine_bearish_signal"] = bearish
        dataframe["pine_bullish_values"] = bull_vals
        dataframe["pine_bearish_values"] = bear_vals
        dataframe["pine_strong_bull"] = strong_bull
        dataframe["pine_neutral_bull"] = neutral_bull
        dataframe["pine_weak_bull"] = weak_bull
        dataframe["pine_strong_bear"] = strong_bear
        dataframe["pine_neutral_bear"] = neutral_bear
        dataframe["pine_weak_bear"] = weak_bear
        # An `if` condition treats na as false, in the source and here alike.
        dataframe["pine_entry_long"] = entry_long == 1.0
        dataframe["pine_exit_long"] = exit_long == 1.0
        dataframe["pine_entry_short"] = entry_short == 1.0
        dataframe["pine_exit_short"] = exit_short == 1.0
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "entry_long": dataframe["pine_entry_long"].to_numpy(dtype=bool),
            "exit_long": dataframe["pine_exit_long"].to_numpy(dtype=bool),
            "entry_short": dataframe["pine_entry_short"].to_numpy(dtype=bool),
            "exit_short": dataframe["pine_exit_short"].to_numpy(dtype=bool),
            "tradingMode": str(params["tradingMode"]),
            "entrySignalOptionsLong": str(params["entrySignalOptionsLong"]),
            "exitSignalOptionsLong": str(params["exitSignalOptionsLong"]),
            "entrySignalOptionsShort": str(params["entrySignalOptionsShort"]),
            "exitSignalOptionsShort": str(params["exitSignalOptionsShort"]),
            "takeProfitPct": float(params["takeProfitPct"]),
            "stopLossPct": float(params["stopLossPct"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # if true
        if ctx["tradingMode"] == "Long":
            # takeProfitLevelLong = strategy.position_avg_price * (1 + tp / 100)
            # stopLossLevelLong   = strategy.position_avg_price * (1 - sl / 100)
            # `position_avg_price` is the engine's own reading at this bar.
            avg_price = broker.position_avg_price
            tp_pct = ctx["takeProfitPct"]
            sl_pct = ctx["stopLossPct"]
            take_profit_level = avg_price * (1.0 + tp_pct / 100.0)
            stop_loss_level = avg_price * (1.0 - sl_pct / 100.0)

            # if isEntrySignalLong()
            if ctx["entry_long"][i]:
                broker.entry("entry1", "long")
            # if (takeProfitPct > 0 and close >= takeProfitLevelLong)
            #    or (stopLossPct > 0 and close <= stopLossLevelLong)
            #    or (exitSignalOptionsLong != "None" and isExitSignalLong())
            if ((tp_pct > 0 and ctx["close"][i] >= take_profit_level)
                    or (sl_pct > 0 and ctx["close"][i] <= stop_loss_level)
                    or (ctx["exitSignalOptionsLong"] != "None"
                        and ctx["exit_long"][i])):
                broker.close("entry1")

        # else if tradingMode == "Short"
        elif ctx["tradingMode"] == "Short":
            # takeProfitLevelShort = strategy.position_avg_price * (1 - tp / 100)
            # stopLossLevelShort   = strategy.position_avg_price * (1 + sl / 100)
            avg_price = broker.position_avg_price
            tp_pct = ctx["takeProfitPct"]
            sl_pct = ctx["stopLossPct"]
            take_profit_level = avg_price * (1.0 - tp_pct / 100.0)
            stop_loss_level = avg_price * (1.0 + sl_pct / 100.0)

            # if isEntrySignalShort()
            if ctx["entry_short"][i]:
                broker.entry("entry1", "short")
            # if (takeProfitPct > 0 and close <= takeProfitLevelShort)
            #    or (stopLossPct > 0 and close >= stopLossLevelShort)
            #    or (exitSignalOptionsShort != "None" and isExitSignalShort())
            if ((tp_pct > 0 and ctx["close"][i] <= take_profit_level)
                    or (sl_pct > 0 and ctx["close"][i] >= stop_loss_level)
                    or (ctx["exitSignalOptionsShort"] != "None"
                        and ctx["exit_short"][i])):
                broker.close("entry1")
