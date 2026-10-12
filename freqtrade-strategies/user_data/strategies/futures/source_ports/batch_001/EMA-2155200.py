"""Port of sources/SM_67cc37f743b8a7a7.pine (batch_001/EMA-2155200.md).

Pine v4 (`//@version=4`, bare builtins `ema`, `rsi`, `crossover`, `crossunder`).
Three EMAs define a stacked trend, an RSI supplies the exit, and the two sides
are symmetric:

    ema5  = ema(close, 21)
    ema20 = ema(close, 55)
    ema50 = ema(close, 200)
    rsiValue = rsi(close, 14)                       # source, 14

    emacrossover  = crossover(ema5, ema20)  and ema5 > ema50 and ema20 > ema50 and close > ema50
    emacrossunder = crossunder(ema5, ema20) and ema5 < ema50 and ema20 < ema50 and close < ema50

    doBuy  = crossover(rsiValue, 30)  and rsiValue < 50
    doSell = crossunder(rsiValue, 70) and rsiValue > 50

    strategy.entry("Long",  strategy.long,  100, when=emacrossover)
    strategy.close("Long",  when=doSell)
    strategy.entry("Short", strategy.short, 100, when=emacrossunder)
    strategy.close("Short", when=doBuy)

Both entries pass an EXPLICIT `qty=100`. `strategy()` declares only
title/overlay, so the strategy-wide sizing is Pine's documented default
(`default_qty_type=strategy.fixed`, `default_qty_value=1`) and that default is
what the port reports; the per-call literal 100 is passed through to
`broker.entry`, which is what actually sizes every order. Entry quantity is
therefore price-independent.

The source has NO `input()` call at all: every parameter (21/55/200, 14, 30/70,
the RSI mid line 50) is a plain assignment. `source_defaults` is empty for that
reason, and those numbers stay literals here rather than becoming tunables.

The `/*backtest` header declares `period: 1d`, so `timeframe` is "1d"; its
`basePeriod: 1h` is the FMZ backtester's own filling granularity for those daily
bars, not the strategy's period. Initial capital is not declared in the source,
so Pine's documented default 1000000 applies; commission and pyramiding are not
declared either (0% and 0).

Only `strategy.entry` / `strategy.close` are used -- no stop, limit, profit,
loss or trail call -- so `source_reproduce_stops` is False and each side is
closed only by its own `strategy.close`.

FIDELITY:

* v4 spells `ema` / `rsi` / `crossover` / `crossunder` bare; the v5/v6 namespace
  forms `ta.ema` / `ta.rsi` / `ta.crossover` / `ta.crossunder` are the same
  functions, and every call this source makes is semantically identical across
  those versions, so the port uses `pine_ta`'s implementations directly.
* `rsiMid = 50` is DECLARED BUT NEVER USED: both RSI guards compare against the
  LITERAL 50 (`rsiValue < 50`, `rsiValue > 50`). The literal is kept.
* `doBuy` / `doSell` are not position-aware -- `strategy.close("Short", when=
  doBuy)` is evaluated even while flat or long. Pine's `strategy.close(id)`
  names an entry, and closing an entry that is not open is a no-op; the shared
  engine reproduces that (PINE_SEMANTICS.md section 1.12), so no guard is added.
* `strategy.close` calls are next-open MARKET exits in both the source and the
  engine, so the close side needs no level plumbing.
* The md carries no argument table and no strategy description, so there is no
  md-vs-source discrepancy to record beyond the file name: the md stem
  "EMA-2155200" reads as the 21/55/200 EMAs, which is what the source uses.
* `pine_ema` seeding is the modelled 'first non-na value' choice
  (PINE_SEMANTICS.md section 3.1) and `pine_rsi` inherits the same Wilder
  seeding choice (section 3.3); both are parity risks versus TradingView.
* `plot(...)` calls, the strategy title and `overlay` are display-only.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled; the chain verifier measures the rounding separately.
"""
from __future__ import annotations

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMEma2155200_67cc37(PinePortBase, IStrategy):
    source_id = "SM_67cc37f743b8a7a7"
    source_file = "EMA-2155200.md"
    timeframe = "1d"
    can_short = True
    # The source has no input() call: every length is a plain assignment.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both strategy.entry calls pass an explicit qty=100; strategy() "
        "declares no sizing, so the strategy-wide default reported here is "
        "Pine's fixed/1 and the literal 100 is what actually sizes each order.",
        "The source has NO input() call -- 21/55/200, 14, 30/70 and the RSI mid "
        "line 50 are plain assignments -- so source_defaults is empty and those "
        "numbers stay literals rather than becoming tunables.",
        "`rsiMid = 50` is DECLARED BUT NEVER USED: both RSI guards compare "
        "against the LITERAL 50. The literal is kept.",
        "v4's bare ema/rsi/crossover/crossunder are the same functions as the "
        "v5/v6 ta.* namespace forms, and every call this source makes is "
        "version-identical, so pine_ta's implementations are used directly.",
        "doBuy/doSell are not position-aware; strategy.close(id) names an entry "
        "and closing an entry that is not open is a no-op, which the engine "
        "reproduces (PINE_SEMANTICS.md section 1.12). No guard is added.",
        "No stop/limit/profit/loss/trail call exists, so source_reproduce_stops "
        "is False and each side is closed only by its own strategy.close.",
        "strategy() declares only title/overlay: fixed/1 sizing, 0% commission, "
        "pyramiding 0 and initial capital 1000000 (Pine's documented default).",
        "pine_ema's 'first non-na value' seeding (PINE_SEMANTICS.md section "
        "3.1) and pine_rsi's Wilder seeding (section 3.3) are modelled choices, "
        "parity risks versus TradingView.",
        "plot calls, the title and `overlay` are display-only.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled; the chain verifier measures the rounding separately.",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema5 = ta.pine_ema(close, 21)
        ema20 = ta.pine_ema(close, 55)
        ema50 = ta.pine_ema(close, 200)
        rsi_value = ta.pine_rsi(close, 14)

        dataframe["pine_ema21"] = ema5
        dataframe["pine_ema55"] = ema20
        dataframe["pine_ema200"] = ema50
        dataframe["pine_rsi"] = rsi_value

        # doBuy / doSell (RSI 30/70 crossings, with the literal 50 guards)
        dataframe["pine_do_buy"] = ta.pine_crossover(rsi_value, 30) & (rsi_value < 50)
        dataframe["pine_do_sell"] = ta.pine_crossunder(rsi_value, 70) & (rsi_value > 50)

        # emacrossover / emacrossunder
        dataframe["pine_long_condition"] = (
            ta.pine_crossover(ema5, ema20)
            & (ema5 > ema50)
            & (ema20 > ema50)
            & (close > ema50)
        )
        dataframe["pine_short_condition"] = (
            ta.pine_crossunder(ema5, ema20)
            & (ema5 < ema50)
            & (ema20 < ema50)
            & (close < ema50)
        )
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "do_buy": dataframe["pine_do_buy"].to_numpy(),
            "do_sell": dataframe["pine_do_sell"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, 100, when=longCondition)
        broker.entry("Long", "long", 100, when=bool(ctx["long_condition"][i]))
        # strategy.close("Long", when=closelongCondition)
        broker.close("Long", when=bool(ctx["do_sell"][i]))
        # strategy.entry("Short", strategy.short, 100, when=shortCondition)
        broker.entry("Short", "short", 100, when=bool(ctx["short_condition"][i]))
        # strategy.close("Short", when=closeshortCondition)
        broker.close("Short", when=bool(ctx["do_buy"][i]))
