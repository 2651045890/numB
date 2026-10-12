"""Port of sources/SM_25f0decd08bdf640.pine
(batch_001/Hull移动平均的趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy.md).

Pine v3, Noro's "HullMA str". A Hull moving average of period `n` decides the
side, and a self-referencing `lot` sizes the entry off `strategy.equity`:

    n2ma = 2*wma(close, round(n/2))
    nma  = wma(close, n)
    diff = n2ma - nma
    sqn  = round(sqrt(n))
    n2ma1= 2*wma(close[1], round(n/2))
    nma1 = wma(close[1], n)
    diff1= n2ma1 - nma1
    sqn1 = round(sqrt(n))
    n1   = wma(diff,  sqn)
    n2   = wma(diff1, sqn)
    c    = n1 > n2 ? green : red
    ma   = plot(n1, color = c)

    lot = 0.0
    lot := strategy.position_size != strategy.position_size[1]
           ? strategy.equity / close * capital / 100
           : lot[1]
    if n1 > n2
        strategy.entry("Long",  strategy.long,  needlong  == false ? 0 : lot)
    if n1 < n2
        strategy.entry("Short", strategy.short, needshort == false ? 0 : lot)
    if true
        strategy.close_all()

`n2` is `n1` lagged one bar by construction (`diff1` is `close[1]` run through
the same two WMAs), so `n1 > n2` / `n1 < n2` are "Hull curve rising / falling".

`strategy(title=..., shorttitle=..., overlay=true, default_qty_type=
strategy.percent_of_equity, default_qty_value=100, pyramiding=0)` names no other
order property, so Pine's documented defaults apply for the rest: initial
capital 1000000, commission 0%, `process_orders_on_close = false`.

The `/*backtest` header declares `period: 4h` on Futures_Binance BTC_USDT, so
`timeframe` is "4h"; `basePeriod: 15m` is the FMZ backtester's own filling
granularity for those 4h bars, not the strategy's period.

DEAD CODE, KEPT: `sqn1` is assigned and never read (measured: its name occurs
only on its own assignment line). It is computed and exposed as a column.
`fromyear` / `toyear` / `frommonth` / `tomonth` / `fromday` / `today` are
declared inputs that are never read (measured: each name occurs only on its own
`input()` line); they stay in `source_defaults` so the declared defaults are
complete, and they gate nothing.

FIDELITY: see source_fidelity_notes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMHullMovingAverageTrendFollowing_25f0de(PinePortBase, IStrategy):
    source_id = "SM_25f0decd08bdf640"
    source_file = "Hull移动平均的趋势跟踪策略Hull-Moving-Average-Trend-Following-Strategy.md"
    timeframe = "4h"
    can_short = True
    source_defaults: dict = {
        "needlong": True,
        "needshort": True,
        "capital": 100,
        "n": 16,
        "fromyear": 1900,
        "toyear": 2100,
        "frommonth": 1,
        "tomonth": 12,
        "fromday": 1,
        "today": 31,
    }
    source_qty_type = "percent_of_equity"
    source_qty_value = 100.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`timeframe` is taken from the source's `/*backtest` header (`period: "
        "4h`, Futures_Binance BTC_USDT). The header's `basePeriod: 15m` is the "
        "FMZ backtester's own fill granularity for those 4h bars, not the "
        "strategy's period.",
        "`strategy(...)` declares only title/shorttitle/overlay/"
        "default_qty_type/default_qty_value/pyramiding, so the port carries "
        "Pine's documented defaults for the rest: initial capital 1000000, "
        "commission 0%, `process_orders_on_close = false`.",
        "`if true` issues `strategy.close_all()` on EVERY bar, not only on a "
        "signal bar. This is the source's literal text, and it is what makes "
        "the entry and the close_all share a bar.",
        "WITHIN-BAR FILL ORDER IS A MODELLED RULE, NOT A PUBLISHED ONE. The "
        "entry and the unconditional close_all are placed on the same bar, and "
        "the engine fills a bar's pending orders in creation (source) order, so "
        "at the next bar's open the entry fills and the close_all behind it "
        "closes it at the same price. PINE_SEMANTICS.md 1.13/1.14 records this "
        "as a choice: TradingView does not document the emulator's same-bar "
        "tie-break, and the other defensible model -- a close_all captures what "
        "was open when it was CREATED, so a call issued while flat creates "
        "nothing -- would let the position survive and is a materially "
        "different strategy. The source cannot settle it.",
        "CONSEQUENCE, MEASURED (local BTC/USDT:USDT 4h, 14815 bars): every "
        "signal bar becomes a zero-length round trip. 14796 entry orders are "
        "placed (7654 Long + 7142 Short), 14795 fills are booked, and all 14795 "
        "have `open_date == close_date` on the same bar with `profit_abs == "
        "0.0` (commission is 0%). The engine's `pine_position` is non-zero on 0 "
        "of the bars.",
        "CONSEQUENCE FOR `lot`, MEASURED by instrumenting the port over the same "
        "14815 bars: because the position is flat at every bar's evaluation, "
        "`strategy.position_size != strategy.position_size[1]` is false on "
        "every bar after the first (and na on the first), so `lot` keeps the na "
        "it inherits from `lot[1]` and never takes the `strategy.equity / close "
        "* capital / 100` branch (`lot` measured na on all 14815 bars). A Pine "
        "entry whose `qty` is na uses the strategy's default order size, so "
        "entries are sized `percent_of_equity` 100 and `capital` (default 100) "
        "never enters the size: the engine sized the first fill at 140.014842 "
        "contracts at 7142.1, i.e. exactly 1000000 / 7142.1. `lot` is still "
        "computed bar by bar, exactly as the source computes it, and the "
        "equity/close branch is still written out.",
        "`lot[1]` on the first bar is na: Pine's series history begins at bar 0, "
        "so the `lot = 0.0` declaration above the `:=` is never what `lot[1]` "
        "reads -- it is overridden in the same bar. This is why the source's "
        "carry cannot self-start, and it is modelled as na rather than 0.",
        "`n2` is `n1` one bar back by construction (`diff1` is the SAME two WMAs "
        "applied to `close[1]`, and a WMA's window is a fixed set of weights). "
        "MEASURED on the local 4h series: on all 14796 bars where both are "
        "defined, `n2` equals `n1[1]` bitwise (max absolute difference 0.0), "
        "and `n2` is na on exactly the bars where `n1[1]` is na. The port "
        "computes both expressions separately, as the source writes them, "
        "rather than substituting the shift.",
        "`sqn1 = round(sqrt(n))` is assigned and never read (measured: the name "
        "occurs only on its own line). It is computed and exposed as a column.",
        "md vs source, PROSE, recorded not followed: the md's Strategy "
        "Description presents this as a trend-following system that goes long "
        "while the Hull curve rises and short while it falls, describes the "
        "Hull construction (n/2, n, then the sqrt-smoothed difference) "
        "correctly, and never mentions the unconditional `strategy.close_all()` "
        "at lines 48-49 of the source. That call is in the code and changes "
        "what the strategy does: it places a close on every bar, so nothing is "
        "ever HELD across bars. The code is the authority; a reader who took "
        "the prose for the specification would be porting a different strategy. "
        "The prose also never mentions `capital` or the self-referencing `lot`.",
        "md vs source, recorded not followed: the md's argument table renders "
        "`v_input_7` (From Month) and `v_input_9` (From day) as `true`, where "
        "the source declares `input(01, ...)`. That is the exporter's rendering "
        "of the integer 1 (the same artefact the batch's other argument tables "
        "show for `1.`). The port uses the source's 1. Neither input is read by "
        "the source, so the disagreement changes no behaviour -- recorded "
        "because the two texts disagree.",
        "`fromyear` / `toyear` / `frommonth` / `tomonth` / `fromday` / `today` "
        "are declared inputs that are never read (measured: each name occurs "
        "only on its own `input()` line). They are kept in `source_defaults` "
        "and gate nothing.",
        "`needlong == false ? 0 : lot` and `needshort == false ? 0 : lot` are "
        "the only places the two bool inputs are read, and both compare a bool "
        "against `false` -- not against 0/1 in a numeric context, so the "
        "PINE_SEMANTICS.md 1.16 trap (bool-as-number silently inverting) does "
        "not apply here. A false switch makes the order quantity exactly 0, "
        "which the engine treats as an order that can never fill.",
        "`round()` is Pine's half-away-from-zero rounding, not numpy's "
        "banker's rounding: `pine_ta.pine_round` is used for both "
        "`round(n/2)` and `round(sqrt(n))`. With the default n = 16 it makes no "
        "difference (8 and 4 either way); it is used because Pine's `round` is "
        "documented as half away from zero and an odd `n` would expose the "
        "difference.",
        "`wma` is `pine_ta.pine_wma` (weights 1..length, newest heaviest), and "
        "`wma(close[1], L)` is computed on the shifted series rather than as a "
        "shift of the WMA -- algebraically the same window, and transcribed as "
        "the source writes it.",
        "na handling: `wma` returns na until its window is full and na anywhere "
        "inside a window propagates (PINE_SEMANTICS.md 3.2). MEASURED with n = "
        "16 (sqn = 4): `n1` is na on bars 0..17 and `n2` on bars 0..18, on the "
        "local 4h BTC series and on the validate_pine synthetic frame alike; "
        "the first `n1 > n2` fires on bar 19 and the first `n1 < n2` on bar 23, "
        "so no signal can fire during warmup (an na comparison is a false "
        "condition in Pine and in this port).",
        "`c = n1 > n2 ? green : red` and `ma = plot(n1, color = c)` are a plot "
        "colour and a plot handle: display only, not reproduced.",
        "There is no `strategy.exit` / stop / limit / trail anywhere in the "
        "source -- the only exit is the unconditional `close_all` -- so "
        "`source_reproduce_stops` is False.",
        "CHAIN VERDICT, MEASURED: on BTC/USDT:USDT 20240101-20250101 (4h) the "
        "chain verifier reports `mismatch_framework_veto` -- engine 2177 "
        "trades against the framework's 1, with 1814 stake vetoes. Each "
        "zero-length round trip asks the framework for `percent_of_equity` 100 "
        "of a 1,000,000 initial capital, and the framework caps the stake near "
        "433,639 on that pair, so the SOURCE's own order size is what the "
        "framework refuses (SOURCE_STAKE_VETO required=1000000.00000000 "
        "max_stake=433639.35283999995). The two sides are therefore not "
        "comparable on this window at all; the veto is a framework limit, not "
        "a statement about the port. `held_engine` and `held_freqtrade` are "
        "both false, and the 1 close_date, 1 price-rounding, 1 price-tick and "
        "1 pnl-step mismatch are the residue of the counts differing.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md 2.4 / 1.6), so the "
        "framework and the engine can differ by a rounded quantity. That is "
        "measured separately by the chain verifier.",
        "`currency` and `slippage` are not declared, and neither is modelled: "
        "Pine's default slippage is 0.",
    ]

    def pine_indicators(self, dataframe: pd.DataFrame, params: dict) -> pd.DataFrame:
        close = dataframe["close"]
        n = int(params["n"])
        # Pine v3 `/` on integers is float division, and `round()` rounds half
        # away from zero; wma takes the resulting integer period.
        half = int(ta.pine_round(n / 2.0))
        sqn = int(ta.pine_round(np.sqrt(float(n))))

        n2ma = 2.0 * ta.pine_wma(close, half)
        nma = ta.pine_wma(close, n)
        diff = n2ma - nma
        # sqn1 = round(sqrt(n)) -- assigned by the source and never read. It is
        # computed here and exposed so the dead variable is not dropped.
        sqn1 = int(ta.pine_round(np.sqrt(float(n))))

        previous_close = close.shift(1)
        n2ma1 = 2.0 * ta.pine_wma(previous_close, half)
        nma1 = ta.pine_wma(previous_close, n)
        diff1 = n2ma1 - nma1

        n1 = ta.pine_wma(diff, sqn)
        n2 = ta.pine_wma(diff1, sqn)

        # c = n1 > n2 ? green : red  -- a plot colour.
        # ma = plot(n1, color = c)   -- a plot handle. Display only, not reproduced.

        dataframe["pine_n2ma"] = n2ma
        dataframe["pine_nma"] = nma
        dataframe["pine_diff"] = diff
        dataframe["pine_sqn"] = float(sqn)
        dataframe["pine_sqn1"] = float(sqn1)
        dataframe["pine_n2ma1"] = n2ma1
        dataframe["pine_nma1"] = nma1
        dataframe["pine_diff1"] = diff1
        dataframe["pine_n1"] = n1
        dataframe["pine_n2"] = n2
        # na comparisons are false, as Pine's are.
        dataframe["pine_long_signal"] = n1 > n2
        dataframe["pine_short_signal"] = n1 < n2
        return dataframe

    def pine_context(self, dataframe: pd.DataFrame, params: dict) -> dict:
        return {
            "close": dataframe["close"].to_numpy(dtype=float),
            "long_signal": dataframe["pine_long_signal"].to_numpy(dtype=bool),
            "short_signal": dataframe["pine_short_signal"].to_numpy(dtype=bool),
            "capital": float(params["capital"]),
            "needlong": bool(params["needlong"]),
            "needshort": bool(params["needshort"]),
        }

    def pine_script(self, broker, i: int, ctx: dict) -> None:
        # --- lot = 0.0 / lot := ... : Pine's self-referencing position carry.
        # On the first bar `lot[1]` and `strategy.position_size[1]` are na, so
        # the carry is seeded with na, not with the 0.0 declared above it.
        if i == 0:
            self._hull_prev_lot = np.nan
            self._hull_prev_position = np.nan

        position = float(broker.position_size)
        previous_position = self._hull_prev_position
        # `strategy.position_size != strategy.position_size[1]` is na when the
        # previous value is na, and na is a false condition.
        if np.isnan(previous_position) or position == previous_position:
            lot = self._hull_prev_lot                      # `: lot[1]`
        else:
            lot = broker.equity / ctx["close"][i] * ctx["capital"] / 100.0
        self._hull_prev_lot = lot
        self._hull_prev_position = position

        # `needlong == false ? 0 : lot` compares a bool against `false`, not
        # against 0/1 in a numeric context (PINE_SEMANTICS.md 1.16).
        long_qty = lot if ctx["needlong"] else 0.0
        short_qty = lot if ctx["needshort"] else 0.0

        # if n1 > n2
        #     strategy.entry("Long", strategy.long, needlong == false ? 0 : lot)
        if ctx["long_signal"][i]:
            broker.entry("Long", "long", qty=long_qty)
        # if n1 < n2
        #     strategy.entry("Short", strategy.short, needshort == false ? 0 : lot)
        if ctx["short_signal"][i]:
            broker.entry("Short", "short", qty=short_qty)
        # if true
        #     strategy.close_all()
        broker.close_all()
