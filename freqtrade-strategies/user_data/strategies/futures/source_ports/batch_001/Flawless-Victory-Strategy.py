"""Port of sources/SM_4929588c271d03e6.pine (batch_001/Flawless-Victory-Strategy.md).

Pine v4. Bunghole's "Flawless Victory Strategy": three selectable parameter sets
over Bollinger Bands, RSI and MFI. Only v1 is enabled by default.

    len = 14; src = close
    up   = rma(max(change(src), 0), len)
    down = rma(-min(change(src), 0), len)
    rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)

    MFIlength = 14; MFIsrc = hlc3
    MFIupper = sum(volume * (change(MFIsrc) <= 0 ? 0 : MFIsrc), MFIlength)
    MFIlower = sum(volume * (change(MFIsrc) >= 0 ? 0 : MFIsrc), MFIlength)
    _rsi(MFIupper, MFIlower) =>                 // the source's OWN rsi, not ta.rsi
        if MFIlower == 0
            100
        if MFIupper == 0
            0
        100.0 - (100.0 / (1.0 + MFIupper / MFIlower))
    mfi = _rsi(MFIupper, MFIlower)

    // v1 Bollinger Bands          // v2 Bollinger Bands
    length1 = 20; mult1 = 1.0      length2 = 17; mult2 = 1.0
    basis1  = sma(close, 20)       basis2  = sma(close, 17)
    dev1    = 1.0 * stdev(close, 20)   dev2 = 1.0 * stdev(close, 17)

    Buy_1 = close < lower1 and rsi > 42      Sell_1 = close > upper1 and rsi > 70
    Buy_2 = close < lower2 and rsi > 42      Sell_2 = close > upper2 and rsi > 76
    Buy_3 = close < lower1 and mfi < 60      Sell_3 = close > upper1 and rsi > 65
                                                       and mfi > 64

    if v1 == true
        strategy.entry("Long", strategy.long, when = Buy_1)
        strategy.entry("Sell",                when = Sell_1)     // NO direction arg
    if v2 == true
        strategy.entry("Long", strategy.long, when = Buy_2)
        strategy.entry("Sell",                when = Sell_2)     // NO direction arg
        strategy.exit("Stoploss/TP", "Long", stop = v2stoploss_level,
                      limit = v2takeprofit_level)
    if v3 == true
        strategy.entry("Long", strategy.long, when = Buy_3)
        strategy.entry("Sell",                when = Sell_3)     // NO direction arg
        strategy.exit("Stoploss/TP", "Long", stop = v3stoploss_level,
                      limit = v3takeprofit_level)

THE THREE "Sell" ENTRIES HAVE NO DIRECTION ARGUMENT -- A BLOCKER, NOT A CHOICE.

`strategy.entry(id, direction, ...)` takes `direction` as its second POSITIONAL
argument, and the Pine v4 reference documents it as required. All three `Sell`
calls in this source pass only `id`, then the NAMED `when=` and `alert_message=`,
so as written they are not valid Pine and have no defined direction. MEASURED:
across the 5,283 `.pine` files under strategy_migration/sources/ there are 10,856
uncommented `strategy.entry` calls, and exactly 3 of them supply no direction at
all -- neither a positional second argument, nor a named `long=` / `short=`, nor
a v5 `direction=`. All 3 are in THIS source (lines 123, 132, 142). The other
corpus files that look similar at a glance (`strategy.entry("BO", limit=...,
long=strategy.long)` and friends) do name their direction. So the omission is a
property of this source, not of how the corpus was extracted.

A direction therefore has to be MODELLED. Two candidates exist and the source
does not choose between them:

  (A) `strategy.short` -- the reading taken here. The order id is "Sell", the
      alert message is "v1 - Sell Signal!", `rsiSellGuard1 = rsi > 70` is an
      OVERBOUGHT guard, and v2/v3 bind a protective `strategy.exit` to the
      separate id "Long", which only makes sense if "Sell" is a separate
      position. This is the reading implied by the source's own identifiers.
  (B) `strategy.long` -- under reading (B) all six entries are long. With
      `pyramiding = 0` an entry in a direction already open is ignored, and v1
      has no exit call at all, so the default configuration would hold a single
      long from the first signal to the end of the window and never trade again.

Reading (B) is degenerate; reading (A) is not, and (A) is what the identifiers
say. (A) is used, flagged here, and NOT presented as the source's literal
content. An auditor who disagrees can flip the three `"short"` arguments in
`pine_script` to `"long"` without touching anything else: no condition depends
on the direction.

MD-vs-CODE: the md PROSE calls this a "15 minute Bitcoin **Long** strategy" and
says "buying one time and one selling one time", which points at reading (B) /
a close rather than a short. `strategy.entry` cannot close a position, so the
prose's "selling" is not expressible by the code's `strategy.entry` call either.
The prose is secondary to the code and is recorded here, not silently adopted.

`strategy()` declares `default_qty_type = strategy.percent_of_equity`,
`default_qty_value = 100`, `initial_capital = 100000`, `pyramiding = 0` and
`currency = 'USD'`; `commission_type` / `commission_value` are not declared, so
Pine's documented default of `strategy.commission.percent` / 0 applies.

The `/*backtest` header declares `period: 2h` on `Futures_Binance` BTC_USDT, so
`timeframe` is "2h". `basePeriod: 15m` is the FMZ backtester's own fill
granularity, not the strategy's period.

FIDELITY -- what is preserved, and what is a recorded uncertainty:

* The RSI is written out from the source's own three lines rather than routed
  through `ta.pine_rsi`. The two agree (checked formula by formula:
  `rma(max(change, 0))`, `rma(-min(change, 0))`, `down == 0 -> 100`,
  `up == 0 -> 0`); it is written out because the source's explicit `up == 0`
  branch is part of what is being reproduced.
* The MFI is the source's OWN `_rsi(MFIupper, MFIlower)`, NOT the shared
  `ta.mfi` model and NOT the batch's `_pine_mfi` helper. Both of those use a
  rolling SUM as well, but they resolve the degenerate windows differently (the
  helper returns 50, `ta.mfi` per the batch's IEEE reading returns 100 or nan),
  whereas this source states its convention explicitly: `MFIlower == 0` gives
  100 and is tested FIRST, then `MFIupper == 0` gives 0. Those branches are
  reproduced in that order.
* MEASURED: the `MFIlower == 0 -> 100` branch IS exercised. Native 2h bars are
  not in the local history, so the measurement frame is the source's own period
  rebuilt by resampling the local BTC/USDT:USDT **1h** futures series to 2h
  (25,049 bars, 2021-01-01..2026-09-19); on that frame 25,036 windows have both
  terms defined, `MFIlower` sums to exactly 0 on 2 of them (2023-06-21 16:00 and
  2024-10-29 18:00) and `MFIupper` never does. Both branch orders are therefore
  reachable, and the second of the two dates falls inside the default
  verification window. This is a measurement on a REBUILT series, not on the
  venue's own 2h bars; the shaping of a bar is not the same thing as the sum of
  the bars that compose it, and `volume` on the rebuilt bars is a true sum while
  `hlc3` is not the venue's own. Stated as such rather than as a native-bar
  measurement.
* `v2stoploss_input` & friends are declared as `input(6.604, ...) / 100`, i.e.
  the INPUT's value is the percentage and the division is applied per bar.
  `source_defaults` therefore carries the percentage (6.604, 2.328, 8.882,
  2.317) and the port divides by 100, so overriding the parameter means the same
  thing it means in the source.
* `v2stoploss_level` / `v2takeprofit_level` / the v3 pair are computed EVERY bar
  at the top of the source, before any `if`, straight off
  `strategy.position_avg_price` (na while flat). The port computes all four
  every bar in that same order and only uses them inside the guarded blocks.
* The four `plot(...)` calls are display-only and place no order.
* `RSILowerLevel1 = 42` etc. are LITERALS in the source, not `input()`s, and
  stay literals here; likewise `len`, `MFIlength`, `length1`, `length2`,
  `mult1`, `mult2`.
* MEASURED with the declared defaults (v1 = true, v2 = v3 = false), on the
  rebuilt-2h frame described above. Over the source's own window
  2022-04-24..2022-05-23 the port books 2 closed round trips and still holds a
  position at the end of the window; over the whole rebuilt series it books 372
  round trips and ends short. NO exit order can end any of them: the v1 block
  contains only the two `strategy.entry` calls, and `strategy.exit` appears
  nowhere else in the source, so every position is ended by the opposite entry
  reversing it. That last part is read off the source, not inferred from the
  ledger. Native 2h data is not in the local history, so `verify_chain.py`
  reports this port `skipped_no_local_data` and no venue-side ledger exists to
  compare against.
* `currency = 'USD'` is not modelled: pine_engine has no exchange rate and keeps
  the account in the venue's quote currency. Relative behaviour is unchanged.
* The md's code block is line-for-line identical to
  sources/SM_4929588c271d03e6.pine, and its seven-row argument table matches the
  seven `input()` defaults (true, false, false, 6.604, 2.328, 8.882, 2.317).
  The only md-vs-code difference is the `direction` argument described above,
  which is absent from BOTH the md and the .pine.
* No `security()` call, no `barstate.isrealtime` branch, no repainting and no
  future-data reference.
* Leverage, margin, liquidation, funding and the venue's contract-step rounding
  of order quantities are not modelled.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMFlawlessVictory_492958(PinePortBase, IStrategy):
    source_id = "SM_4929588c271d03e6"
    source_file = "Flawless-Victory-Strategy.md"
    timeframe = "2h"
    can_short = True
    source_defaults: dict = {
        "v1": True,
        "v2": False,
        "v3": False,
        "v2stoploss": 6.604,
        "v2takeprofit": 2.328,
        "v3stoploss": 8.882,
        "v3takeprofit": 2.317,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100_000.0
    source_reproduce_stops = True
    source_fidelity_notes = [
        "BLOCKER: all three `strategy.entry(\"Sell\", when = ...)` calls omit the "
        "required `direction` argument, so the source is not valid Pine as "
        "written and its short side is undefined. Measured: of the 10,856 "
        "uncommented strategy.entry calls in the 5,283-file sources corpus, "
        "exactly 3 supply no direction (no positional second argument, no named "
        "long=/short=, no v5 direction=), and all 3 are in this source, at "
        "lines 123, 132 and 142. The omission is the SOURCE's own and not an "
        "extraction artifact: the platform that hosts it (fmz.com/strategy/365687, "
        "fetched 2026-09-24) renders the same three direction-less "
        "strategy.entry(\"Sell\", when = ...) calls, and its copy does not resolve "
        "the intended direction either.",
        "The direction is MODELLED as strategy.short, on the evidence of the "
        "source's own identifiers (id 'Sell', alert 'Sell Signal!', the "
        "overbought rsi > 70 guard, and the protective exit bound to the "
        "separate id 'Long'). The alternative reading (strategy.long) would, "
        "with pyramiding=0 and v1 having no exit call, hold one long from the "
        "first signal to the end of the window. No condition depends on the "
        "direction, so the three 'short' arguments can be flipped without any "
        "other change.",
        "MD-vs-CODE: the md prose calls this a '15 minute Bitcoin Long strategy' "
        "and says 'buying one time and one selling one time' -- that points at "
        "a long-only reading, which the code's strategy.entry cannot express as "
        "a close. Recorded; the code is primary and the reading taken is stated "
        "above rather than presented as the source's literal content.",
        "The RSI is written out from the source's own three lines; it agrees "
        "formula-for-formula with ta.pine_rsi, but the source's explicit "
        "`up == 0 -> 0` branch is part of what is reproduced.",
        "The MFI is the source's OWN _rsi(MFIupper, MFIlower), not the batch's "
        "_pine_mfi helper and not ta.mfi: this source states its degenerate "
        "conventions explicitly (MFIlower == 0 -> 100 tested first, then "
        "MFIupper == 0 -> 0) instead of leaving them to the platform. Measured "
        "on a 2h frame REBUILT by resampling the local BTC/USDT:USDT 1h futures "
        "series (25,049 bars, 2021-01-01..2026-09-19; native 2h is not in the "
        "local history): of 25,036 defined windows, MFIlower sums to 0 on 2 "
        "(2023-06-21 16:00, 2024-10-29 18:00) and MFIupper never does, so the "
        "first branch IS exercised -- including inside the default verification "
        "window.",
        "v2stoploss_input & friends are input(6.604, ...)/100, so "
        "source_defaults carries the percentages (6.604 / 2.328 / 8.882 / 2.317) "
        "and the port divides by 100 per bar, as the source does.",
        "v2stoploss_level / v2takeprofit_level / the v3 pair are computed every "
        "bar at the top of the source, off strategy.position_avg_price (na while "
        "flat); the port computes all four every bar in that order.",
        "The four plot() calls are display-only.",
        "RSILowerLevel1 = 42 etc., len, MFIlength, length1, length2, mult1 and "
        "mult2 are literals in the source, not inputs, and stay literals.",
        "Measured with the declared defaults on the rebuilt-2h frame: 2 closed "
        "round trips and a position still open over the source's own window "
        "2022-04-24..2022-05-23; 372 round trips over the whole rebuilt series. "
        "No exit order can end any of them -- the v1 block has no exit call and "
        "strategy.exit appears nowhere else in the source -- so every position "
        "ends by reversal. Native 2h data is absent locally, so verify_chain "
        "reports this port skipped_no_local_data.",
        "currency = 'USD' is not modelled; the engine keeps the account in the "
        "venue's quote currency.",
        "The md's code block is identical to the .pine and its seven-row "
        "argument table matches all seven input() defaults; the only md-vs-code "
        "difference is the missing direction, absent from both.",
        "No security() call, no barstate.isrealtime branch, no repainting and no "
        "future-data reference.",
        "CHAIN: verify_chain --port SM_4929588c271d03e6 returns "
        "'skipped_no_local_data'. The port's period is 2h and the local history "
        "covers only 5m/15m/1h/4h/1d, so no framework-side ledger exists to "
        "compare against and no chain verdict is claimed.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]
        size = len(dataframe)

        # -- RSI -----------------------------------------------------------------
        # len = 14; src = close
        # up   = rma(max(change(src), 0), len)
        # down = rma(-min(change(src), 0), len)
        # rsi  = down == 0 ? 100 : up == 0 ? 0 : 100 - 100 / (1 + up / down)
        change = ta.pine_change(close)
        up = ta.pine_rma(ta.pine_max(change, 0.0), 14).to_numpy(dtype=float)
        down = ta.pine_rma(-ta.pine_min(change, 0.0), 14).to_numpy(dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            rsi = 100.0 - 100.0 / (1.0 + up / down)
        rsi = np.where(down == 0.0, 100.0, np.where(up == 0.0, 0.0, rsi))

        # -- MFI -----------------------------------------------------------------
        # MFIupper = sum(volume * (change(hlc3) <= 0 ? 0 : hlc3), 14)
        # MFIlower = sum(volume * (change(hlc3) >= 0 ? 0 : hlc3), 14)
        # mfi = _rsi(MFIupper, MFIlower)  -- the source's own rsi, tested in order.
        hl3 = ta.pine_source(dataframe, "hlc3")
        hl3_values = hl3.to_numpy(dtype=float)
        volume_values = volume.to_numpy(dtype=float)
        mfi_change = ta.pine_change(hl3)
        # Pine's `cond ? 0 : x` takes x when the condition is na, so the first
        # bar's turnover is counted on BOTH sides -- numpy's False for a NaN
        # comparison gives the same.
        upper_term = np.where((mfi_change <= 0).to_numpy(), 0.0, hl3_values) * volume_values
        lower_term = np.where((mfi_change >= 0).to_numpy(), 0.0, hl3_values) * volume_values
        upper_sum = pd.Series(upper_term, index=dataframe.index)
        lower_sum = pd.Series(lower_term, index=dataframe.index)
        mfi_upper = upper_sum.rolling(14, min_periods=14).sum().to_numpy(dtype=float)
        mfi_lower = lower_sum.rolling(14, min_periods=14).sum().to_numpy(dtype=float)
        with np.errstate(divide="ignore", invalid="ignore"):
            mfi_value = 100.0 - (100.0 / (1.0 + mfi_upper / mfi_lower))
        # `if MFIlower == 0 -> 100` is tested first; then `if MFIupper == 0 -> 0`.
        mfi = np.where(mfi_lower == 0.0, 100.0, np.where(mfi_upper == 0.0, 0.0, mfi_value))

        # -- Bollinger Bands ------------------------------------------------------
        # v1: length1 = 20, mult1 = 1.0   v2: length2 = 17, mult2 = 1.0
        basis1 = ta.pine_sma(close, 20)
        dev1 = 1.0 * ta.pine_stdev(close, 20)
        upper1 = (basis1 + dev1).to_numpy(dtype=float)
        lower1 = (basis1 - dev1).to_numpy(dtype=float)

        basis2 = ta.pine_sma(close, 17)
        dev2 = 1.0 * ta.pine_stdev(close, 17)
        upper2 = (basis2 + dev2).to_numpy(dtype=float)
        lower2 = (basis2 - dev2).to_numpy(dtype=float)

        src1 = close.to_numpy(dtype=float)
        src2 = close.to_numpy(dtype=float)

        # -- Triggers and guards --------------------------------------------------
        # v1
        buy_1 = (src1 < lower1) & (rsi > 42.0)
        sell_1 = (src1 > upper1) & (rsi > 70.0)
        # v2
        buy_2 = (src2 < lower2) & (rsi > 42.0)
        sell_2 = (src2 > upper2) & (rsi > 76.0)
        # v3 (operator precedence: `and` chains left to right, all three required)
        buy_3 = (src1 < lower1) & (mfi < 60.0)
        sell_3 = (src1 > upper1) & (rsi > 65.0) & (mfi > 64.0)

        dataframe["pine_rsi"] = rsi
        dataframe["pine_mfi"] = mfi
        dataframe["pine_upper1"] = upper1
        dataframe["pine_lower1"] = lower1
        dataframe["pine_upper2"] = upper2
        dataframe["pine_lower2"] = lower2
        dataframe["pine_buy_1"] = buy_1
        dataframe["pine_sell_1"] = sell_1
        dataframe["pine_buy_2"] = buy_2
        dataframe["pine_sell_2"] = sell_2
        dataframe["pine_buy_3"] = buy_3
        dataframe["pine_sell_3"] = sell_3
        assert len(dataframe) == size
        return dataframe

    def pine_context(self, dataframe, params):
        size = len(dataframe)
        # Inputs are read through source_parameters(), so they are broadcast per
        # bar and read in pine_script like any other Pine series. The three
        # SL/TP inputs are stored as PERCENTAGES and divided by 100 here, which
        # is where the source's `input(...) / 100` division sits.
        return {
            "buy_1": dataframe["pine_buy_1"].to_numpy(),
            "sell_1": dataframe["pine_sell_1"].to_numpy(),
            "buy_2": dataframe["pine_buy_2"].to_numpy(),
            "sell_2": dataframe["pine_sell_2"].to_numpy(),
            "buy_3": dataframe["pine_buy_3"].to_numpy(),
            "sell_3": dataframe["pine_sell_3"].to_numpy(),
            "v1": np.full(size, bool(params["v1"]), dtype=bool),
            "v2": np.full(size, bool(params["v2"]), dtype=bool),
            "v3": np.full(size, bool(params["v3"]), dtype=bool),
            "v2stoploss": np.full(size, float(params["v2stoploss"]), dtype=float) / 100.0,
            "v2takeprofit": np.full(size, float(params["v2takeprofit"]), dtype=float) / 100.0,
            "v3stoploss": np.full(size, float(params["v3stoploss"]), dtype=float) / 100.0,
            "v3takeprofit": np.full(size, float(params["v3takeprofit"]), dtype=float) / 100.0,
        }

    def pine_script(self, broker, i, ctx):
        # v2stoploss_level = strategy.position_avg_price * (1 - v2stoploss_input)
        # v2takeprofit_level = strategy.position_avg_price * (1 + v2takeprofit_input)
        # v3stoploss_level = strategy.position_avg_price * (1 - v3stoploss_input)
        # v3takeprofit_level = strategy.position_avg_price * (1 + v3takeprofit_input)
        # Computed every bar at the top of the source, before any `if`;
        # strategy.position_avg_price is na while flat.
        average = broker.position_avg_price
        v2_stoploss_level = average * (1 - ctx["v2stoploss"][i])
        v2_takeprofit_level = average * (1 + ctx["v2takeprofit"][i])
        v3_stoploss_level = average * (1 - ctx["v3stoploss"][i])
        v3_takeprofit_level = average * (1 + ctx["v3takeprofit"][i])

        # if v1 == true
        if ctx["v1"][i]:
            # strategy.entry("Long", strategy.long, when = Buy_1, ...)
            broker.entry("Long", "long", when=bool(ctx["buy_1"][i]))
            # strategy.entry("Sell", when = Sell_1, ...) -- NO direction argument
            # in the source; modelled as strategy.short (see the module docstring).
            broker.entry("Sell", "short", when=bool(ctx["sell_1"][i]))

        # if v2 == true
        if ctx["v2"][i]:
            broker.entry("Long", "long", when=bool(ctx["buy_2"][i]))
            broker.entry("Sell", "short", when=bool(ctx["sell_2"][i]))
            # strategy.exit("Stoploss/TP", "Long", stop = v2stoploss_level,
            #               limit = v2takeprofit_level)
            broker.exit(
                "Stoploss/TP", "Long",
                stop=v2_stoploss_level, limit=v2_takeprofit_level,
            )

        # if v3 == true
        if ctx["v3"][i]:
            broker.entry("Long", "long", when=bool(ctx["buy_3"][i]))
            broker.entry("Sell", "short", when=bool(ctx["sell_3"][i]))
            broker.exit(
                "Stoploss/TP", "Long",
                stop=v3_stoploss_level, limit=v3_takeprofit_level,
            )
