"""Port of sources/SM_33e741bbe4c254e6.pine (batch_001/CM多重EMA金叉死叉策略CM-Multiple-EMA-Crossover-Strategy.md).

Pine v4. Four EMAs and a 21/55 crossover:

    ema8  = ema(close, 8)
    ema13 = ema(close, 13)
    ema21 = ema(close, 21)
    ema55 = ema(close, 55)

    emacrossover = crossover(ema21, ema55) and ema8 and ema13 > ema55
    emacrossunder = crossunder(ema21, ema55) and ema8 and ema13 < ema55

    strategy.entry("Long",  strategy.long,  qty=na, when=longCondition)
    strategy.close("Close Long",                   when=closelongCondition)
    strategy.entry("Short", strategy.short, qty=na, when=shortCondition)
    strategy.close("Close Short",                  when=closeshortCondition)

so the four calls are made in that order on every bar, with
longCondition = closelongCondition's opposite = emacrossover and
shortCondition = closeshortCondition's opposite = emacrossunder (the source
assigns them that way; they are not negations of each other in the code).

Three source properties are load-bearing and are reproduced literally rather
than "cleaned up":

* `and ema8` uses the EMA *value* as a boolean. Pine treats a float as true when
  it is neither na nor zero, so this conjunct is a live condition only during an
  EMA's warmup. It is NOT rewritten into a price comparison (see
  PINE_SEMANTICS.md §1.16 for the mirror-image trap on bools used as numbers).
* `strategy.close("Close Long")` / `strategy.close("Close Short")` name ids that
  no `strategy.entry` ever used. Pine's `strategy.close(id)` is keyed on the
  ENTRY id (the engine's `_close_entries` matches `from_entry`), so neither call
  closes anything: the two close conditions are inert and the position only
  changes by an opposite entry reversing it.
* `qty=na` means "use `strategy()`'s default quantity", which is Pine's default
  `fixed` / 1 because `strategy()` here declares no sizing arguments at all.

`strategy(title="CM EMA Trend Cross STRAT", shorttitle="CM EMA Strat",
overlay=true)` declares only display arguments, so the defaults are `fixed` / 1
unit, commission 0%, `pyramiding = 0`, `initial_capital = 1000000`,
`process_orders_on_close = false`.

The `/*backtest` header declares `period: 6h` on Futures_Binance BTC_USDT, so
`timeframe` is "6h"; its `basePeriod: 15m` is the FMZ backtester's own bar grid.

FIDELITY:

* The md's Strategy Logic says the long trigger is "8-day, 13-day, 21-day EMAs
  ALL cross above the 55-day EMA" and that the position is closed "on reverse
  crossover". The source does neither: only ema21 is tested for a crossover (and
  `ema8` only for truthiness), and both `strategy.close` calls name entry ids
  that do not exist. The source is authoritative; both prose divergences are
  recorded here and the source's logic is NOT altered to match the md.
* The md describes the periods as days; the EMAs are bar-based and the source
  runs on 6h bars, so "8/13/21/55" count 6h bars, not days.
* `ema` seeding is a modelled choice (first non-na seed), see
  PINE_SEMANTICS.md §3.1.
* No stop/limit/trail exit exists, so `source_reproduce_stops` is False and a
  position still open at the end of the window stays open.
* `plot(...)` / `shorttitle` / `overlay` are display-only and are not
  reproduced.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled (§二.4, §1.6).
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


class SMCMEmaTrendCross_33e741(PinePortBase, IStrategy):
    source_id = "SM_33e741bbe4c254e6"
    source_file = "CM多重EMA金叉死叉策略CM-Multiple-EMA-Crossover-Strategy.md"
    timeframe = "6h"
    can_short = True
    # No input() in the source: the four EMA lengths are literals.
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "`and ema8` uses a float as a boolean; Pine is true for non-na, "
        "non-zero, so the conjunct only bites during EMA warmup. Left as a "
        "truthiness test, not rewritten into a price comparison (§1.16 is the "
        "mirror case: a bool used in a numeric context).",
        "strategy.close(\"Close Long\") / strategy.close(\"Close Short\") name "
        "entry ids that no strategy.entry used, so under Pine's per-entry "
        "close semantics both are no-ops; the position only turns on an "
        "opposite entry reversing it. Reproduced literally -- the close calls "
        "are made, and the engine (like Pine) matches them against no open "
        "entry.",
        "md vs source: the md says all of ema8/ema13/ema21 must cross the "
        "55 EMA and that the position is closed on the reverse cross. The "
        "source tests only ema21 for a crossover and its close ids are inert. "
        "The source wins; recorded, not applied.",
        "md vs source: the md calls the periods 'days', but the source runs on "
        "6h bars and the EMAs are bar counts.",
        "qty=na means the strategy() default quantity: fixed / 1 unit.",
        "ema seeding is a modelled choice (first non-na seed), §3.1.",
        "No stop/limit/trail exit exists, so source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "plot/shorttitle/overlay are display-only, not reproduced.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled (§二.4, §1.6).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        ema8 = ta.pine_ema(close, 8)
        ema13 = ta.pine_ema(close, 13)
        ema21 = ta.pine_ema(close, 21)
        ema55 = ta.pine_ema(close, 55)
        # `and ema8` -- Pine truthiness of a float: na is false, 0.0 is false.
        ema8_true = ema8.notna() & (ema8 != 0.0)
        emacrossover = ta.pine_crossover(ema21, ema55) & ema8_true & (ema13 > ema55)
        emacrossunder = ta.pine_crossunder(ema21, ema55) & ema8_true & (ema13 < ema55)
        dataframe["pine_ema8"] = ema8
        dataframe["pine_ema13"] = ema13
        dataframe["pine_ema21"] = ema21
        dataframe["pine_ema55"] = ema55
        dataframe["pine_long_condition"] = emacrossover
        dataframe["pine_short_condition"] = emacrossunder
        return dataframe

    def pine_context(self, dataframe, params):
        long_condition = dataframe["pine_long_condition"].to_numpy()
        return {
            "long_condition": long_condition,
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            # longCondition = emacrossover        closelongCondition = emacrossunder
            # shortCondition = emacrossunder      closeshortCondition = emacrossover
            "close_long_condition": long_condition,
            "close_short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Long", strategy.long, qty=na, when=longCondition)
        if ctx["long_condition"][i]:
            broker.entry("Long", "long")
        # strategy.close("Close Long", when=closelongCondition)
        broker.close("Close Long", when=ctx["close_long_condition"][i])
        # strategy.entry("Short", strategy.short, qty=na, when=shortCondition)
        if ctx["short_condition"][i]:
            broker.entry("Short", "short")
        # strategy.close("Close Short", when=closeshortCondition)
        broker.close("Close Short", when=ctx["close_short_condition"][i])
